Usage
=====

CLI
***

The cli (ts-colab) provides a series of sub-commands to interact with
Testspace. Those sub-commands leverage the API described below.

.. code-block:: console

    (testspace)⚡ ⇒  ts-colab --help
    Usage: ts-colab [OPTIONS] COMMAND [ARGS]...

      Console script for testspace_colab.

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

    (testspace)⚡ ⇒  ts-colab client --help

    Usage: testspace [--version] [--help] <command> [<args>]

    Commands:
      config        Get and set default global options.
      push          Push existing result file(s) to a Space. (default)

    See 'testspace help <command>' to read about a specific command.

    For more information about Testspace, visit www.testspace.com.

Examples
--------

Configuration
.............

.. code-block:: console

    (testspace)⚡ ⇒  ts-colab client config url "72e7a247e02b9d4d521916fe81a708cfa824dcd3@lbrack.testspace.com/samples/main"
     domain: https://********@lbrack.testspace.com
     project: samples
     space: main
    (testspace)⚡ ⇒  ts-colab client config
     domain: https://********@lbrack.testspace.com
     project: samples
     space: main


Push
....

.. code-block:: console

    (testspace)⚡ ⇒  ts-colab client push sample.xml
    Aggregating content...
    Uploading to Testspace (https://lbrack.testspace.com/projects/samples/spaces/main)...
      https://lbrack.testspace.com/spaces/133471/result_sets/123753


API
***

There are three sub-modules under :py:mod:`testspace_colab`:

    * :py:mod:`testspace_colab.lib` which provides the
      :py:class:`API <testspace_colab.lib.API>` class
    * :py:mod:`testspace_colab.client` providing the
      :py:class:`Binary <testspace_colab.client.Binary>` to invoke
      the native client.
    * :py:mod:`testspace_colab.cli` providing the aformentioned CLI
      implementation

To use testspace-colab in a project::

    import testspace_colab
