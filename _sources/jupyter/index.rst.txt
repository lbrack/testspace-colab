.. highlight:: shell

Jupyter Notebooks
=================

Below, you will find the documentation for any available notebooks.
To run Jupyter Lab, you have several options:

    1 - In the Browser

        .. code-block:: console

            $ ts-colab jupyter --no-elk

    2 - In VSCode

        .. code-block:: console

            $ pip install ipykernel
            $ python3 -m ipykernel install --user --name=testspace-colab

        The in VSCode, click on the Kernel (located on the top right corner
        of the notebook), and select the "testspace-colab" kernel

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples/index

IMPORTANT
---------

    The CI system runs the notebook that are listed herein. However, it is essential
    that those notebooks are saved with a ``testspace-colab`` kernel name as shown
    below

    .. image:: kernel-spec.png

    To generate such spec, run the following in **your virtualenv**. Note that this
    is done automatically by make install

    .. code-block:: console

        (testspace)⚡ ⇒   pip install ipykernel
        (testspace)⚡ ⇒   python3 -m ipykernel install --user --name=testspace-colab

    The **ONLY** thing that matters is the **NAME**


