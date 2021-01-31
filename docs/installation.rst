.. highlight:: shell

============
Installation
============

Dev release
-----------

Install the devpi-client (if not already installed)

.. code-block:: console

    $ pip install devpi-client
    $ devpi use https://m.devpi.net/testspace/dev
    $ devpi install testspace-utils

Stable release
--------------

**This project is not published on pypi but on** https://m.devpi.net/testspace

To install testspace-utils, run this command in your terminal:

.. code-block:: console

    $ pip install -i https://m.devpi.net/testspace/prod/+simple/ testspace_utils

This is the preferred method to install testspace-utils, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for testspace-utils can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/lbrack/testspace_utils

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ cd testspace-utils
    $ pip install -e .


.. _Github repo: https://github.com/lbrack/testspace_utils
