ACCORDION

-ACCelerating and Optimizing model RecommenDatIONs


-Functionality

An automated framework for clustering and selecting relevant data for guided network extension and query answering. More specifically, answering biological questions by automatically assembling new, or expanding existing models using published literature. This facilitates information reuse and data reproducibility and replaces hundreds or thousands of manual experiments, thereby reducing the time needed for the advancement of knowledge. 
Clustering: creating groups of interactions, comparing to an existing model
Extension: adding different groups of extensions to the model and verifying behavior against defined properties



-Description of files

.setup.py python package dependencies required
.runACCORDION.py functions for extending discrete network models in the BioRECIPES tabular format using knowledge from literature. 
.markovCluster.py contains the functions that creates and clusters the network of baseline model and machine reading output and adds different groups of extensions to the model
.examples/Input/BooleanTcell.xlsx example of a baseline model in the BioRECIPES format
.examples/Input/MachineReadingOutput.csv example of machine reading output
.examples/Input/TheProperties example of system properties as BLTL expressions for the T cell model



-I/O

Input

.Machine Reading output file with the following header
RegulatedName,RegulatedID,RegulatedType,RegulatorName,RegulatorID,RegulatorType,PaperID
.A file containing the model to extend in the BioRECIPES tabular format
.Inflation parameter for Markov Clustering
.The number of return paths


Output

.grouped_ext A pickle file containing grouped (clustered) extensions, specified as nested lists. Each group starts with an integer, followed by interactions specified as [regulator element, regulated element, Interaction type: Activation (+) or Inhibition (-)
This file along with the directory of system properties will be the input to the statistical model checking to verify the behavior of candidate models against the properties
.grouped_ext_Merged A pickle file containing the merged clusters
.Clusters Directory that contains individual clusters 
.abc_model Baseline model network
.abc_model_network Baseline model + machine reading output network