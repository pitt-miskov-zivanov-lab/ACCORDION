/***********************************************************************************************
 *
 *
 *
 * Statistical tests in this software are copied from bnwrap, 
 * copyright (C) 2010, 2011, 2012 Paolo Zuliani and Edmund M. Clarke.  All rights reserved.
 * By using this software the USER indicates that he or she has read, understood and will comply
 * with the following:
 *
 * 1. The USER is hereby granted non-exclusive permission to use, copy and/or
 * modify this software for internal, non-commercial, research purposes only. Any
 * distribution, including commercial sale or license, of this software, copies of
 * the software, its associated documentation and/or modifications of either is
 * strictly prohibited without the prior consent of the authors. Title to copyright
 * to this software and its associated documentation shall at all times remain with
 * the authors. Appropriated copyright notice shall be placed on all software
 * copies, and a complete copy of this notice shall be included in all copies of
 * the associated documentation. No right is granted to use in advertising,
 * publicity or otherwise any trademark, service mark, or the name of the authors.
 *
 * 2. This software and any associated documentation is provided "as is".
 *
 * THE AUTHORS MAKE NO REPRESENTATIONS OR WARRANTIES, EXPRESSED OR IMPLIED,
 * INCLUDING THOSE OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, OR THAT
 * USE OF THE SOFTWARE, MODIFICATIONS, OR ASSOCIATED DOCUMENTATION WILL NOT
 * INFRINGE ANY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER INTELLECTUAL PROPERTY
 * RIGHTS OF A THIRD PARTY.
 *
 * The authors shall not be liable under any circumstances for any direct,
 * indirect, special, incidental, or consequential damages with respect to any
 * claim by USER or any third party on account of or arising from the use, or
 * inability to use, this software or its associated documentation, even if the
 * authors have been advised of the possibility of those damages.
 * ***********************************************************************************************/


#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <algorithm>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <gsl/gsl_cdf.h>
#include <gsl/gsl_rng.h>
#include <numeric>
#include <sys/types.h>
#include <sys/wait.h>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <ctime>
#include <typeinfo>

#define EXIT_SUCCESS_SAT    51
#define EXIT_SUCCESS_UNSAT  52

using namespace std;

// base class for every statistical test
class Test {
protected:

  string args;
  unsigned int out;			// current result of the test
  unsigned long int samples, successes;	// number of samples, successes

public:

  static const unsigned int NOTDONE = 0;
  static const unsigned int DONE = 1;

  // no default constructor
  Test(string v) {
    args = v;
    out = NOTDONE;
    samples = 0;
    successes = 0;
  }

  virtual void init () =0;

  bool done () {
    return (out != NOTDONE);
  }

  virtual void doTest(unsigned long int n, unsigned long int x) = 0;

  virtual void printResult() = 0;

};


// class for hypothesis tests
class HTest : public Test {
protected:
  double theta;			// threshold
				// Null hypothesis is (theta, 1)

public:

  static const unsigned int NULLHYP = 2;
  static const unsigned int ALTHYP  = 1;

  HTest(string v): Test(v) {
  }

  void printResult () {

    switch (out) {
      // print only when the test is finished
      case NOTDONE:
        cerr << "Test.printResult() : test not completed: " << args << endl; 
        exit(EXIT_FAILURE); 
      case NULLHYP:
        cout << args << ": " << "Accept Null hypothesis"; break;
      case ALTHYP: 
        cout << args << ": " << "Reject Null hypothesis"; break;
    }
    cout << ", successes = " << successes << ", samples = " << samples << endl;
  }
};


// base class for statistical estimation
class Estim : public Test {
protected:
  double delta;			// half-interval width
  double c;			// coverage probability
  double estimate;		// the estimate

public:

  Estim(string v) : Test(v){
  }

  // defined later because it uses a method from class CHB
  void printResult ();

};



// Chernoff-Hoeffding bound
class CHB : public Estim {
private:
  unsigned long int N;		// the bound

public:
  CHB(string v) : Estim(v){
    N = 0;
  }

  unsigned long int get_CH_bound() {
    if (N == 0) {
      cerr << "N has not been set" << endl;
      exit(EXIT_FAILURE);
    }
    return N;
  }

