.. _build_breaking_change:

Build breaking changes in Linux
===============================

Key change
----------

Due to compatibility issues detected with Ubuntu 22.04, the use of `dotnetcore2` has been removed.
The embedded version of .NET associated to `dotnetcore2` is old and has **incompatibilities** with the
version of `openssl` that is installed by default in Ubuntu 22.04. This caused errors and conflicts with
critical dependencies in the environment.

Workaround considered
---------------------

A temporary workaround was considered, which involved manually installing an older version of the
`libssl1.1` library. While this allowed the use of `dotnetcore2`, it is **not recommended** as a
long-term solution for the following reasons:

- **Security risks**: Installing an older version of `libssl` introduces vulnerabilities, as it may
lack the latest security updates provided in the newer versions.
- **System instability**: Manually forcing an older version of `libssl` can lead to dependency
conflicts with other software packages that rely on newer versions of this library, potentially
causing further compatibility issues in the system.
- **Maintenance overhead**: Relying on deprecated or unsupported libraries increases the
complexity of future upgrades and system maintenance, making the environment harder to manage in the
long term.

Impact
------

Users need to install `.NET` themselves. The installation process can be done following the official
Microsoft documentation for `.NET` on Linux to ensure proper setup and compatibility. See
`Register Microsoft package repository <https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu#register-the-microsoft-package-repository>`_
and `Install .NET <https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu#install-net>`_.

.. note:: Ubuntu 22.04 and later versions
    Starting with Ubuntu 22.04, `.NET` is available in the official Ubuntu repository.
    If you want to use the Microsoft package to install `.NET`, you can use the following
    approach to *"demote"* the Ubuntu packages so that the Microsoft packages take precedence.

    1. Ensure the removal of any existing `.NET` installation. In Ubuntu, this can be done with
    the following command:

    .. code::

        sudo apt remove dotnet* aspnetcore* netstandard*

    2. Create a preference file in `/etc/apt/preferences.d`, for example `microsoft-dotnet.pref`,
    with the following content:

    .. code::

        Package: dotnet* aspnet* netstandard*
        Pin: origin "archive.ubuntu.com"
        Pin-Priority: -10

        Package: dotnet* aspnet* netstandard*
        Pin: origin "security.ubuntu.com"
        Pin-Priority: -10

    3. Perform an update and install of the version you want, for example .NET 6.0 or 8.0

    .. code::

        sudo apt update && sudo apt install -y dotnet-sdk-6.0
