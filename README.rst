===============
testspace-colab
===============


.. image:: https://img.shields.io/pypi/v/testspace_colab.svg
        :target: https://pypi.python.org/pypi/testspace_colab

.. image:: https://readthedocs.org/projects/testspace-colab/badge/?version=latest
        :target: https://testspace-colab.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

A collaborative environment to experiment with data extracted from testspace.
This project provides a complete environment to mind data from Testspace,
persist it, and analyze it. The intent is to provide a prototyping environment
for Testspace's Insight 2.0.

* Free software: MIT license
* Documentation: `documentation`_


Features
--------

* Contains testspace client binaries (2.5.4061)
* Provides a CLI (ts-colab) as well as an API
* See the `user manual`_ to get started
* Provides facility to start an ELK (ElasticSearch/Logstach/Kibana)
  via the `sebp/elk docker image`_. All that is needed is to have `docker`_ installed
  on your machine. Refer to the documentation for additional details.

Development
-----------

Check the
`contributing guidelines <https://m.devpi.net/testspace/dev/testspace-colab/latest/+d/contributing.html>`_
to learn how to clone, install, develop and release this project.

.. _`documentation` : https://m.devpi.net/testspace/dev/testspace-colab/latest/+d/index.html
.. _`readthedocs` : https://testspace-colab.readthedocs.io
.. _`user manual` : https://m.devpi.net/testspace/dev/testspace-colab/latest/+d/usage.html
.. _`docker` : https://docker-py.readthedocs.io/en/stable/
.. _`sebp/elk docker image` : https://hub.docker.com/r/sebp/elk
