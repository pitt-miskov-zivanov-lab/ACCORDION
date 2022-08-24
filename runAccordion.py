"""
@author: Yasmine
"""

import pandas as pd
import re
from markovCluster import runMarkovCluster
from markovCluster import extend_model
import argparse
import networkx as nx
import pickle
import time


#This function and the following function are inherited from DySE framework
# define regex for valid characters in variable names
_VALID_CHARS = r'a-zA-Z0-9\@\_\/'


def get_model(model_file):
	""" Return a dictionary of the model regulators, ids, etc.
	"""

	global _VALID_CHARS

	regulators = dict()
	model_dict = dict()


	# Load the input file containing elements and regulators
	df_model = pd.read_excel(model_file, na_values='NaN', keep_default_na = False)
	# check model format
	if df_model.columns[0].lower() == 'element attributes':
		df_model = df_model.reset_index()
		df_model = df_model.rename(columns=df_model.iloc[1]).drop([0,1]).set_index('#')	

	input_col_name = [x.strip() for x in df_model.columns if ('element name' in x.lower())]
	input_col_ids = [x.strip() for x in df_model.columns if ('ids' in x.lower())]
	
	input_col_type = [x.strip() for x in df_model.columns if ('element type' in x.lower())]
	input_col_X = [x.strip() for x in df_model.columns if ('variable' in x.lower())]
	input_col_A = [x.strip() for x in df_model.columns if ('positive' in x.lower())]
	input_col_I = [x.strip() for x in df_model.columns if ('negative' in x.lower())]

	# set index to variable name column
	# remove empty variable names
	# append cols with the sets of regulators using .apply

	for curr_row in df_model.index:
		element_name = df_model.loc[curr_row,input_col_name[-1]].strip()
		ids = df_model.loc[curr_row,input_col_ids[0]].strip().upper().split(',')
		#print(ids)
		element_type = df_model.loc[curr_row,input_col_type[0]].strip()
		var_name = df_model.loc[curr_row,input_col_X[0]].strip()
		pos_regulators = df_model.loc[curr_row,input_col_A[0]].strip()
		neg_regulators = df_model.loc[curr_row,input_col_I[0]].strip()

		if var_name == '': 
			continue

		curr = []
		
		if pos_regulators != '': 
			curr += re.findall('['+_VALID_CHARS+']+',pos_regulators)
			
		if neg_regulators != '': 
			curr += re.findall('['+_VALID_CHARS+']+',neg_regulators)

		# returning regulators separately for compatibility with runMarkovCluster
		regulators[var_name] = set(curr)
		model_dict[var_name] = {
			'name' : element_name, 
			'ids' : ids,
			'type' : element_type,
			'regulators' : set(curr)}

	return model_dict, regulators

def getVariableName(model_dict, curr_map, ext_element_info):
	""" Match the element name from the extension to an element in the model 
	"""

	global _VALID_CHARS

	ext_element_name = ext_element_info[0]

	# Check for valid element name
	if ext_element_name=='':
		#logging.warn('Missing element name in extensions')
		return ''	
	elif re.search('[^'+_VALID_CHARS+']+',ext_element_name):
		#logging.warn(('Skipping due to invalid characters in variable name: %s') % str(ext_element_name))
		return ''

	ext_element_id = ext_element_info[3]
	ext_element_type = ext_element_info[5]
	
	if ext_element_name in curr_map: 
		return curr_map[ext_element_name]

	# from the location and type
	match = ext_element_name + '_ext'
	confidence = 0.0
	# Iterate all names in the dictionary and find the most likely match
	for key,value in model_dict.items():

		curr_conf = 0.0
		if ext_element_id.upper() in value['ids']:
			curr_conf = 1
		elif ext_element_name.upper().startswith(value['name'].upper()) \
			or value['name'].upper().startswith(ext_element_name.upper()):
			curr_conf = 0.8

		if curr_conf>0 and value['type'].lower().startswith(ext_element_type):
			curr_conf += 1

		if curr_conf > confidence:
			match = key
			confidence = curr_conf
			if curr_conf==2: break

	curr_map[ext_element_name] = match
	return match

