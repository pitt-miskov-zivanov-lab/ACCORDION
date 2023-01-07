# Model Checking

## Description of files

- `dishwrap`
  - a wrapper to call the DiSH simulator and model checking

## Usage

- `dishwrap`
~~~
Usage: dishwrap <testfile> <checker> <property> <simulator> <modelfile> <trace> [<scenarios>] [<normalize>] [<steps>]

where:
      <testfile> is a sequence of test specifications;
      <checker> is the path to the trace checker executable;
      <property> is the file name of the BLTL property to check;
      <simulator> is the path to simulator_interface.py;
      <modelfile> is the file name of the model in DySE format;
      <trace> is the name of the trace file computed by the simulator;
      <scenarios> indicates the initial values to use
         input two comma-separated values to calculate the difference
         (0 is the first initial values column in modelfile);
      <normalize> {0,1} is whether to normalize scenarios to the first scenario input
      <steps> is the number of simulation steps
Available test specifications:

Hypothesis test:
 Lai's test: Lai <theta> <cost per sample>
 Bayes Factor test: BFT <theta> <threshold T> <alpha> <beta>
 Sequential Probability Ratio Test: SPRT <theta> <threshold T> <indifference region delta>
 Bayes Factor test with indifference region: BFTI <theta> <threshold T> <alpha> <beta> <indifference region delta>

Estimation methods:
 Chernoff-Hoeffding bound: CHB <delta> <coverage probability>
 Bayesian estimation: BEST <delta> <coverage probability> <alpha> <beta>

Empty lines and lines beginning with '#' are ignored.
~~~
