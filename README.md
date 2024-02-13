# ACCORDION
[![Documentation Status](https://readthedocs.org/projects/melody-accordion/badge/?version=latest)](https://melody-accordion.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pitt-miskov-zivanov-lab/ACCORDION/HEAD?labpath=%2Fexamples%2Fuse_ACCORDION.ipynb)

### (ACCelerating and Optimizing model RecommenDatIONs)

ACCORDION (ACCelerating and Optimizing model RecommenDatIONs) is a novel tool and methodology for rapid model assembly by automatically extending and evaluating dynamic network models with the information published in literature. This facilitates information reuse and data reproducibility and replaces hundreds or thousands of manual experiments, thereby reducing the time needed for the advancement of knowledge.

## Contents

- [Functionality](#Functionality)
- [I/O](#IO)
- [Online Web-based Usage](#Online-Web-based-Usage)
- [Offline Installation](#Offline-Installation)
- [Package Structure](#Package-Structure)
- [Case Study: T cell differentiation](#Case-Study-T-cell-differentiation)
- [Citation](#Citation)
- [Funding](#Funding)
- [Support](#Support)

## Functionality
An automated framework for clustering and selecting relevant data for guided network extension and query answering. More specifically, answering biological questions by automatically assembling new, or expanding existing models using published literature.
- Clustering: creating groups of interactions, related to an existing model
- Extension: adding different groups of extensions to the model and evaluating the model behavior using defined properties

## I/O and Parameters


### Input
- A .xlsx file containing the baseline model to extend, in the tabular format with the following column headers, see [`examples/input/BaselineModel_Tcell.xlsx`](examples/input/BaselineModel_Tcell.xlsx)
Element Name, Element IDs, Positive Regulators, Negative Regulators, Levels, Initial 0
- Machine reading output file with the following header, it has potential interactions that could be added to baseline model, see [`examples/input/CandidateEvents_Tcell.csv`](examples/input/CandidateEvents_Tcell.csv)
RegulatedName, RegulatedID, RegulatedType, RegulatorName, RegulatorID, RegulatorType, PaperID
- Property files containing the property expression based on BLTL syntax, they are the golden properties that the extended models should satisfy, see them at directory [`examples/input/Properties_Tcell/p1`](examples/input/Properties_Tcell/p1)

### Parameters
- Inflation parameter for Markov Clustering, defined in Cell 14 of the notebook
- Number of return paths, defined in Cell 19 of the notebook

### Intermediate Output
- [`examples/output/abc_model`](examples/output/abc_model), network edges with only baseline model interactions
- [`examples/output/abc_model_network`](examples/output/abc_model_network), network edges with baseline model and machine reading output network

### Output: Clusters
- [`examples/output/markov_cluster`](examples/output/markov_cluster), a cluster dictionary that contains individual clusters, each line shows one cluster, formed by element in the baseline model or machine reading output

### Output: Candidate Extended Model
- [`examples/output/grouped_ext`](examples/output/grouped_ext), a pickle file containing grouped (clustered) extensions, specified as nested lists. Each group starts with an integer, followed by interactions specified as [regulator element, regulated element, Interaction type: Activation (+) or Inhibition (-)]. This file along with the directory of system properties will be the input to the statistical model checking to verify the behavior of candidate models against the properties
- [`examples/output/grouped_ext_Merged`](examples/output/grouped_ext_Merged), a pickle file containing the merged clusters (different than _grouped_ext_ which is not merged), clusters are merged based on user-selected number of return paths
- [`examples/output/BaselineModel_Tcell_Extension_Candidate_1.xlsx`](examples/output/BaselineModel_Tcell_Extension_Candidate_1.xlsx), a new .xlsx file containing the resulting candidate extended model, this is just one candidate extension and there could be many candidates
- [`examples/output/BaselineModel_Tcell_Extension_Candidate_2.xlsx`](examples/output/BaselineModel_Tcell_Extension_Candidate_2.xlsx), a new .xlsx file containing another resulting candidate extended model, same as above

### Output: Model Checking
- [`examples/checking`](examples/checking), containing model checking results of the resulting extended model against properties
- [`examples/traces`](examples/traces), containing trace files generated from simulating the resulting extended model, required by statistical model checking


## Online Web-based Usage
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pitt-miskov-zivanov-lab/ACCORDION/HEAD)

Run the demonstrated example (read the comments in each cell and uncomment some to choose your case study); or alternatively upload user-customized input files (see [I/O](#IO)) to the _input/_ directory on File Browser Tab (upper left corner) of Binder.

#### This interactive jupyter notebook walks you though all of the code and functions to:

1. Become familiar with and parse the input files including baseline model spreadsheet and machine reading extracted events.
2. Cluster events into groups, generate extension candidates and possibly merge some candidates.
3. Modify the baseline model spreadsheet according to extension candidates.
4. Test new model files against system properties and obtain model checking results that will help modelers choose the best extended model from the set of available candidate models.

## Offline Installation

1. Clone the ACCORDION repository to your computer.
   ```
   git clone https://github.com/pitt-miskov-zivanov-lab/ACCORDION.git
   ```
2. Navigate into the directory, install ACCORDION and its python dependencies and two non-python dependencies.
   ```
   cd ACCORDION
   python setup.py install
   ```
   Check [ReadTheDocs page of this ACCORDION tool](https://accordion.readthedocs.io/en/latest/TutorialandInstallation.html#offline-installation) for more detailed installtion instructions and debugging suggestions, MacOS/Linux users have alternative way to build non-python packages using managers like [conda](https://anaconda.org/bioconda/mcl), [brew](https://formulae.brew.sh/formula/gsl), [apt](https://manpages.ubuntu.com/manpages/jammy/en/man8/apt.8.html), Windows users may need [Cygwin](https://www.cygwin.com) installation to compile.

3. Run the provided notebook (Check [Jupyter notebook installation](https://jupyter.org/install) here).
   ```
   jupyter notebook examples/use_ACCORDION.ipynb
   ```

## Package Structure

- [`setup.py`](setup.py): python file that help set up python dependencies installation and non-python package building
- [`src/`](src/): directory that includes core python ACCORDION files
  - [`src/runAccordion.py`](src/runAccordion.py): functions for extending discrete network models in the BioRECIPES tabular format using knowledge from literature, as well as adding different groups of extensions to the model
  - [`src/markovCluster.py`](src/markovCluster.py): contains the functions that creates and clusters the network of baseline model and machine reading output
- [`dependencies/`](dependencies/): dependencies directory, containing gsl and MCL packages and model checking module (part of [DySE framework](https://www.nmzlab.pitt.edu/our-tools))
- [`examples/`](examples/): directory that includes tutorial notebook and example inputs and outputs
- [`environment.yml`](environment.yml): environment file, required by [Binder](https://mybinder.readthedocs.io/en/latest/using/config_files.html#environment-yml-install-a-conda-environment)
- [`postBuild`](postBuild): path settings and compilation, used by [Binder](https://mybinder.readthedocs.io/en/latest/using/config_files.html#postbuild-run-code-after-installing-the-environment)
- [`docs/`](docs/): containing files supporting the repo's host on [Read the Docs](https://accordion.readthedocs.io)
- [`supplementary/`](supplementary): containing supplementary files for paper manuscript
- [`LICENSE.txt`](LICENSE.txt): MIT License
- [`README.md`](README.md): it's me!

## Case Study: T cell differentiation

1. **Input 1**: The baseline model (BM) to be extended is given in [`examples/input/BaselineModel_Tcell.xlsx`](examples/input/BaselineModel_Tcell.xlsx), with 62 elements, key information of this model is listed below:

| Element Name | Positive Regulators                     | Negative Regulators | Levels | Initial 0 |
| ------------ | --------------------------------------- | ------------------- | ------ | --------- |
| AKT          | (PDK1,MTORC2)                           | AKT_OFF             | 2      | 0         |
| AKT_OFF      |                                         |                     | 2      | 0         |
| AP1          | (FOS_DD,JUN)                            |                     | 2      | 0         |
| CA           | TCR                                     |                     | 2      | 0         |
| CD122        |                                         |                     | 2      | 1         |
| CD132        |                                         |                     | 2      | 1         |
| CD25         | FOXP3,(AP1,NFAT,NFKAPPAB),STAT5         |                     | 2      | 0         |
| ...          | ...                                     |      ...            | ...    | ...       |
| TAK1         | PKCTHETA                                |                     | 2      | 0         |
| TCR          | TCR_LOW,TCR_HIGH                        |                     | 2      | 0         |
| TCR_HIGH     |                                         |                     | 2      | 0         |
| TCR_LOW      |                                         |                     | 2      | 0         |
| TGFBETA      |                                         |                     | 2      | 0         |
| TSC          |                                         | AKT                 | 2      | 1         |
| FOXO1        |                                         |                     | 2      | 1         |

 **Input 2**: The candidate event (CE) set, represented as a set of signed directed edges, is given in [`examples/input/CandidateEvents_Tcell.csv`](examples/input/CandidateEvents_Tcell.csv). The studied candidate set has 118 events, with key information as follows:

| regulator_name | regulated_name | interaction | PaperID    |
| -------------- | -------------- | ----------- | ---------- |
| AKT            | CD4            | decreases   | PMC2275380 |
| AKT            | CTRL           | decreases   | PMC2275380 |
| TGFBETA        | AKT            | increases   | PMC2275380 |
| Foxp3          | Ctla4          | increases   | PMC2275380 |
| Foxp3          | Gpr83          | increases   | PMC2275380 |
| Pten           | CD8            | increases   | PMC3375464 |
| PTEN           | HSC            | increases   | PMC3375464 |
| ...            | ...            | ...         | ...        |
| TCR            | MEK1           | increases   | PMC4418530 |
| TCR            | CK2            | increases   | PMC4418530 |
| MTORC2         | MTORC2         | increases   | PMC4418530 |
| CD28           | MTORC2         | increases   | PMC4418530 |
| IL2_EX         | MTORC2         | increases   | PMC4418530 |
| IL2_R          | MTORC2         | increases   | PMC4418530 |
| PI3K           | PIP3           | increases   | PMC4418530 |

2. Markov cluster algorithm is applied to cluster the set of candidate event (with a user-defined inflation parameter of 2), 17 clusters are detected as follows:

| Clusters   | Interaction List|
| ---------- | --------------- |
| Cluster 1   |   ['AKT', 'FOXO1', '-'],<br>  ['PTEN', 'AKT', '-'],<br>  ['MEK1_ext', 'PTEN', '+'],<br>  ['AKT', 'MEK1_ext', '-'],<br>  ['TBK1_ext', 'AKT', '-'],<br>  ['AKT', 'MAGI1_ext', '-'],<br>  ['FOXO1', 'PTEN', '+'],<br>  ['PIP3', 'AKT', '+'],<br>  ['PTEN', 'AKT', '+'],<br>  ['AKT', 'TBK1_ext', '+'],<br>  ['CHK1_ext', 'AKT', '+'],<br>  ['FOXO1', 'Foxo3a_ext', '-'],<br>  ['TBK1_ext', 'CD4_ext', '-'],<br>  ['MEK1_ext', 'AKT', '-'],<br>  ['AKT', 'FoxO3_ext', '-'],<br>  ['TBK1_ext', 'AKT', '+'],<br>  ['TGFBETA', 'AKT', '+'],<br>  ['IFNgamma_ext', 'AKT', '+'],<br>  ['CK2_ext', 'AKT', '+'],<br>  ['AKT', 'CD4_ext', '-'],<br>  ['Itk_ext', 'CD4_ext', '+'],<br>  ['CTLA4_ext', 'AKT', '-'],<br>  ['CD4_ext', 'IL17A_ext', '-'],<br>  ['TCR', 'MEK1_ext', '+'],<br>  ['PDK1', 'AKT', '+'],<br>  ['CK2_ext', 'CD4_ext', '+'],<br>  ['AKT', 'CTRL_ext', '-'],<br>  ['AKT', 'Itk_ext', '-'],<br>  ['MTOR', 'TBK1_ext', '+'],<br>  ['PI3K', 'AKT', '-'],<br>  ['TCR', 'CD4_ext', '-'],<br>  ['TBK1_ext', 'FOXO1', '+'],<br>  ['TIL_ext', 'AKT', '-'],<br>  ['Bcl2l11_ext', 'CD4_ext', '+'],<br>  ['TBK1_ext', 'CD4_ext', '+'],<br>  ['PI3K', 'AKT', '+'],<br>  ['MTORC2', 'AKT', '+'],<br>  ['MTOR', 'AKT', '+'],<br>  ['PD1_ext', 'AKT', '-'],<br>  ['AKT', 'MTORC2', '-'],<br>  ['SHIP1_ext', 'AKT', '-'],<br>  ['TCR', 'AKT', '-'],<br>  ['Itk_ext', 'CD4_ext', '-'] |
| Cluster 2  |   ['TCR', 'MTORC2', '+'],<br>  ['TCR', 'CK2_ext', '+'],<br>  ['TCR', 'Itk_ext', '+'],<br>  ['TCR', 'CD25', '+'],<br>  ['TCR', 'PTEN', '-'],<br>  ['CK2_ext', 'PTEN', '-'],<br>  ['P53_ext', 'PTEN', '-'],<br>  ['PI3K', 'PTEN', '+'],<br>  ['TCR', 'NEDD4_ext', '+'],<br>  ['PTEN', 'HSC_ext', '+'],<br>  ['MEK2', 'PTEN', '+'],<br>  ['NEDD4_ext', 'PTEN', '-'],<br>  ['PI3K', 'PIP3', '+'],<br>  ['PTEN', 'PIP3', '-'],<br>  ['PTEN', 'Itk_ext', '-'],<br>  ['RAS', 'PTEN', '-'],<br>  ['PI3K', 'PTEN', '-'],<br>  ['TCR', 'PIP3', '+'],<br>  ['PTEN', 'CD8_ext', '+'] |
| Cluster 3  |   ['CD25', 'MTORC2', '+'],<br>  ['FOXP3', 'Ctla4_ext', '+'],<br>  ['FOXP3', 'Gpr83_ext', '+'],<br>  ['FOXP3', 'Itk_ext', '+'],<br>  ['IL2', 'Itk_ext', '+'],<br>  ['IL2', 'MTORC2', '+'] |
| …          | …  |
| Cluster 15 |   ['ERK', 'S5B_ext', '+']  |
| Cluster 16 |   ['FASL_ext', 'FAS_ext', '+'] |
| Cluster 17 |   ['HIF1alpha_ext', 'IL17A_ext', '-'] |

3. We now extend the baseline model to include candidate event set and obtain 17 candidate models, see two examples at [`examples/output/BaselineModel_Tcell_Extension_Candidate_1.xlsx`](examples/output/BaselineModel_Tcell_Extension_Candidate_1.xlsx) and [`examples/output/BaselineModel_Tcell_Extension_Candidate_2.xlsx`](examples/output/BaselineModel_Tcell_Extension_Candidate_2.xlsx). The first extended candidate model now has 79 elements (compared to 62 of baseline model), and its top seven rows are now as follows:

| Element Name | Positive Regulators                                                                          | Negative Regulators                                                         | Levels | Initial 0 |
| ------------ | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------ | --------- |
| AKT          | (PDK1,MTORC2),PIP3,PTEN,CHK1_ext,<br>TBK1_ext,TGFBETA,IFNgamma_ext,<br>CK2_ext,PDK1,PI3K,MTORC2,MTOR | AKT_OFF,PTEN,TBK1_ext,MEK1_ext,<br>CTLA4_ext,PI3K,TIL_ext,PD1_ext,<br>SHIP1_ext,TCR | 2      | 0         |
| AKT_OFF      |                                                                                              |                                                                             | 2      | 0         |
| AP1          | (FOS_DD,JUN)                                                                                 |                                                                             | 2      | 0         |
| CA           | TCR                                                                                          |                                                                             | 2      | 0         |
| CD122        |                                                                                              |                                                                             | 2      | 1         |
| CD132        |                                                                                              |                                                                             | 2      | 1         |
| CD25         | FOXP3,(AP1,NFAT,NFKAPPAB),STAT5                                                              |                                                                             | 2      | 0         |

For example, the extension is obvious that regulators for `AKT` are significantly updated.

We omit to show the remaining candidate models, but all 17 of them are listed under the directory of [`examples/output/`](examples/output/). Under different parameters, total number of candidate models may vary.

4. Statistical model checking is run on the candidate models, against golden properties. The properties are extracted from golden models, indicating the golden behavior that a model expect to satisfy under certain scenario. For example, we test five candidate models against four properties stored in [`examples/input/Properties_Tcell/p1/`](examples/input/Properties_Tcell/p1/). A property match table summarizes all the probabilities. Users are able to choose the preferred candidate model by the criterion of general satisfication or priortized satisfication, subject to certain application scenario.

|                       | Property 1d  | Property 1c  | Property 1b  | Property 1a  |
| --------------------- | -------- | -------- | -------- | -------- |
| Extension_Candidate_1 | 0.711712 | 0.956522 | 0.956522 | 0.956522 |
| Extension_Candidate_2 | 0.956522 | 0.956522 | 0.956522 | 0.956522 |
| Extension_Candidate_3 | 0.956522 | 0.956522 | 0.956522 | 0.956522 |
| Extension_Candidate_4 | 0.956522 | 0.956522 | 0.956522 | 0.956522 |
| Extension_Candidate_5 | 0.956522 | 0.956522 | 0.956522 | 0.956522 |

5. Two other case studies of TLGL and PCC are available, users can edit and uncomment cell 7, 10, 14, 23, 26, 31, 32 to play with other case studies. 

## Citation

_Yasmine Ahmed, Cheryl Telmer, Gaoxiang Zhou, Natasa Miskov-Zivanov, “Context-aware knowledge selection and reliable model recommendation with ACCORDION”, bioRxiv preprint, doi: https://doi.org/10.1101/2022.01.22.477231._

## Funding

This work was funded in part by DARPA Big Mechanism award, AIMCancer (W911NF-17-1-0135); and in part by the University of Pittsburgh, Swanson School of Engineering.

## Support
For installtion and reproducibility concerns, feel free to reach out to Natasa Miskov-Zivanov: nmzivanov@pitt.edu
