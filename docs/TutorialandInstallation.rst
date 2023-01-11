########################
Online Tutorial
########################
.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/pitt-miskov-zivanov-lab/ACCORDION/HEAD

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

2. Navigate into the directory, install ACCORDION and its python dependencies and two non-python dependencies `gsl <https://www.gnu.org/software/gsl/>`_ and `MCL <http://micans.org/mcl/>`_.

.. code-block:: bash

   cd ACCORDION
   python setup.py install

Alternatively: You can (i)-first install python dependencies

.. code-block:: bash

  pip install -e .

(ii)-and non-python dependencies building using package managers like `conda <https://anaconda.org/bioconda/mcl>`_, `brew <https://formulae.brew.sh/formula/gsl>`_, `apt <https://manpages.ubuntu.com/manpages/jammy/en/man8/apt.8.html>`_ |br|
(iii)-in this case, make sure to compile

.. code-block:: bash

  cd dependencies/Model_Checking/dishwrap_v1.0/dishwrap
  make
  cd ../monitor
  make

3. Run the provided notebook. Comment Cell 11 & 29 if you already build the non-python dependencies locally.

.. code-block:: bash

  jupyter notebook examples/use_ACCORDION.ipynb

########################
Input and Output
########################

Input includes:
  * a .xlsx file containing the model to extend, in the BioRECIPES tabular format, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/input/BooleanTcell.xlsx>`_
  * a machine reading output file with the following header, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/input/MachineReadingOutput.csv>`_ |br| RegulatedName, RegulatedID, RegulatedType, RegulatorName, RegulatorID, RegulatorType, PaperID
  * inflation parameter for markov clustering
  * number of return paths
  * property file containing the property expression based on BLTL syntax, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/tree/main/examples/input/TheProperties>`_

Output includes:
  * a cluster dictionary that contains individual clusters, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/markov_cluster>`_
  * a pickle file containing grouped (clustered) extensions, specified as nested lists. Each group starts with an integer, followed by interactions specified as [regulator element, regulated element, Interaction type: Activation (+) or Inhibition (-)], `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/grouped_ext>`_. This file along with the directory of system properties will be the input to the statistical model checking to verify the behavior of candidate models against the properties
  * another pickle file containing the merged clusters (different than _grouped_ext_ which is not merged), clusters are merged based on user-selected number of return paths, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/grouped_ext_Merged>`_
  * a new .xlsx file containing the resulting extended model, this is just one candidate extension and there could be many candidates, `see example <https://github.com/pitt-miskov-zivanov-lab/ACCORDION/blob/main/examples/output/BooleanTcell_Extension_Candidate_1.xlsx>`_
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
