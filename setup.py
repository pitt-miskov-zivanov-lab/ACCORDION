from setuptools import setup
from setuptools.command.install import install
import subprocess

def readme():
    with open('README.md') as f:
        return f.read()

# building non-python dependencies (mcl, gsl)
# This compileLibrary(install) class only works with 'python setup.py install', not 'pip install -e .'
class compileLibrary(install):
    def run(self):
        install.run(self)

        # in model extension(ACCORDION), MCL package installation is required
        command = "cd dependencies/mcl-14-137"
        command += " && ./configure && make && make install && make clean && make distclean"
        process = subprocess.Popen(command, shell=True)
        process.wait()

        # in model checking, gsl package installation and two build-ups are required
        command = "cd dependencies/gsl-2.7.1"
        command += " && ./configure && make && make install && make clean && make distclean"
        command += " && cd ../Model_Checking/dishwrap_v1.0/dishwrap && make"
        command += " && cd ../monitor && make"
        process = subprocess.Popen(command, shell=True)
        process.wait()

setup(
    name='ACCORDION',
    version='Latest',

    author='Yasmine Ahmed',
    #author_email='',
    description='ACCelerating and Optimizing model RecommenDatIONs',
    long_description='A conditional clustering of relating data, built by the Mechanisms and Logic of Dynamics Lab at the University of Pittsburgh',
    #license='',
    keywords='dynamic system boolean logical qualitative modeling simulation',

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