  void init() {
    string testName;

    // convert test arguments from string to float
    istringstream inputString(args);
    inputString >> testName >> delta >> c;			// by default >> skips whitespaces

    // sanity checks
    if ((delta >= 0.5) || (delta <= 0.0)) {
      cerr << args << " : must have 0 < delta < 0.5" << endl; 
      exit(EXIT_FAILURE);
    }

    if (c <= 0.0) {
      cerr << args << " : must have c > 0" << endl; 
      exit(EXIT_FAILURE);
    }

    // compute the Chernoff-Hoeffding bound
    N = int (ceil (1/(2*pow(delta, 2)) * log(1/(1-c))));

    // writes back the test arguments, with proper formatting
    ostringstream tmp;
    tmp << testName << " " << delta << " " << c;
    args = tmp.str();
  }

  void doTest (unsigned long int n, unsigned long int x) {

    // a multi-threaded program will overshoot the bound
    if (n >= N) {
      out = DONE;
      samples = n;
      successes = x;
      estimate = double (x)/ double(n);
    }
  }
};


// print the results of an estimation object
void Estim::printResult (){

    // platform-dependent stuff
    string Iam = typeid(*this).name(); 

    // print only when the test is finished
    switch (out) {
      case NOTDONE:
        cerr << "Estim.printResult() : test not completed: " << args << endl; 
        exit(EXIT_FAILURE); 
      case DONE:
        cout << args << ": estimate = " << estimate <<  ", successes = " << successes 
		<< ", samples = " << samples;

	// if called by a CHB object, print the sample size 
	// of the Chernoff-Hoeffding bound, as well
	if (Iam.find("CHB",0) != string::npos) {
	  cout << ", C-H bound = " << dynamic_cast<CHB*>(this)->get_CH_bound();
	}
	cout << endl; break;
    }
};


// Bayesian Interval Estimation with Beta prior
//
// Zuliani, Platzer, Clarke. HSCC 2010.
//
//
class BayesEstim : public Estim {
private:
  double alpha, beta;		// Beta prior parameters

public:
  BayesEstim(string v): Estim(v) {
  }

  void init() {
    string testName;

    // convert test arguments from string to float
    istringstream inputString(args);
    inputString >> testName >> delta >> c >> alpha >> beta;	// by default >> skips whitespaces

    // sanity checks
    if ((delta > 0.5) || (delta <= 0.0)) {
      cerr << args << " : must have 0 < delta < 0.5" << endl; 
      exit(EXIT_FAILURE);
    }

    if (c <= 0.0) {
      cerr << args << " : must have c > 0" << endl; 
      exit(EXIT_FAILURE);
    }

    if ((alpha <= 0.0) || (beta <= 0.0)) {
      cerr << args << " : must have alpha, beta > 0" << endl; 
      exit(EXIT_FAILURE);
    }
    
    // writes back the test arguments, with proper formatting
    ostringstream tmp;
    tmp << testName << " " << delta << " " << c << " " << alpha << " " << beta;
    args = tmp.str();
  }

  void doTest (unsigned long int n, unsigned long int x) {

    double t0, t1;		// interval bounds
    double postmean;		// posterior mean
    double coverage;		// computed coverage
    double a, b;

    // compute posterior mean
    a = double(x) + alpha; b = double(n + alpha + beta);
    postmean = a / b;

    // compute the boundaries of the interval
    t0 = postmean - delta; t1 = postmean + delta;
    if (t1 > 1) { t1 = 1; t0 = 1 - 2*delta;};
    if (t0 < 0) { t1 = 2*delta; t0 = 0;};

    // compute posterior probability of the interval
    coverage = gsl_cdf_beta_P (t1, a, b - a) - gsl_cdf_beta_P (t0, a, b - a);

    // check if done
    if (coverage >= c) {
      out = DONE;
      estimate = postmean;
      samples = n;
      successes = x;
    }
  }
};



