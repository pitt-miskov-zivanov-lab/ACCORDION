#############
Installation
#############

ACCORDION requires Python and C compiler installed on local machine. If users want to explore the interactive notebook we provided, Jupyter Notebook is also required.

Cloning Repo
------------------
A copy of the ACCORDION repository can be downloaded from the Bitbucket website at
`https://bitbucket.org/biodesignlab/accordion/src/master/ <https://bitbucket.org/biodesignlab/accordion/src/master/>`_,
or cloned through git at the command line::

    >> git clone https://bitbucket.org/biodesignlab/accordion/src/master/

You will then need to run the `setup.py` file to use ACCORDION as a package, which installs the dependencies python packages
(including networkx, numpy, pandas, openpyxl, math, pickle, matplotlib.pyplot)::

    >> python setup.py install

Building MCL Code
------------------
Markov Cluster Algorithm is called in this tool, users can either visit `https://micans.org/mcl/ <https://micans.org/mcl/>`_ ,
and download the tar.gz file of latest stable release 14-137 and follow installation instructions on site.
Alternatively, install it from the local copy in the repository::

    >> cd dependencies/mcl-14-137
    >> ./configure
    >> make
    >> make install
    >> make clean
    >> make distclean
