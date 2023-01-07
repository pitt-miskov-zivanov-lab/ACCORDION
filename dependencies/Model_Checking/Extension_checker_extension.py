# From Extension/checker_extension.py of DySE Framwork repo
# See details at https://github.com/orgs/pitt-miskov-zivanov-lab/repositories (find the repo named DySE)

import os
import multiprocessing
from joblib import Parallel, delayed
from collections import defaultdict
import subprocess
import logging
import glob

import Extension_extension_util as eu
from Checking_checking import get_estimate

# TODO: restructure to separate extension from checker functions

def parallel_model_checker_extension(init_model, extensions, output_path,
	test_, property_, threshold, framework_path, scenario='0', normalize=False,
	steps=1000):

	# check whether original model satisfies properties
	# TODO: add an initial_estimate keyword input to allow skipping this
	# TODO: call nested scenario checker or check unit depending on property format

	curr_estimate = check_unit(test_, property_, init_model, [0,], output_path,
		framework_path, scenario, normalize, steps)

	logging.info(('Initial estimate: %s ') % (str(curr_estimate)))

	# parallelize extension and checking using each extension group
	gen = (ext for ext in extensions)
	num_cores = multiprocessing.cpu_count()

	# TODO: call nested scenario checker or check unit depending on property format
	Parallel(n_jobs=num_cores,verbose=50)(
		delayed(check_unit)(
			test_, property_, init_model, ext, output_path,
			framework_path, scenario, normalize, steps
			)
		for ext in gen)

	# get estimate for each extended model
	# TODO: use estimate returned by check_unit and use an accumulator
	ext_to_estimate = dict()
	for ext in extensions:
		checking_output = output_path+'~temp_estimate_'+str(ext[0])+'.txt'
		ext_to_estimate[ext[0]] = get_estimate(checking_output)

	msg = ('Estimates for each extension group : \n'
		+ '\n'.join([
			str(key)+' : '+str(ext_to_estimate[key])
			for key in ext_to_estimate
			])
		+ '\n\n')
	logging.info(msg)

	# collect all models that satisfied properties with estimates above the threshold
	all_passing_idx = [x for x in ext_to_estimate if ext_to_estimate[x] > threshold]
	msg = ('Model indices with estimates above threshold: \n'
		+ '\n'.join([
			str(key)+' : '+str(ext_to_estimate[key])
			for key in all_passing_idx
			])
		+ '\n\n')
	logging.info(msg)

	# rename all models with estimates above the threshold
	for pass_idx in all_passing_idx:
		ext_model = output_path + '~temp_final_' + str(pass_idx) + '.xlsx'
		out_model = output_path + 'final_' + str(pass_idx) + '.xlsx'
		os.system('mv '+ext_model+' '+out_model)

		# TODO: rename and save traces too? need to glob multiple trace files
		# ext_trace = output_path + '~temp_trace_' + str(pass_idx) + '.txt'
		# out_trace = output_path + 'trace_' + str(pass_idx) + '.txt'
		# os.system('mv '+ext_trace+' '+out_trace)

	# get the model with the highest estimate
	max_idx = max(ext_to_estimate, key=ext_to_estimate.get)
	if ext_to_estimate[max_idx] > curr_estimate:
		# TODO: rename this model as the "best" model?
		best_estimate = ext_to_estimate[max_idx]
		msg = ('Highest scoring extension group '+str(max_idx)+'.\n'
			+ 'Edges are: \n'
			+ ' '.join([str(ele) for ele in extensions[max_idx-1][1:]])
			+ '\n\n')
	else:
		best_estimate = curr_estimate
		msg = 'Original model had highest probability of satisfying properties'

	logging.info(msg)

	logging.info(('Highest Estimate : %s') % (str(best_estimate)))

	return ext_to_estimate