//  Lai's test
//
//  Tze Leung Lai
//  "Nearly Optimal Sequential Tests of Composite Hypotheses"
//  The Annals of Statistics
//  1988, 16(2): 856-886
// 
// 
//  Inputs
//  theta: probability threshold - must satisfy 0 < theta < 1
//  c    : cost per observation
//  n    : number of samples
//  x    : number of successful samples. It must be  x <= n
// 
// 
//  The Null hypothesis H_0 is the interval [theta, 1]
//
//  Output
//  out : NOTDONE more samples needed
//        ALTHYP is the hypothesis [0, theta]
//        NULLHYP is the hypothesis [theta, 1]
//
// 

class Lai : public HTest {
private:
  double cpo;			  // cost per observation

  gsl_rng * r;			  // pseudo-random number generator
  double pi;			  // 3.14159

public:
  Lai (string v) : HTest(v) {
  }

  void init () {
    string testName;

    // convert test arguments from string to float
    istringstream inputString(args);
    inputString >> testName >> theta >> cpo;			// by default >> skips whitespaces

    // sanity checks
    if ((theta >= 1.0) || (theta <= 0.0)) {
      cerr << args << " : must have 0 < theta < 1" << endl; 
      exit(EXIT_FAILURE);
    } 

    if (cpo <= 0.0) {
      cerr << args << " : must have cost > 0" << endl; 
      exit(EXIT_FAILURE);
    }

    // initialize pseudo-random number generator
    r = gsl_rng_alloc (gsl_rng_mt19937);
    srand(time(NULL));                    
    gsl_rng_set (r, rand());

    pi = atan(1)*4;
    
    // writes back the test arguments, with proper formatting
    ostringstream tmp;
    tmp << testName << " " << theta << " " << cpo;
    args = tmp.str();
  }

  void doTest (unsigned long int n, unsigned long int x) {

    double maxle = double(x)/n;		// max likelihood estimate
    double T, t;
    double KL;				// Kullback-Leibler information number
    double g, w;

    // compute the Kullback-Leibler information number
    if (maxle == 0.0) 
      KL = log(1/(1-theta)); 
    else if (maxle == 1.0) 
      KL = log(1/theta); 
    else 
      KL = maxle * log(maxle/theta) + (1 - maxle) * log( (1-maxle)/(1-theta) );

    // compute function g and the threshold
    t = cpo*n;
    if (t >= 0.8) { 
        w = 1/t; 
        g = (1/(16*pi))*(pow(w,2) - (10/(48*pi))*pow(w,4) + pow(5/(48*pi), 2)*pow(w,6));
    } else if ((0.1 <= t) && (t < 0.8))
	g = (exp(-1.38*t-2))/(2*t);
    else if ((0.01 <= t) && (t < 0.1)) 
	g = (0.1521 + 0.000225/t - 0.00585/sqrt(t))/(2*t);
    else  w = 1/t; g = 0.5*(2*log(w) + log(log(w)) - log(4*pi) - 3*exp(-0.016*sqrt(w)));

    T = g/n;

    // check if we are done
    if (KL >= T) {
      samples = n;
      successes = x;

      // decide which hypothesis to accept
      if (maxle == theta)
          if (gsl_rng_uniform (r) <= 0.5) out = NULLHYP; 
	  else out = ALTHYP;
      else if (maxle > theta) out = NULLHYP; else out = ALTHYP;
    }
  }
};


// The Bayes Factor Test with Beta prior
// 
//  It computes the Bayes Factor P(data|H_0)/P(data|H_1) and returns
//  whether it is greater/smaller than a specified threshold value or not.
// 
//  Inputs
//  theta: probability threshold - must satisfy 0 < theta < 1
//  T    : ratio threshold satisfying T > 1
//  n    : number of samples
//  x    : number of successful samples. It must be  x <= n
//  alpha: Beta prior parameter
//  beta : Beta prior parameter
//  podds: prior odds ratio ( = P(H_1)/P(H_0) )
//
//  The Null hypothesis H_0 is the interval [theta, 1]
//
//  Output
//  out : NOTDONE more samples needed
//        ALTHYP is the hypothesis [0, theta]
//        NULLHYP is the hypothesis [theta, 1]
//
  
class BFT : public HTest {
private:
  double T;			// ratio threshold
  double podds;			// prior odds 
  double alpha, beta;		// Beta prior parameters
	
public:
  BFT (string v) : HTest(v) {
  }