def parseExtension(model_dict, ext_file):
	""" 
     This function converts the interactions within the reading output file 
     into BioRECIPES format.
     
     Parameters
     ----------
     model_dict : dict
         Dictionary that holds baseline model regulator and regulated elements
     ext_file : str
         The path of the reading output file
         
     Returns
     -------
     ext_edges : set()
         Each interaction within the reading output file will have the format
         (regulator element, regulated element, type of interaction (+/-))
	"""    
	regulated_col = 8
	interaction_col = 16
	ext_edges, curr_map = set(),  dict()
    
	with open(ext_file) as f:
		for line in f:
			if line.startswith('regulator_name'): continue 
			line = line.strip()
			s = re.split(',',line)
			name1, name2 = getVariableName(model_dict,curr_map,s[0:regulated_col]), getVariableName(model_dict,curr_map,s[regulated_col:interaction_col])          
			if name1=="" or name2=="": continue
			pos = '+' if s[16]=='increases' else '-'

			if (name2 in model_dict and name1 in model_dict[name2]): 				
				continue
			ext_edges.add((name1, name2, pos))
	return ext_edges

def merge_clusters(regulators, path, ReturnTh):
    """ 
    This function prints indices of clusters  to be merged based on the existence of one or more return paths.
    It generates the grouped_ext_Merged pickle file that contains the merged clusters.
     
    Parameters
    ----------
    regulators : dict
        contains baseline model elements and corresponding regulator elements
    path : str
        The path of the directory that contains the grouped_ext file 
        
     Returns
     -------
    """
    # Merge clusters if there is one or more return paths
    
    G = nx.DiGraph()
    G = makeDiGraphBase(regulators)
    com_edges = list()
    group_num = 1
    extensions = pickle.load(open(path+"grouped_ext",'rb'))    
    
    for ii in range(0,len(extensions)):
        for jj in range(ii+1,len(extensions)):
            count = 0    
            cluster1 = extensions[ii]
            cluster2 = extensions[jj]
            G1 = nx.DiGraph()
            G2 = nx.DiGraph()
            
            for e in cluster1[1:]:
                #ee=e[1].split('->')
                if e[2] == '+':
                    G1.add_edge(e[0], e[1],weight=1) 
                elif e[2] == '-':
                    G1.add_edge(e[0], e[1],weight=0)
                    
            for e in cluster2[1:]:
                #ee=e[1].split('->')
                if e[2] == '+':
                    G2.add_edge(e[0], e[1],weight=1) 
                elif e[2] == '-':
                    G2.add_edge(e[0], e[1],weight=0) 
            Gall = nx.compose(G1,G2) 
            for g in G.edges:
                if g[0] in G1:
                    for ne in G.successors(g[1]):
                        if ne in G2:
                            for ne1 in G2.successors(ne):
                                if ne1 in G:
                                    count = count+1
                if g[0] in G1:
                    for ne in G.successors(g[0]):
                        if ne in G2:
                            for ne1 in G2.successors(ne):
                                if ne1 in G:
                                    count = count+1
            if count > int(ReturnTh): #set threshold for the number of return paths
                print('merge:')
                print(str(ii) + " and " + str(jj))
                Gall = nx.compose(G1,G2)
                NODESS = list()    
                for (node1,node2,data) in Gall.edges(data=True):
                    temp=list()
                    temp.append(node1)
                    temp.append(node2)
                    if data['weight'] == 0:
                        temp.append('-')
                    elif data['weight'] == 1:
                        temp.append('+')
                    NODESS.append(temp)
                com_edges.append([group_num] + NODESS)            
                group_num = group_num+1
                
    pickle.dump(com_edges, open(path + "grouped_ext_Merged",'wb')) #Merged clusters 
    
    return
    
    
def makeDiGraphBase(mdldict):
    """
    This function converts the baseline model into a directed graph. 
    
    Parameters
    ----------
    mdldict : dict
        Baseline model dictionary 
        
    Returns
    -------
    G : DiGraph()
        Directed graph of the baseline model
    """    
    G = nx.DiGraph()
    G.clear()
    for key, values in mdldict.items():
        G.add_node(key)
        for value in values:
            G.add_edge(value, key)
    return G

