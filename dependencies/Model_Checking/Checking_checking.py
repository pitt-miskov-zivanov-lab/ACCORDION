# From Checking/checking.py of DySE Framwork Repo
# See details at https://github.com/orgs/pitt-miskov-zivanov-lab/repositories (find the repo named DySE)

import numpy as np
import re


def get_runs(checking_output_file) -> int:
    """Read number of samples (runs) from model checking output file
    """

    with open(checking_output_file, 'r') as p_file:
        content = p_file.readlines()
        for line in content:
            match = re.search(r'samples = ([0-9]+)', line)
            if match:
                return int(match.group(1))


def get_estimate(checking_output_file) -> float:
	""" Read probability estimate from model checking output file
	"""

	with open(checking_output_file, 'r') as p_file:
		content = p_file.readlines()
		for line in content:
			match = re.search(r'estimate = ([0-9]+\.[0-9]+)', line)
			if match:
				return float(match.group(1))


def create_test(
        coverage=0.7,
        test='BEST',
        delta=0.05,
        alpha=1,
        beta=1):
    """Create test parameter file for model checking

        test: 'BEST' for bayesian estimation
    """

    test_string = '{} {} {} {} {}'.format(test, delta, coverage, alpha, beta)

    return test_string



def create_property(
        variables: list(),
        values: list(),
        timesteps: list(),
        functions=None,
        holds=None,
        ranges=None,
        joins=None,
        timing=None,
        variable_joins=None):
    """Create a property in LTL notation from specified values and timesteps

        Inputs:
            variables : list of model variable (element) names for the property
            (remaining inputs are nested lists, where each item corresponds to each variable)
            values : lists of values of each variable to use in defining property conditions
            timesteps : lists of timesteps corresponding to values for each variable
            functions : lists of comparison operators {==,<,>,<=,>=} for values for each variable
            holds : lists of time intervals that values must hold
            ranges : lists of step ranges around corresponding timesteps (timestep +/- range for each value)
            joins : lists of logic functions {'AND','OR'} to join conditions for each variable
            timing : list of timing method to use for each variable {'relative','absolute'}
                if absolute, includes step variable in the property to check for conditions
                within 'ranges' of specified time steps
            variable_joins : for multiple variables, list of logic functions {'AND','OR'} to join conditions
        Outputs:
            property string in BLTL notation
    """

    if timing is None:
        timing = ['absolute' for x in variables]
    else:
        if len(timing) != len(variables):
            raise ValueError('Length of timing list must equal variables')

    if variable_joins is None:
        if len(variables) > 1:
            variable_joins = ['AND' for x in variables[1:]]
        else:
            variable_joins = ['AND']
    else:
        if len(variable_joins) != len(variables) - 1:
            raise ValueError('Length of variable_joins list must equal len(variables) - 1')

    for idx, this_var in enumerate(variables):

        var_values = values[idx]
        var_timesteps = timesteps[idx]

        # fill default values
        if functions is None:
            var_funcs = ['==' for x in var_values]
        else:
            var_funcs = functions[idx]
            for func in var_funcs:
                if func not in ['==', '<', '>', '<=', '>=']:
                    raise ValueError(('Invalid function ({}) for variable {}, '
                            'must be in {==,<,>,<=,>=}').format(func, this_var))

        if holds is None:
            var_holds = [1 for x in var_values]
        else:
            var_holds = holds[idx]

        if ranges is None:
            var_ranges = [0 for x in var_values]
        else:
            var_ranges = ranges[idx]

        # check that lengths of lists all match
        # (already checked values and timesteps)
        if not (len(var_values) == len(var_timesteps) == len(var_funcs) == len(var_holds) == len(var_ranges)):
            raise ValueError('Number of values, timesteps, '
                            'functions, holds, and ranges must be equal')

        # set join logic operator
        if joins is None:
            var_join = ['AND' for x in var_values[1:]]
        else:
            var_join = joins[idx]

        if len(var_join) != len(var_values) - 1:
            raise ValueError('Length of joins must be number of values - 1 for variable {}'.format(this_var))
        ops = [0 for x in var_join]
        for join_idx, this_join in enumerate(var_join):
            if this_join is 'AND':
                ops[join_idx] = '&'
            elif this_join is 'OR':
                ops[join_idx] = '|'
            else:
                raise ValueError('Invalid join operator for variable {}, must be AND or OR'.format(this_var))

        # create intervals from given timesteps
        intervals = [var_timesteps[0]] + list(np.diff(var_timesteps))

        # add ranges to each interval
        intervals = np.array(intervals) + np.array(var_ranges)


        if idx > 0:
            if variable_joins[idx-1] is 'AND':
                property_string += ' & '
            elif variable_joins[idx-1] is 'OR':
                property_string += ' | '
            else:
                raise ValueError('Invalid variable join operator, must be AND or OR')
        else:
            property_string = ''


        this_var_idx = 0

        property_string += 'F[{}](G[{}]({}{}{}'.format(
                intervals[this_var_idx], var_holds[this_var_idx], this_var,
                var_funcs[this_var_idx], var_values[this_var_idx])

        if timing[idx] == 'absolute':
            # include step ranges
            property_string += '&step>={}&step<={}'.format(
                    var_timesteps[this_var_idx]-var_ranges[this_var_idx],
                    var_timesteps[this_var_idx]+var_ranges[this_var_idx])

        property_string += ')'
        close_parens = 1

        for this_var_idx in range(1, len(var_values)):
            property_string += ' {} F[{}](G[{}]({}{}{}'.format(
                    ops[this_var_idx-1], intervals[this_var_idx],
                    var_holds[this_var_idx], this_var,
                    var_funcs[this_var_idx], var_values[this_var_idx])

            if timing[idx] == 'absolute':
                # include step ranges
                property_string += '&step>={}&step<={}'.format(
                    var_timesteps[this_var_idx]-var_ranges[this_var_idx],
                    var_timesteps[this_var_idx]+var_ranges[this_var_idx])

            property_string += ')'
            close_parens += 1

        property_string += ')' * close_parens

    return property_string