  void init () {	// initialize test parameters

    double p0, p1;		// prior probabilities	
    string testName;

    // convert test arguments from string to double
    istringstream inputString(args);
    inputString >> testName >> theta >> T >> alpha >> beta;		// by default >> skips whitespaces

    // sanity checks
    if (T <= 1.0) {
      cerr << args << " : must have T > 1" << endl; 
      exit(EXIT_FAILURE);
    }

    if ((theta >= 1.0) || (theta <= 0.0)) {
      cerr << args << " : must have 0 < theta < 1" << endl; 
      exit(EXIT_FAILURE);
    } 

    if ((alpha <= 0.0) || (beta <= 0.0)) {
      cerr << args << " : must have alpha, beta > 0" << endl; 
      exit(EXIT_FAILURE);
    }

    // compute prior probability of the alternative hypothesis
    p1 = gsl_cdf_beta_P (theta, alpha, beta);

    // sanity check
    if ((p1 >= 1.0) || (p1 <= 0.0)) {
      cerr << args << " : Prob(H_1) is either 0 or 1" << endl; 
      exit(EXIT_FAILURE);
    }
    p0 = 1 - p1;

    // compute prior odds
    podds = p1 / p0; 

    // writes back the test arguments, with proper formatting
    ostringstream tmp;
    tmp << testName << " " << theta << " " << T << " " << alpha << " " << beta;
    args = tmp.str();
  }


  void doTest (unsigned long int n, unsigned long int x) {

    double B;

    // compute Bayes Factor
    B = podds * (1/gsl_cdf_beta_P(theta, x+alpha, n-x+beta) - 1);

    // compare and, if done, set
    if (B > T) {out = NULLHYP; samples = n; successes = x;}
    else if (B < 1/T) {out = ALTHYP; samples = n; successes = x;}

  }
};


// The Bayes Factor Test with Beta prior and indifference region
//
// It computes the Bayes Factor P(data|H_0)/P(data|H_1) and returns
// whether it is greater/smaller than a specified threshold value or not.
// 
//  Inputs
//  theta1: probability threshold - must satisfy 0 < theta1 < theta2 < 1
//  theta2: probability threshold
//  T    : ratio threshold satisfying T > 1
//  n    : number of samples
//  x    : number of successful samples. It must be  x <= n
//  alpha: Beta prior parameter
//  beta : Beta prior parameter
//  podds: prior odds ratio ( = P(H_1)/P(H_0) )
// 
//  The Null hypothesis H_0 is the interval [theta2, 1]
//
//  Output
//  out : NOTDONE more samples needed
//        ALTHYP is the hypothesis [0, theta1]
//        NULLHYP is the hypothesis [theta2, 1]
// 
//
 
class BFTI : public HTest {
private:
  double T;			// ratio threshold
  double podds;			// prior odds 
  double alpha, beta;		// Beta prior parameters
  double delta;			// half indifference region
  double theta1, theta2;	// theta1 < theta2 (indifference region)
	
public:
  BFTI (string v) : HTest(v) {
  }

  void init () {		// initialize test parameters

    double p0, p1;		// prior probabilities	
    string testName;

    // convert test arguments from string to float
    istringstream inputString(args);
    inputString >> testName >> theta >> T >> alpha >> beta >> delta;	// by default >> skips whitespaces

    // sanity checks
    if (T <= 1.0) {
      cerr << args << " : must have T > 1" << endl; 
      exit(EXIT_FAILURE);
    }

    if ((theta >= 1.0) || (theta <= 0.0)) {
      cerr << args << " : must have 0 < theta < 1" << endl; 
      exit(EXIT_FAILURE);
    } 

    if ((alpha <= 0.0) || (beta <= 0.0)) {
      cerr << args << " : must have alpha, beta > 0" << endl; 
      exit(EXIT_FAILURE);
    }

    if ((delta >= 0.5) || (delta <= 0.0)) {
      cerr << args << " : must have 0 < delta < 0.5" << endl; 
      exit(EXIT_FAILURE);
    } 
    
    // prepare parameters
    theta1 = max(0.0, theta-delta);
    theta2 = min(1.0, theta+delta);

    // another sanity check
    if ((theta1 <= 0.0) || (theta2 >= 1.0)) {
      cerr << args << " : indifference region borders 0 or 1" << endl; 
      exit(EXIT_FAILURE);
    }

    // compute prior probability of the alternative hypothesis
    p1 = gsl_cdf_beta_P (theta1, alpha, beta);

    // sanity check
    if ((p1 >= 1.0) || (p1 <= 0.0)) {
      cerr << args << " : Prob(H_1) is either 0 or 1" << endl; 
      exit(EXIT_FAILURE);
    }
    p0 = 1 - p1;

    // compute prior odds
    podds = p1 / p0;
    
    // writes back the test arguments, with proper formatting
    ostringstream tmp;
    tmp << testName << " " << theta << " " << T << " " << alpha << " " << beta << " " << delta;
    args = tmp.str();
  }