def get_args():
    
    parser = argparse.ArgumentParser(description="Network model extension using ACCORDION")
    parser.add_argument('ReadingOutput', type=str,help="Reading output spreadsheet")
    parser.add_argument('Baseline', type=str,help="Baseline model in BioRECIPES format")
    parser.add_argument('Inflation', type=str,help="Inflation parameter for Markov clustering")
    parser.add_argument('ReturnTh', type=str,help="Return path threshold")
    parser.add_argument('out', type=str,help="Output directory")
    args = parser.parse_args()
    return(args)

def main():
    
    args = get_args()
    
    t0 = time.time()
    #Reading output .csv file. File format(RegulatedName,RegulatedID,RegulatedType,RegulatorName,RegulatorID,RegulatorType,PaperID)
    interaction_filename = args.ReadingOutput
    
    #Baseline model
    model_dict, regulators = get_model(args.Baseline)
    
    #use parseExtension if Reading output format is (RegulatedName,RegulatedID,RegulatedType,RegulatorName,RegulatorID,RegulatorType,PaperID) 
    exttt=parseExtension(model_dict, interaction_filename) 
    
    res,new_base_model = runMarkovCluster(args.out,exttt,model_dict,args.Inflation) # try 1.5,2,4,6
    
    merge_clusters(regulators, args.out, args.ReturnTh)
    
    t1 = time.time()
    total = t1-t0
    print("time to run ACCORDION in seconds: " + str(total))
    
#==============================================================================
#     clusterFile = args.out+"cluster"
#     
#     
#     for e in res:
#         fill = clusterFile+str(e[0])
#         output_stream = open(fill, 'w')
#         for ee in e[1:]:
#             if ee[1] == ee[0]:continue
#             output_stream.write(ee[0]+' '+ee[1]+' '+ee[2]+'\n')
#         output_stream.close()
#         
#     for e in res:    
#         ext_model = args.out + "ExtendedModel" + str(e[0]) + ".xlsx"    
#         extend_model(args.Baseline,e,ext_model)
#         
#     # Merge clusters if there is one or more return paths 
#     
#     G = nx.DiGraph()
#     G = makeDiGraphBase(regulators)
#     com_edges = list()
#     group_num = 1
#     extensions = pickle.load(open(args.out+"grouped_ext",'rb'))
#     
#     
#     for ii in range(0,len(extensions)):
#         for jj in range(ii+1,len(extensions)):
#             count = 0    
#             cluster1 = extensions[ii]
#             cluster2 = extensions[jj]
#             G1 = nx.DiGraph()
#             G2 = nx.DiGraph()
#             
#             for e in cluster1[1:]:
#                 if e[2] == '+':
#                     G1.add_edge(e[0], e[1],weight=1) 
#                 elif e[2] == '-':
#                     G1.add_edge(e[0], e[1],weight=0)
#                     
#             for e in cluster2[1:]:
#                 if e[2] == '+':
#                     G2.add_edge(e[0], e[1],weight=1) 
#                 elif e[2] == '-':
#                     G2.add_edge(e[0], e[1],weight=0) 
#                     
#             Gall = nx.compose(G1,G2) 
#             
#             for g in G.edges:
#                 if g[0] in G1:
#                     for ne in G.successors(g[1]):
#                         if ne in G2:
#                             for ne1 in G2.successors(ne):
#                                 if ne1 in G:
#                                     count = count+1
#                 if g[0] in G1:
#                     for ne in G.successors(g[0]):
#                         if ne in G2:
#                             for ne1 in G2.successors(ne):
#                                 if ne1 in G:
#                                     count = count+1
#                                
#                                     
#             if count > args.ReturnTh: #set threshold for the number of return paths
#                 print('merge:')
#                 print(str(ii)+" and "+str(jj))
#                 Gall = nx.compose(G1,G2)
#                 NODESS = list()    
#                 
#                 for (node1,node2,data) in Gall.edges(data=True):
#                     temp = list()
#                     temp.append(node1)
#                     temp.append(node2)
#                     
#                     if data['weight'] == 0:
#                         temp.append('-')
#                     elif data['weight'] == 1:
#                         temp.append('+')
#                         
#                     NODESS.append(temp)
#                 com_edges.append([group_num]+NODESS)            
#                 group_num = group_num+1
#                 
#                 
#     pickle.dump(com_edges, open(args.out + "grouped_ext_Merged",'wb'))
# 
#==============================================================================
if __name__ == '__main__':
    main()
    