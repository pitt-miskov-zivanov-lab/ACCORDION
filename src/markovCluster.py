import re, copy, sys, os
from collections import defaultdict
import pickle
import logging

def runMarkovCluster(out_dir,ext_edges,base_model,coef):
	"""
 	This function prepares the inputs to the markov clustering algorithm (MCL) and creates a pickle file for
	the output clusters with interaction information. It also returns a modified baseline model (without introducing new nodes).

	Parameters
	----------
	out_dir : str
		Path of the directory that will include all output files (including intermediate and final results)
	ext_edges : set
		Holds the interactions in the reading output file (extracted events). Each interaction is in the form:
		(regulator element, regulated element, type of interaction (+/-))
	base_model : dict
		Dictionary that holds baseline model elements and corresponding regulator elements
	coef :	 int
		The inflation parameter of the markov clustering algorithm

	Returns
	-------
  	res : list
		Each item in this list is a grouped extension (i.e., this indivisible group is one candidate for model extension).
		It's also stored as 'grouped_ext' file.
	new_base_model : dict
		The baseline model elements are keys of this dict and the values are the corresponindg regulator elements(includes new edges information from extracted events).
	"""

	ext_model,new_base_model = buildExtGraph(ext_edges,base_model)
	clusteringAlgo(out_dir,ext_model,coef)
	ModelNetwork(out_dir,base_model)
	res = getGroupedExt(out_dir+'markov_cluster',ext_edges)
	pickle.dump(res, open(out_dir+'grouped_ext','wb'))
	return res, new_base_model

def buildExtGraph(ext_edges,base_model=dict()):
	"""
 	A utility function for runMarkovCluster(), this function constructs two graph models, one with the whole extension information (i.e., with both new edges and new nodes),
	another for the modified baseline model (i.e.,without introducing new nodes)

	Parameters
	----------
	ext_edges : set
		Holds the interactions in the reading output file (extracted events). Each interaction is in the form:
		(regulator element, regulated element, type of interaction (+/-))
	base_model : dict
		Dictionary that holds baseline model elements and corresponding regulator elements

	Returns
	-------
  	ext_model : dict
		This dict contains the elements of both the baseline model and the reading output file.
		Those elements are the keys and the values are the corresponding regulator elements.
	new_base_model : dict
		The baseline model elements are keys of this dict and the values are the corresponindg regulator elements.
	"""

	new_base_model=dict()
	for k in base_model:
		new_base_model[k]=base_model[k]['regulators']
	ext_model = copy.deepcopy(new_base_model)
	for edge in ext_edges:
		if edge[1] in ext_model:
			ext_model[edge[1]].add(edge[0])
		else:
			ext_model[edge[1]] = {edge[0]}
	return ext_model,new_base_model

def clusteringAlgo(MCL_result_folder,ext_model,coef):
	"""
 	A utility function for runMarkovCluster(), this function is designed to run Markov Clustering Algorithm(MCL) obtained at https://micans.org/mcl/, build on its latest stable release /mcl/src/mcl-14-137

	Parameters
	----------
	MCL_result_folder : str
		Folder name of the directory that will store the intermediate and final result file of MCL algorithm, default as 'examples/Output/'.
		Inside the folder, 'markov_cluster' file is the final clustering result, with each row in this file being a cluster.
	ext_model : dict
		This dict contains the elements of both the baseline model and the reading output file.
		Those elements are the keys and the values are the corresponding regulator elements.
	coef :	 int
		The inflation parameter of the Markov Clustering Algorithm(MCL)
	"""

	# translate ext_model into the abc format supported by MCL, stored inside 'abc_model'(an intermediate output)
	abc_model = MCL_result_folder + 'abc_model'
	output_stream = open(abc_model, 'w')
	for tgt in sorted(ext_model):
		for reg in sorted(ext_model[tgt]):
			if tgt==reg: continue
			output_stream.write(reg+' '+tgt+' '+str(1)+'\n')
	output_stream.close()

	MCL_result_file = MCL_result_folder + 'markov_cluster'

	cmd = 'mcl '+abc_model.replace(' ','\ ')+' --abc -I '+str(coef)+' -o '+MCL_result_file.replace(' ','\ ')
	logging.info('Running the following command through MCL algorithm:\n{}\n'.format(cmd))
	os.system(cmd)

def ModelNetwork(out_dir,base_model):
	"""
 	A utility function for runMarkovCluster(), this function translates the baseline model to a file with edges of interactions (serves as an intermediate result file)

	Parameters
	----------
	out_dir : str
		Path of the directory that will include the output file
	base_model : dict
		Dictionary that holds baseline model elements and corresponding regulator elements

	"""

	new_base_model=dict()
	for k in base_model:
		new_base_model[k]=base_model[k]['regulators']
	abc_model = out_dir + 'abc_model_network'
	output_stream = open(abc_model, 'w')
	for tgt in sorted(new_base_model):
		for reg in sorted(new_base_model[tgt]):
			if tgt==reg: continue
			output_stream.write(reg+' '+tgt+'\n')
	output_stream.close()

def getGroupedExt(cluster_file,ext_edges):
	"""
 	A utility function for runMarkovCluster(), this function summarizes the clustering result file and interaction information to generate list of candidate extensions

	Parameters
	----------
	cluster_file : str
		The path of the markov_cluster file (the result of MCL algorithm), each row in this file is a list that is classified as a cluster
	ext_edges : set
		Holds the interactions in the reading output file (extracted events). Each interaction is in the form:
		(regulator element, regulated element, type of interaction (+/-))

	Returns
	-------
  	res : list
		Each item in this list is a grouped extension (i.e., this indivisible group is one candidate for model extension)
	"""

	group_num = 1
	get_group = dict()
	get_ext = defaultdict(list)
	res = list()
	with open(cluster_file) as f:
		for idx, line in enumerate(f,start=1):
			for ele in re.findall('\S+',line.strip()):
				#print(idx)
				get_group[ele] = idx

	for edge in ext_edges:
		g1 = get_group[edge[0]] if edge[0] in get_group else sys.maxsize
		g2 = get_group[edge[1]] if edge[1] in get_group else sys.maxsize
		group = min(g1, g2)
		if group==sys.maxsize: continue
		get_ext[group] += [list(edge)]

	for key in sorted(get_ext):
		if not get_ext[key]: continue
		res.append([group_num]+get_ext[key])
		group_num += 1

	return res
