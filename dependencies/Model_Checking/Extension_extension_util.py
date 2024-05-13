# From Extension/extension_util.py of DySE Framwork repo
# See details at https://github.com/orgs/pitt-miskov-zivanov-lab/repositories (find the repo named DySE)

import os
import openpyxl
import pandas as pd
import Simulation_Simulator_Python_simulator as sim
from Translation_model import get_model, model_to_dict, model_from_dict, model_to_excel


def extend_unit(mdl,edges,simRun,simLen,outPath,scenario):
	""" Generate temp trace and extended model files, run a simulation
	"""

	trace = outPath+"~temp_trace_"+str(edges[0])+".txt"
	ext_model = outPath + "~temp_final_" + str(edges[0]) + ".xlsx"
	extend_model(mdl,edges,ext_model)

	model = sim.Simulator(ext_model)
	model.run_simulation('ra',simRun,simLen,trace,scenario=scenario,outMode=3)


def extend_model(mdl,edges,ext_model,init_method='1'):
	""" Extend a copy of the original model by adding edges
	"""

	# TODO: return dataframe
	# TODO: convert model to dict of similar form to extensions?
	os.system('cp '+mdl+' '+ext_model)

	model = get_model(mdl)
	num_elements = model.shape[0]
	model_dict = model_to_dict(model)

	index_col = '#'
	var_name_col = 'Variable'
	pos_reg_col = 'Positive'
	neg_reg_col = 'Negative'
	ele_name_col = 'Element Name'
	ele_id_col = 'Element IDs'
	for key,item in model_dict.items():
		# TODO: check for mismatched scenarios in model dict?
		input_col_initial = [
				x.strip() for x in item
				if ('initial' in x.lower() or 'scenario' in x.lower())
				]

	# will add a new index number for all new elements
	new_element_num = num_elements+1

	# FIXME: check get_regulation_init option
	for e in edges[1:]:
		# add any new elements and set required values
		# TODO: other attributes
		if e[0] not in model_dict:
			if init_method == 'regulation':
				model_dict[e[0]] = {
					init : get_regulation_init(
							model_dict, e[0], pos_reg_col, neg_reg_col, init
							)
					for init in input_col_initial
					}
			else:
				model_dict[e[0]] = {init : 1 for init in input_col_initial}
			model_dict[e[0]][index_col] = new_element_num
			# default to using the variable name as the name and ID
			model_dict[e[0]][ele_name_col] = e[0]
			model_dict[e[0]][ele_id_col] = e[0]
			new_element_num += 1

		if e[1] not in model_dict:
			if init_method == 'regulation':
				model_dict[e[1]] = {
					init : get_regulation_init(
							model_dict,e[1],pos_reg_col,neg_reg_col,init
							)
					for init in input_col_initial
					}
			else:
				model_dict[e[1]] = {init : 1 for init in input_col_initial}
			model_dict[e[1]][index_col] = new_element_num
			# default to using the variable name as the name and ID
			model_dict[e[1]][ele_name_col] = e[1]
			model_dict[e[1]][ele_id_col] = e[1]
			new_element_num += 1

		# TODO: use '!' notation here
		reg_col = pos_reg_col if e[2] in [
				'+','increases','NOT decreases'
				] else neg_reg_col
		if (model_dict[e[1]].get(reg_col) is None
				or model_dict[e[1]].get(reg_col) == ''
				):
			model_dict[e[1]][reg_col] = e[0]
		else:
			# TODO: choose function to add edge here
			model_dict[e[1]][reg_col] += (','+e[0])

	# convert back to dataframe to write to excel
	df_model = model_from_dict(model_dict)
	model_to_excel(df_model,ext_model)


def get_regulation_init(model_dict,this_element,pos_reg_col,neg_reg_col,scenario_col_name):
	"""Calculate the intial value of an element based on the activity of its regulators
	"""

	sum_pos = 0
	sum_neg = 0

	# check for positive regulators
	pos_reg_list = model_dict[this_element][pos_reg_col].split(',')
	if pos_reg_list != '':
		# sum initial values of the element's regulators
		for pos_reg in pos_reg_list:
			sum_pos += model_dict[pos_reg][scenario_col_name]

	# check for negative regulators
	neg_reg_list = model_dict[this_element][neg_reg_col].split(',')
	if neg_reg_list != '':
		for neg_reg in neg_reg_list:
			sum_neg += model_dict[neg_reg][scenario_col_name]

	if sum_pos != 0 :
		sum_pos = sum_pos/sum_pos
	if sum_neg != 0 :
		sum_neg = sum_neg/sum_neg

	return 1 - sum_pos + sum_neg
	
