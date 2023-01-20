# ACCORDION
[![Documentation Status](https://readthedocs.org/projects/accordion/badge/?version=latest)](https://accordion.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pitt-miskov-zivanov-lab/ACCORDION/HEAD?labpath=%2Fexamples%2Fuse_ACCORDION.ipynb)

### (ACCelerating and Optimizing model RecommenDatIONs)

ACCORDION (ACCelerating and Optimizing model RecommenDatIONs) is novel tool and methodology for rapid model assembly by automatically extending dynamic network models with the information published in literature. This facilitates information reuse and data reproducibility and replaces hundreds or thousands of manual experiments, thereby reducing the time needed for the advancement of knowledge.

## Contents

- [Functionality](#Functionality)
- [I/O](#IO)
- [Online Tutorial](#Online-Tutorial)
- [Offline Installation](#Offline-Installation)
- [Package Structure](#Package-Structure)
- [Citation](#Citation)
- [Funding](#Funding)
- [Support](#Support)

## Functionality
An automated framework for clustering and selecting relevant data for guided network extension and query answering. More specifically, answering biological questions by automatically assembling new, or expanding existing models using published literature.
- Clustering: creating groups of interactions, comparing to an existing model
- Extension: adding different groups of extensions to the model and verifying behavior against defined properties

## I/O

### Input
- A .xlsx file containing the model to extend, in the BioRECIPES tabular format, see [`examples/input/BooleanTcell.xlsx`](examples/input/BooleanTcell.xlsx)
- Machine reading output file with the following header, see [`examples/input/MachineReadingOutput.csv`](examples/input/MachineReadingOutput.csv)
RegulatedName,RegulatedID,RegulatedType,RegulatorName,RegulatorID,RegulatorType,PaperID
- Inflation parameter for Markov Clustering, defined in Cell 12 of the notebook
- Number of return paths, defined in Cell 17 of the notebook
- Property file containing the property expression based on BLTL syntax, see them at directory [`examples/input/TheProperties/p1`](examples/input/TheProperties/p1)

### Output

- [`examples/output/markov_cluster`](examples/output/markov_cluster), a cluster dictionary that contains individual clusters
- [`examples/output/grouped_ext`](examples/output/grouped_ext), a pickle file containing grouped (clustered) extensions, specified as nested lists. Each group starts with an integer, followed by interactions specified as [regulator element, regulated element, Interaction type: Activation (+) or Inhibition (-)]. This file along with the directory of system properties will be the input to the statistical model checking to verify the behavior of candidate models against the properties
- [`examples/output/grouped_ext_Merged`](examples/output/grouped_ext_Merged), a pickle file containing the merged clusters (different than _grouped_ext_ which is not merged), clusters are merged based on user-selected number of return paths
- [`examples/output/BooleanTcell_Extension_Candidate_1.xlsx`](examples/output/BooleanTcell_Extension_Candidate_1.xlsx), a new .xlsx file containing the resulting extended model, this is just one candidate extension and there could be many candidates
- [`examples/checking`](examples/checking), containing model checking results of the resulting extended model against properties
- intermediate output - [`examples/output/abc_model`](examples/output/abc_model), network edges with only baseline model interactions
- intermediate output - [`examples/output/abc_model_network`](examples/output/abc_model_network), network edges with baseline model and machine reading output network
- intermediate output - [`examples/traces`](examples/traces), containing trace files generated from simulating the resulting extended model, required by statistical model checking

## Online Tutorial
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pitt-miskov-zivanov-lab/ACCORDION/HEAD)

Run the demonstrated example; or alternatively upload user-customized input files (see [I/O](#IO)) to the _input/_ directory on File Browser Tab (upper left corner) of Binder.

#### This interactive jupyter notebook walks you though all of the code and functions to:

1. Get familiar with and parse the input files including baseline model spreadsheet and machine reading extracted events.
2. Cluster events into groups, generate extension candidates and possibly merge some candidates.
3. Modify baseline model spreadsheet according to extension candidates.
4. Test new model files against system properties and obtain model checking results that will help modelers choose the best extension among candidates.

## Offline Installation

1. Clone the ACCORDION repository to your computer.
   ```
   git clone https://github.com/pitt-miskov-zivanov-lab/ACCORDION.git
   ```
2. Navigate into the directory, install ACCORDION and its python dependencies and two non-python dependencies ([gsl](https://www.gnu.org/software/gsl/) and [MCL](http://micans.org/mcl/)).
   ```
   cd ACCORDION
   python setup.py install
   ```
   Alternatively:
   - You can separate python dependencies installation `pip install -e .`;
   - and non-python dependencies building using package managers like [conda](https://anaconda.org/bioconda/mcl), [brew](https://formulae.brew.sh/formula/gsl), [apt](https://manpages.ubuntu.com/manpages/jammy/en/man8/apt.8.html);
   - in this case, make sure to compile.
   ```
   cd dependencies/Model_Checking/dishwrap_v1.0/dishwrap
   make
   cd ../monitor
   make
   ```
3. Run the provided notebook (Check [Jupyter notebook installation](https://jupyter.org/install) here). Comment Cell 11 & 29 if you already build the non-python dependencies locally.
   ```
   jupyter notebook examples/use_ACCORDION.ipynb
   ```

## Package Structure

- [`setup.py`](setup.py): python file that help set up python dependencies installtion and non-python package building
- [`src/`](src/): directory that includes core python ACCORDION files
  - [`src/runAccordion.py`](src/runAccordion.py): functions for extending discrete network models in the BioRECIPES tabular format using knowledge from literature, as well as adding different groups of extensions to the model
  - [`src/markovCluster.py`](src/markovCluster.py): contains the functions that creates and clusters the network of baseline model and machine reading output
- [`dependencies/`](dependencies/): dependencies directory, containing gsl and MCL packages and model checking module (a part of [DySE framework](https://www.nmzlab.pitt.edu/our-tools))
- [`examples/`](examples/): directory that includes tutorial notebook and example inputs and outputs
- [`environment.yml`](environment.yml): environment file, required by [Binder](https://mybinder.readthedocs.io/en/latest/using/config_files.html#environment-yml-install-a-conda-environment)
- [`postBuild`](postBuild): path settings and compilation, used by [Binder](https://mybinder.readthedocs.io/en/latest/using/config_files.html#postbuild-run-code-after-installing-the-environment)
- [`docs/`](docs/): containing files supporting the repo's host on [Read the Docs](https://accordion.readthedocs.io)
- [`supplementary/`](supplementary): containing supplementary files for paper manuscript
- [`LICENSE.txt`](LICENSE.txt): MIT License
- [`README.md`](README.md): this is me!

## Citation

_Yasmine Ahmed, Cheryl Telmer, Gaoxiang Zhou, Natasa Miskov-Zivanov, “Context-aware knowledge selection and reliable model recommendation with ACCORDION”, bioRxiv preprint, doi: https://doi.org/10.1101/2022.01.22.477231._

## Funding

| Program                  |   Grant Number   |
| ------------------------ | ---------------: |
| DARPA Big Mechanism      | W911NF-17-1-0135 |
| ------------------------ | ---------------: |
| University of Pittsburgh |                  |

## Support
_To be updated_
