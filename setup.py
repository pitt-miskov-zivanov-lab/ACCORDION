from setuptools import setup

def readme():
    with open('README_accordion') as f:
        return f.read()

setup(
    name='ACCORDION',
    version='1.0',
    
    author='Yasmine Ahmed',
    #author_email='',
    description='ACCORDION',
    long_description='A conditional clustering of relating data, built by the Mechanisms and Logic of Dynamics Lab at the University of Pittsburgh',
    #license='',
    keywords='dynamic system boolean logical qualitative modeling simulation',

    packages=['ACCORDION'],
    include_package_data=True,

    install_requires=[
        'networkx',
        'numpy',
        'pandas',
        'openpyxl',
        'rst2pdf',
        'tornado==4.5.3' # to not interfere with jupyter
    ],
    zip_safe=False # install as directory
    )