
CPP = g++
DEFS =
CFLAGS =
CDEBUG = #-g
COPT = -O3 #-Wall
VERBOSE = #-DVERBOSE
OPENMP_LIB = -fopenmp
GSL_LIB = -lgsl -lgslcblas
LIBS = $(GSL_LIB)
DEFS = -DOPENMP

EXEC= dishwrap
# EXEC= dishwrap pdishwrap

# all: $(EXEC)

# single processor
dishwrap: dishwrap.cpp Makefile
	$(CPP) $(COPT) -o dishwrap dishwrap.cpp $(CDEBUG) $(VERBOSE) $(LIBS)

# # parallel version, using OpenMP
# pdishwrap: dishwrap.cpp Makefile
# 	$(CPP) $(DEFS) $(COPT) -o pdishwrap dishwrap.cpp $(CDEBUG) $(VERBOSE) $(LIBS) $(OPENMP_LIB)

clean:
	rm -f *.o
	rm -f $(EXEC)