def nested_scenario_checker(init_model, extensions, output_path,
    test_, property_, threshold, framework_path, scenario='0', normalize=False,
	steps=1000):
	"""Call model checker for each scenario using properties in nested folders.

	Note that with separate property files, properties could be satisfied at different
	simulation steps in different scenarios.
	"""

	scenarios_input = scenario.split(',')

	# match up property files with scenarios
	if normalize:
		first_scenario = scenarios_input[0]
		scenarios = [','.join([first_scenario,scen]) for scen in scenarios_input][1:]
	else:
		scenarios = scenarios_input

	if os.path.isdir(property_):
		properties = sorted(glob.glob(property_+'/*'))
	else:
		properties = property_.split(',')

	if len(scenarios) != len(properties):
		raise ValueError(('Number of scenarios and properties does not match: '
			'%d scenarios, %d properties') % (len(scenarios),len(properties)))

	# get estimates for all scenarios and their corresponding properties
	estimates = []
	for idx,this_scenario in enumerate(scenarios):

		scenario_prop = properties[idx]

		if os.path.isdir(scenario_prop):
			prop = sorted(glob.glob(scenario_prop+'/*'))
		else:
			prop = [scenario_prop]

		for this_prop in prop:
			this_estimate = check_unit(
				test_, this_prop, init_model, extensions,
				output_path, framework_path, this_scenario,
				normalize, steps
				)
			estimates.append(this_estimate)

			logging.info(
				('Scenario: %s \n Property: %s \n Estimate: %0.6f \n') % (this_scenario, this_prop, this_estimate))

	return estimates


def check_unit(test_, property_, model_, extensions, output_path, framework_path,
	scenario='0', normalize=False, steps=1000):
	""" Generate temporary trace, estimate, and model files and call model checker
	"""

	ext_index = str(extensions[0])
	trace_ = output_path + "~temp_trace_" + ext_index + ".txt"
	estimate_ = output_path + "~temp_estimate_" + ext_index + ".txt"
	ext_model = output_path + "~temp_final_" + ext_index + ".xlsx"

	eu.extend_model(model_, extensions, ext_model)

	estimate = call_checker(test_, property_, ext_model, trace_, estimate_,
		framework_path, scenario, normalize, steps)

	return estimate


def call_checker(test_, property_, model_, trace_, estimate_,
	framework_path, scenario='0', normalize=False, steps=1000) -> float:
	""" Call model checker and return probability estimate
	"""

	# navigate to framework directory but keep path to starting directory
	start_dir = os.getcwd()
	framework_dir = os.path.join(start_dir,framework_path)
	rel_input_path = os.path.relpath(start_dir,framework_path)
	os.chdir(framework_dir)

	# convert arguments to strings for dishwrap call
	if normalize:
		normalize_str = '1'
	else:
		normalize_str = '0'
	steps_str = str(steps)
	scenario_str = str(scenario)

	# create file paths
	# add quotes around file paths to handle spaces in file names
	# for the call to dishwrap/checker
	# NOTE: not replacing spaces with '\ ' to keep this platform agnostic
	property_path_str = '\"' + os.path.join(rel_input_path,property_) + '\"'
	model_path_str = '\"' + os.path.join(rel_input_path,model_) + '\"'
	trace_path_str = '\"' + os.path.join(rel_input_path,trace_) + '\"'

	# TODO: check dishwrap to see why quotes won't work with the test file
	test_path_str = os.path.join(rel_input_path,test_)

	# executable paths
	dishwrap_path_str = os.path.join('dishwrap_v1.0','dishwrap','dishwrap')
	checker_path_str = os.path.join('dishwrap_v1.0','monitor','checker')
	simulator_path_str = os.path.join('Simulation_Simulator_Python_simulator_interface.py')

	# call checker and pipe output to txt file
	checker_output_file = open(os.path.join(rel_input_path,estimate_), 'w')
	p = subprocess.Popen([dishwrap_path_str,
			test_path_str,
			checker_path_str,
			property_path_str,
			simulator_path_str,
			model_path_str,
			trace_path_str,
			scenario_str,
			normalize_str,
			steps_str],
			stdout=checker_output_file,
			stderr=subprocess.PIPE,
			universal_newlines=True)

	p.wait()

	if p.returncode != 0:
		error = p.communicate()[1]
		os.chdir(start_dir)
		raise ValueError(
			'Error in model checker: Return Code ' + str(p.returncode) + '\n'
			+ str(error))

	# return to original directory
	os.chdir(start_dir)
	# read estimate from checker output
	estimate = get_estimate(estimate_)

	return estimate
