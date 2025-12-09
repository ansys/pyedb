.. _ref_security_consideration:

Security considerations
=======================

This section provides information on security considerations for the use
of pyedb. It is important to understand the capabilities which pyedb
provides, especially when using it to build applications or scripts that
accept untrusted input.

If a function displays a warning that redirects to this page, it indicates
that the function may expose security risks when used improperly.
In such cases, it is essential to pay close attention to:

- **Function arguments**: Ensure that arguments passed to the function are
  properly validated and do not contain untrusted content such as arbitrary
  file paths, shell commands, or serialized data.
- **Environment variables**: Be cautious of environment variables that can
  influence the behavior of the function, particularly if they are user-defined
  or inherited from an untrusted execution context.
- **Global settings (`settings`)**: Pyedb settings control various aspects of
  runtime behavior such as AEDT features, use of LSF cluster or remote server
  connections. Review these settings to avoid unexpected side effects or security
  vulnerabilities.

Always validate external input, avoid executing arbitrary commands or code,
and follow the principle of least privilege when developing with pyedb.
