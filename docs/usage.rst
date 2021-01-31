Usage
=====

CLI
***

The cli (ts-utils) provides a series of sub-commands to interact with
Testspace. Those sub-commands leverage the API described below.

.. code-block:: console

    (testspace)⚡ ⇒  ts-utils --help
    Usage: ts-utils [OPTIONS] COMMAND [ARGS]...

      Console script for testspace_utils.

    Options:
      --help  Show this message and exit.

    Commands:
      client  Runs the client with the specified parameters

The client sub-command provide direct access to the Testspace client executables
which are embedded in the distribution (OSX, Linux and Windows). The proper binary
is resolved at runtime based on the operating system.

This sub-command may be called with the same command line argument as the native
command line .e.g.

.. code-block:: console

    (testspace)⚡ ⇒  ts-utils client --help

    Usage: testspace [--version] [--help] <command> [<args>]

    Commands:
      config        Get and set default global options.
      push          Push existing result file(s) to a Space. (default)

    See 'testspace help <command>' to read about a specific command.

    For more information about Testspace, visit www.testspace.com.

API
***

There are three sub-modules under :py:mod:`testspace_utils`:

    * :py:mod:`testspace_utils.lib` which provides the
      :py:class:`API <testspace_utils.lib.API>` class
    * :py:mod:`testspace_utils.client` providing the
      :py:class:`Binary <testspace_utils.client.Binary>` to invoke
      the native client.
    * :py:mod:`testspace_utils.cli` providing the aformentioned CLI
      implementation

.. todo:: To be documented when we have something meaningful.

To use testspace-utils in a project::

    import testspace_utils