  void doTest (unsigned long int n, unsigned long int x) {

    double B;

    // compute Bayes Factor
    B = podds * (1 - gsl_cdf_beta_P(theta2, x+alpha, n-x+beta)) / gsl_cdf_beta_P(theta1, x+alpha, n-x+beta);

    // compare and, if done, set
    if (B > T) {out = NULLHYP; samples = n; successes = x;}
    else if (B < 1/T) {out = ALTHYP; samples = n; successes = x;}

  }
};



// The Sequential Probability Ratio Test 
//
//  Inputs
//  theta1, theta2 : probability thresholds satisfying theta1 < theta2
//  T : ratio threshold satisfying T > 1
//  n : number of samples
//  x : number of successful samples. It must be  x <= n
// 
//  Output
//  out : NOTDONE more samples needed
//        ALTHYP is the hypothesis [0, theta1]
//        NULLHYP is the hypothesis [theta2, 1]

class SPRT : public HTest {
private:
  double delta;			// half indifference region
  double theta1, theta2;	// theta1 < theta2 (indifference region)
  double T;			// ratio threshold
	
public:
  SPRT (string v) : HTest(v) {
  }

  void init () {		// initialize test parameters

    string testName;

    // convert test arguments from string to float
    istringstream inputString(args);
    inputString >> testName >> theta >> T >> delta;		// by default >> skips whitespaces

    // sanity checks
    if (T <= 1.0) {
      cerr << args << " : must have T > 1" << endl; 
      exit(EXIT_FAILURE);
    }

    if ((theta >= 1.0) || (theta <= 0.0)) {
      cerr << args << " : must have 0 < theta < 1" << endl; 
      exit(EXIT_FAILURE);
    } 

    if ((delta >= 0.5) || (delta <= 0.0)) {
      cerr << args << " : must have 0 < delta < 0.5" << endl; 
      exit(EXIT_FAILURE);
    } 

    // prepare parameters
    theta1 = max(0.0, theta-delta);
    theta2 = min(1.0, theta+delta);

    // another sanity check
    if ((theta1 <= 0.0) || (theta2 >= 1.0)) {
      cerr << args << " : indifference region borders 0 or 1" << endl; 
      exit(EXIT_FAILURE);
    }
    
    // writes back the test arguments, with proper formatting
    ostringstream tmp;
    tmp << testName << " " << theta << " " << T << " " << delta;
    args = tmp.str();
  }

  void doTest (unsigned long int n, unsigned long int x) {

    double r,t;

    // compute log-ratio and log-threshold
    r = x * log (theta2/theta1) + (n-x)*log((1-theta2)/(1-theta1));
    t = log(T);

    // compare and, if done, set
    if (r > t) {out = NULLHYP; samples = n; successes = x;}
    else { if (r < -t) {out = ALTHYP; samples = n; successes = x;}}
  }
};
    


