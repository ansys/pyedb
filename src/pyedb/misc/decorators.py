import functools
import warnings


def deprecated_property(func):
    """
    This decorator marks a property as deprecated.
    It will emit a warning when the property is accessed.
    """

    def wrapper(*args, **kwargs):
        warnings.warn(f"Access to deprecated property {func.__name__}.", category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return wrapper


def deprecate_argument_name(argument_map):
    """Decorator to deprecate certain argument names in favor of new ones."""

    def decorator(func):
        """Decorator that wraps the function to handle deprecated arguments."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function that checks for deprecated arguments."""
            func_name = func.__name__
            for old_arg, new_arg in argument_map.items():
                if old_arg in kwargs:
                    warnings.warn(
                        f"Argument `{old_arg}` is deprecated for method `{func_name}`; use `{new_arg}` instead.",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    # NOTE: Use old argument if new argument is not provided
                    if new_arg not in kwargs:
                        kwargs[new_arg] = kwargs.pop(old_arg)
                    else:
                        kwargs.pop(old_arg)
            return func(*args, **kwargs)

        return wrapper

    return decorator
