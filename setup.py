from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='ACCORDION',
    version='Latest',

    author='Yasmine Ahmed',
    #author_email='',
    description='ACCelerating and Optimizing model RecommenDatIONs',
    long_description='A conditional clustering of relating data, built by the Mechanisms and Logic of Dynamics Lab at the University of Pittsburgh',
    #license='',
    keywords='dynamic system boolean logical qualitative modeling simulation',

    package=['src','dependencies/Model_Checking']

    include_package_data=True,

    install_requires=[
        'networkx',
        'numpy',
        'pandas',
        'openpyxl',
        'rst2pdf',
        'joblib',
        'tornado==4.5.3' # to not interfere with jupyter
    ],
    zip_safe=False # install as directory
    )
