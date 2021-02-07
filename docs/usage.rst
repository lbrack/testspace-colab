Usage
=====

There are two types of usage this point. The CLI (ts-colab) enables user to
use the test space API from the command line to visualize data or capture
it in file as json.

The API, which is used by the CLI, provides a programmatic access to a
**Testspace** server

Environment Variables
*********************

You can set the following environment variables

    * *TS_COLAB_DEBUG* Turns debugging ON but setting it to ``true``
    * *TS_COLAB_CONFIG_DIR* path to an alternate config file

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

Note that the configuration file is normally location under ``~/,config/testspace/config``.
This will be file used by default. It is possible to change the file location by point the
``TS_COLAB_CONFIG_DIR`` environment variable to a valid testspace config file (mostly use for
testing)

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

Get
...

This command performs get request that are delegated to the
`testspace-python <https://github.com/s2technologies/testspace-python>`_ library.

for instance, to access the following API

    .. code-block::

        testspace.get_result(result, project=None, space=None)

You would call

    .. code-block:: console

        (testspace)⚡ ⇒  ts-colab get result test_data project=samples space=main
        URL=https://lbrack.testspace.com
        ID     | NAME      | COMPLETE | BUILD_STATUS | SUITE_COUNTS | CASE_COUNTS  | ANNOTATION_COUNTS | FAILURE_COUNTS     | DURATION | SESSION_DURATION |
        123753 | test_data | True     | None         | [6, 1, 0]    | [9, 1, 2, 0] | [1, 0, 1]         | [1, 0, 0, 0, 0, 1] | 0.0      | 0.0              |

Where:

    - ``test_data`` is the name of the result (positional)
    - ``project`` is optional (because of the *=None*)
    - ``space`` is also optional

Note that the following syntax produces the same outcome

    .. code-block:: console

        (testspace)⚡ ⇒  ts-colab get result result=test_data project=samples space=main
        (testspace)⚡ ⇒  ts-colab get result test_data samples main
        (testspace)⚡ ⇒  ts-colab get result test_data space=main #use the default project

It is possible to change the output from ``tabular`` to ``yaml`` or ``json`` using the
``--format`` option. It is also possible to store the JSON output to a file.

To obtain a complete report for a given result, you can use the built-in method

    .. code-block:: console

        (testspace)⚡ ⇒  ts-colab get result_details test_data -o dump.json -f json
        URL=https://lbrack.testspace.com
        [suite] tmp.test_suite_1
            [case] test_case_1
        [suite] tmp.test_suite_1 [C1] HTTP-200
          [suite] tmp.test_suite_1.TestSuiteC1
            [case] test_case_2
            [case] test_case_3
        ...
        [suite] tmp.pyfoldler_1.test_suite_3.TestSuiteC3 [C2] HTTP-200
        {'annotation_counts': [1, 0, 1],
         'build_status': None,
         ...
         'updated_at': '2021-02-04T01:22:36.000+01:00',
         'user_id': 44}
        saving response as json to /home/laurent/github/laurent/testspace-colab/dump.json Done!


This will not only fetch the result meta-data but also the complete report
consisting of suite and test case details and annotation.

.. _elk_cli:

ELK
...

For controlling ELK programmatically, check :ref:`ELK API <elk_api>`

The `Elastic Stack <https://elk-docker.readthedocs.io>`_ used for testing can be controlled
from the command line using the ``ts-colab elk`` sub commands as illustrated below

    .. code-block:: console

        (testspace)⚡ ⇒  ts-colab elk start
        starting ... be patient
        ELK Container started ID=56b66568e8a092ae794213cfde010031a4d4f5c57bb71a6736941038556bbef7

Once started, you can view the container

    .. code-block:: console

        (testspace)⚡ ⇒  docker ps
        CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS              PORTS                                                                                        NAMES
        56b66568e8a0   sebp/elk:7.10.0   "/usr/local/bin/star…"   50 minutes ago   Up About a minute   0.0.0.0:5044->5044/tcp, 0.0.0.0:5601->5601/tcp, 9300/tcp, 0.0.0.0:9200->9200/tcp, 9600/tcp   elk-testspace-colab

When running you can check the status

    .. code-block:: console

        (testspace)⚡ ⇒  ts-colab elk info
        getting elasticsearch info
        ...
        version:
          build_date: '2020-11-09T21:30:33.964949Z'
          build_flavor: default
          build_hash: 51e9d6f22758d0374a0f3f5c6e8f3a7997850f96
          build_snapshot: false
          build_type: tar
          lucene_version: 8.7.0
          minimum_index_compatibility_version: 6.0.0-beta1
          minimum_wire_compatibility_version: 6.8.0
          number: 7.10.0
        Done

        (testspace)⚡ ⇒  ts-colab elk health
        getting cluster health
        active_primary_shards: 6
        relocating_shards: 0
        ...
        status: green
        task_max_waiting_in_queue_millis: 0
        timed_out: false
        unassigned_shards: 0

        Done
        (testspace)⚡ ⇒  ts-colab elk stop
        stopping ... be patient
        ELK stopped

Note that when stopped, the container is not being remove. This has to be done
manually.

    .. code-block:: console

        (testspace)⚡ ⇒  docker ps -a 
        CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS                     PORTS     NAMES
        56b66568e8a0   sebp/elk:7.10.0   "/usr/local/bin/star…"   53 minutes ago   Exited (0) 4 seconds ago             elk-testspace-colab

        (testspace)⚡ ⇒  docker rm elk-testspace-colab
        elk-testspace-colab





API
***

There are several sub-modules under :py:mod:`testspace_colab`:

    * :py:mod:`testspace_colab.lib` which provides the
      :py:class:`API <testspace_colab.lib.API>` class ro interface
      with testspace
    * :py:mod:`testspace_colab.client` providing the
      :py:class:`Binary <testspace_colab.client.Binary>` to invoke
      the native client.
    * :py:mod:`testspace_colab.cli` providing the aformentioned CLI
      implementation
    * :py:mod:`testspace_colab.elk` which provides the
      :py:class:`ELK <testspace_colab.elk.ELK>` class to control
      and access an ELK stack running on Docker.

To use testspace-colab in a project::

    import testspace_colab

.. _elk_api:

ELK
---

For controlling ELK from the command line, check the :ref:`elk cli <elk_cli>`

This project contains a facility to start ELK a.k.a. as ElasticSearch, Logstash, Kibana
locally for development purposes via the :class:`testspace_colab.elk.ELK` class.

The usage is pretty simple and is illustrated below

.. code-block:: console

    from testspace_colab.elk import ELK
    elk = ELK()
    elk.available
    Out[4]: False
    elk.start()
    Out[5]: <Container: 41061dd5a2>
    elk.available
    Out[6]: True
    elk.elastic_search.info()
    Out[7]:
    {'name': 'elk',
     'cluster_name': 'elasticsearch',
     'cluster_uuid': 'ckRg9onsSqyU13AdGPkOAg',
     'version': {'number': '7.10.0',
      'build_flavor': 'default',
      'build_type': 'tar',
      'build_hash': '51e9d6f22758d0374a0f3f5c6e8f3a7997850f96',
      'build_date': '2020-11-09T21:30:33.964949Z',
      'build_snapshot': False,
      'lucene_version': '8.7.0',
      'minimum_wire_compatibility_version': '6.8.0',
      'minimum_index_compatibility_version': '6.0.0-beta1'},
     'tagline': 'You Know, for Search'}
    elk.stop()
    Out[8]: <Container: 41061dd5a2>