int main (int argc, char **argv) {
  // Call the simulator to generate element trace files, check output against 
  // the provided property using the specified statistical test.

  const string USAGE = 
    "\nUsage: dishwrap <testfile> <checker> <property> <simulator> <modelfile> <trace> [<scenarios>] [<normalize>] [<steps>] \n\n"
    "where:\n"
    "      <testfile> is a sequence of test specifications;\n"
    "      <checker> is the path to the trace checker executable;\n"
    "      <property> is the file name of the BLTL property to check;\n"
    "      <simulator> is the path to simulator_interface.py;\n"
    "      <modelfile> is the file name of the model in DySE format;\n"
    "      <trace> is the name of the trace file computed by the simulator;\n"
    "      <scenarios> indicates the initial values to use \n"
    "         input two comma-separated values to calculate the difference \n"
    "         (0 is the first initial values column in modelfile); \n"
    "      <normalize> {0,1} is whether to normalize scenarios to the first scenario input \n"
    "      <steps> is the number of simulation steps \n"
    "Available test specifications: \n\n"
    "Hypothesis test:\n"
    " Lai's test: Lai <theta> <cost per sample>\n"
    " Bayes Factor test: BFT <theta> <threshold T> <alpha> <beta>\n"
    " Sequential Probability Ratio Test: SPRT <theta> <threshold T> <indifference region delta>\n"
    " Bayes Factor test with indifference region: BFTI <theta> <threshold T> <alpha> <beta> <indifference region delta>\n"
    "\n"
    "Estimation methods:\n"
    " Chernoff-Hoeffding bound: CHB <delta> <coverage probability>\n"
    " Bayesian estimation: BEST <delta> <coverage probability> <alpha> <beta>\n\n"
    "Empty lines and lines beginning with '#' are ignored.\n"
    "";

  bool alldone = false;		// all tests done
  bool done;
  unsigned long int n = 0;	// number of samples
  unsigned long int x = 0;	// number of successes
  unsigned int numtests = 0;	// number of tests to perform

  int ret;			// code returned by system when calling the simulator

  vector<string> lines;		// variables for string processing
  string line, keyword;

  vector<Test *> myTests;	// list of tests to perform

  // simulator arguments
  // TODO: use keyword option inputs instead of positional
  vector<string> scenarios;
  string scenarios_input((char *) "0");
  string normalize_input((char *) "0");
  string steps_input((char *) "1000");

  // check input arguments
  if (argc == 10) {
    scenarios_input = (char *) argv[7];
    normalize_input = (char *) argv[8];
    steps_input = (char *) argv[9];
  }
  else if (argc == 9) {
    scenarios_input = (char *) argv[7];
    normalize_input = (char *) argv[8];
  }
  else if (argc == 8) {
    scenarios_input = (char *) argv[7];
  }
  else if (argc != 7) {
    cout << USAGE << endl;
    exit(EXIT_FAILURE);
  }

  // command for running the trace checker
  string checkercommand((char *) argv[2]);
  string property((char *) argv[3]);
  
  // command for running the simulator interface
  string simcommand((char *) argv[4]);
  // location of the model file
  string modelfile((char *) argv[5]);
  // name of the simulation trace output file
  string trace((char *) argv[6]);

  // base command for running simulator
  string basedishcmd = "python3 " + simcommand + " " + modelfile;

  // input test file
  string testfile((char *) argv[1]);

  // read test input file line by line
  ifstream input(testfile.c_str());
  if (!input.is_open()) {
    cerr << "Error: cannot open testfile: " << argv[1] << endl;
    exit(EXIT_FAILURE);
  }
  while( getline(input, line) ) lines.push_back(line);

  // for each test create object, pass arguments, and initialize
  for (int i = 0; i < lines.size(); i++) {

    istringstream iline(lines[i]);		// each line is a test specification
    
    // by default, extraction >> skips whitespaces
    keyword = "";
    iline >> keyword;
    
    // discard comments (lines starting with '#') or empty lines
    if ((keyword.compare(0, 1, "#") != 0) && (keyword.length() > 0)) {

      transform(keyword.begin(), keyword.end(), keyword.begin(), ::toupper);  // convert to uppercase

      // create the corresponding test object
      if      (keyword == "SPRT") myTests.push_back(new SPRT(lines[i]));
      else if (keyword == "BFT")  myTests.push_back(new BFT(lines[i]));
      else if (keyword == "LAI")  myTests.push_back(new Lai(lines[i]));
      else if (keyword == "CHB")  myTests.push_back(new CHB(lines[i]));
      else if (keyword == "BEST") myTests.push_back(new BayesEstim(lines[i]));
      else if (keyword == "BFTI") myTests.push_back(new BFTI(lines[i]));
      else {
        cerr << "Test unknown: " << lines[i] << endl;
        exit(EXIT_FAILURE);
      }

      myTests[numtests]->init();				// initializes the object
      numtests++;
    }
  }

  if (numtests == 0) {
    cout << "No test requested - exiting ..." << endl;
    exit (EXIT_SUCCESS);
  }

  // timing stuff
  time_t start = time(NULL);
  clock_t tic = clock();

    // build the command lines for calling the simulator and trace checker
    string dishcmd = basedishcmd + " " + trace + " --scenario=" + scenarios_input;
    dishcmd += " --steps=" + steps_input;
    dishcmd += " --output_format=2 --runs=1";

    checkercommand += " " + property;

    // process scenarios input
    boost::split(scenarios,scenarios_input,boost::is_any_of(","));
    
    if (scenarios.size() > 1) {
      // build command to call the checker on the processed trace file from the simulator
      // get base file path + name and extension of trace file
      vector<string> trace_split_ext;
      size_t ext_idx = trace.find_last_of(".");
      trace_split_ext.push_back(trace.substr(0, ext_idx));
      trace_split_ext.push_back(trace.substr(ext_idx));

      if ((trace_split_ext[0] == "") || (trace_split_ext[1] == "")) {
        cerr << "Error processing trace file path: " << trace << endl;
        exit(EXIT_FAILURE);
      }

      string trace_processed;

      if ((scenarios.size() == 2) && (normalize_input != "0")) {
        // will calculate the difference between the two scenarios, 
        // call the checker on the difference output file
        // using scenario number to index difference file
        trace_processed = trace_split_ext[0] + "_diff" + scenarios[1] + trace_split_ext[1];
        checkercommand += " " + trace_processed;

        dishcmd += " --difference";  
      }
      else if ((scenarios.size() > 2) && (normalize_input != "0")) {
        // will normalize traces, then concatenate all scenario traces 
        // into one file and call the checker on that file
        trace_processed = trace_split_ext[0] + "_concat" + trace_split_ext[1];
        checkercommand += " " + trace_processed;

        dishcmd += " --concatenate";
        dishcmd += " --difference";
      }
      else {
        // will concatenate all scenario traces (but won't normalize)
        // and call the checker on that file
        trace_processed = trace_split_ext[0] + "_concat" + trace_split_ext[1];
        checkercommand += " " + trace_processed;

        dishcmd += " --concatenate";
      }
      
    }
    else {
      checkercommand += " " + trace;
    }


    // start sampling
    while (! alldone) {
      
      // call the simulator
      cout << "Calling simulator" << endl;
      cout << dishcmd << endl;
      ret = system(dishcmd.c_str());

      if (!WIFEXITED(ret)) {
          cerr << "Error: system() call to simulator terminated abnormally: " << dishcmd << endl;
          exit (EXIT_FAILURE);
      }

      if (WEXITSTATUS(ret) == EXIT_FAILURE) {
          cerr << "Error: system() call to simulator unsuccessful: " << dishcmd << endl;
          exit (EXIT_FAILURE);
      }

      // call the checker
      cout << "Calling checker" << endl;
      cout << checkercommand << endl;
      ret = system(checkercommand.c_str());

      if (!WIFEXITED(ret)) {
          cerr << "Error: system() call to trace checker terminated abnormally: " << checkercommand << endl;
          exit (EXIT_FAILURE);
      }

      switch (WEXITSTATUS(ret)) {

	      // increase number of successes
        case EXIT_SUCCESS_SAT:  x++; break;

        case EXIT_SUCCESS_UNSAT: break;

        default:
          cerr << "Error: unknown return code from trace checker - return code: " << ret << endl;
          exit (EXIT_FAILURE);
      }
        
      // increase number of samples
      n++;

        // do all the tests
        alldone = true;
        for (int j = 0; j < numtests; j++) {
  
          // do a test, if not done
          done = myTests[j]->done();
          if (!done) { 
            myTests[j]->doTest (n, x);
            done = myTests[j]->done();
	    if (done) myTests[j]->printResult();
          }
          alldone = alldone && done;
        }

    }		// loop

  cout << "Elapsed cpu time: " << (clock() - tic) / (double)CLOCKS_PER_SEC << endl;

  cout << "Elapsed wall time: " << (time(NULL) - start) << endl;

  exit(EXIT_SUCCESS);
}
