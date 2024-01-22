from setuptools import setup
from setuptools.command.install import install
import subprocess
import platform

def readme():
    with open('README.md') as f:
        return f.read()

# building non-python dependencies (mcl, gsl)
# This compileLibrary(install) class only works with 'python setup.py install', not 'pip install -e .'
class compileLibrary(install):
    def run(self):
        install.run(self)

        command=""
        # in model extension(ACCORDION), MCL package installation is required
        if platform.system()=='Darwin':
            command += "cd dependencies && tar -xvzf mcl-14-137.tar.gz && "
            command += "cd mcl-14-137 && ./configure && make && sudo make install && cd .. && rm -r mcl-14-137/ && mcl -h"
        elif platform.system()=='Linux':
            command += "sudo apt-get install mcl"
        elif platform.system()== 'Windows' or platform.system().startswith('CYGWIN'):
            command += "cd dependencies && tar -xvzf mcl-14-137.tar.gz && "
            command += "cd mcl-14-137 && sh configure && make && make install && cd .. && rm -r mcl-14-137/ && mcl -h"
        process = subprocess.Popen(command, shell=True)
        process.wait()

        command=""
        # in model checking, gsl package installation is required
        if platform.system()=='Darwin' or platform.system()=='Linux':
            command += "cd dependencies && tar -xvzf gsl-2.7.1.tar.gz && "
            command += "cd gsl-2.7.1 && ./configure && make && sudo make install && cd .. && rm -r gsl-2.7.1/"
        elif platform.system()== 'Windows' or platform.system().startswith('CYGWIN'):
            #gsl is supposed to be installed within cygwin installation
            command += ""
        process = subprocess.Popen(command, shell=True)
        process.wait()

        #compile two c++ files
        command = "cd dependencies/Model_Checking/dishwrap_v1.0/dishwrap && make clean && make"
        command += "&& cd ../monitor && make clean && make"
        process = subprocess.Popen(command, shell=True)
        process.wait()

setup(
    name='ACCORDION',
    version='1.0',

    author='Yasmine Ahmed',
    #author_email='',
    description='ACCelerating and Optimizing model RecommenDatIONs',
    long_description='A conditional clustering of relating data, built by the Mechanisms and Logic of Dynamics Lab at the University of Pittsburgh',
    #license='',
    keywords='extension clustering modeling model-checking',

    package=['src','dependencies.Model_Checking'],

    cmdclass={'install': compileLibrary},

    include_package_data=True,

    install_requires=[
        'networkx',
        'numpy',
        'pandas',
        'openpyxl',
        'rst2pdf',
        'joblib',
        'tornado'
    ],
    zip_safe=False # install as directory
    )
