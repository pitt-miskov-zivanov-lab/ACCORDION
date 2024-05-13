########################
Online Web-based Usage
########################
.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/pitt-miskov-zivanov-lab/ACCORDION/HEAD?labpath=%2Fexamples%2Fuse_ACCORDION.ipynb

Click the icon above and run the demonstrated example; or alternatively upload user-customized input files to the input/ directory on File Browser Tab (upper left corner) of Binder.

This interactive jupyter notebook walks you though all of the code and functions to:
 * Get familiar with and parse the input files including baseline model spreadsheet and machine reading extracted events.
 * Cluster events into groups, generate extension candidates and possibly merge some candidates.
 * Modify baseline model spreadsheet according to extension candidates.
 * Test new model files against system properties and obtain model checking results that will help modelers choose the best extension among candidates.

########################
Offline Installation
########################

ACCORDION requires Python and C compiler installed on local machine. If users want to explore the interactive notebook we provided locally, Jupyter notebook installation is also required.

1. Clone the `ACCORDION repository <https://github.com/pitt-miskov-zivanov-lab/ACCORDION>`_, to your computer.

.. code-block:: bash

 git clone https://github.com/pitt-miskov-zivanov-lab/ACCORDION.git

2. Navigate into the directory, install ACCORDION, its python dependencies and two non-python dependencies (MCL-a cluster algorithm for graphs, GSL-GNU Scientific Library).

..

   - **MacOS/Linux**

.. code-block:: bash

 cd ACCORDION
 python setup.py install

.. admonition:: And alternatively on MacOS/Linux

 - Feel free to only install python dependencies first via ``cd ACCORDION && pip install -e .``
 - And build non-python packages using your package managers. For MCL, try |br| ``sudo apt-get install mcl`` or ``conda install -c "bioconda/label/cf201901" mcl``; For GSL, try ``sudo apt-get install libgsl-dev`` or ``conda install -c conda-forge gsl`` or ``brew install gsl``
 - Compile two C++ files to executables via |br| ``cd dependencies/Model_Checking/dishwrap_v1.0/dishwrap && make && cd ../monitor && make``
 - The following libraries might also be required to compile successfully: ``boost``, ``flex``, ``bison``; install them via apt-get / conda / brew and update your system ``CPLUS_INCLUDE_PATH`` when there are related errors

..

   - **Windows (preferably in Cygwin Terminal)**

.. code-block:: bash

 cd ACCORDION
 python setup.py install

.. Attention::
 **Windows users**: Since many commands in C building process are not available on fresh Windows, `Cygwin <https://www.cygwin.com>`_ installation is encouraged as it has a large collection of open source tools which provide functionality similar to a Linux distribution

 - During Cygwin installation, follow default options given, but take time in :guilabel:`Select Packages` stage, :guilabel:`Search` in full view the following packages and change from ``skip`` option to certain version: |br| ``bison,flex,gcc-core(==7.4.0-1),gcc-g++(==7.4.0-1),gsl,libboost-devel,libgsl-devel,make``
 - Open Cygwin Terminal to build and compile, you need to first use ``cd C:`` to change directory to C drive and then further change to local files
 - Force Cygwin to run python executeable of Windows, not the python executeable in Cygwin's own bin folder:

   - first, run ``where python`` in Windows Command Prompt to get python location |br| (e.g., ``C:\{this\is\the\path\to}\python.exe`` );
   - then, run ``export PATH=/cygdrive/C/{this/is/the/path/to}/:$PATH`` in Cygwin Terminal;
   - lastly, check ``which python`` in Cygwin Terminal, it should not return ``/usr/bin/python`` again.
 - Make sure to use the above ``export`` command each time you open a new Cygwin Terminal


3. Run the provided notebook.

.. code-block:: bash

  jupyter notebook examples/use_ACCORDION.ipynb

########################
Input and Output
########################

Input includes:
  * a .xlsx file containing the model to extend, in the `BioRECIPE model<https://melody-biorecipe.readthedocs.io/en/latest/model_representation.html>`_ format, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/input/BaselineModel_Tcell.xlsx>`_
  * a machine reading output file, in the `BioRECIPE interaction<https://melody-biorecipe.readthedocs.io/en/latest/bio_interactions.html>`_ format, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/input/CandidateEvents_Tcell.csv>`_
  * inflation parameter for markov clustering
  * number of return paths
  * property file containing the property expression based on BLTL syntax, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/tree/main/examples/input/Properties_Tcell>`_

Output includes:
  * a cluster dictionary that contains individual clusters, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/markov_cluster>`_
  * a pickle file containing grouped (clustered) extensions, specified as nested lists. Each group starts with an integer, followed by interactions specified as [regulator element, regulated element, Interaction type: Activation (+) or Inhibition (-)], `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/grouped_ext>`_. This file along with the directory of system properties will be the input to the statistical model checking to verify the behavior of candidate models against the properties
  * another pickle file containing the merged clusters (different than _grouped_ext_ which is not merged), clusters are merged based on user-selected number of return paths, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/grouped_ext_Merged>`_
  * a new .xlsx file containing the resulting extended model, this is just one candidate extension and there could be many candidates, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/BaselineModel_Tcell_Extension_Candidate_1.xlsx>`_
  * model checking results of the resulting extended model against properties, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/tree/main/examples/checking>`_

########################
Dependency Resources
########################

  * `Model Checking module <https://www.nmzlab.pitt.edu/our-tools>`_, part of DySE framework, being used to test new model files against system properties
  * `GSL - GNU Scientific Library <https://www.gnu.org/software/gsl/>`_, required by model checking module
  * `MCL - a cluster algorithm for graphs <http://micans.org/mcl/>`_, being used to cluster events into groups

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />
