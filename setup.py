from setuptools import setup, find_packages



setup(
    name='pbesa',
    version='4.0.9',
    packages=find_packages(),
    install_requires=[
        'pymongo==4.6.3',
        'requests==2.32.3',
        'azure-ai-projects==1.0.0b6',
        'azure-ai-inference==1.0.0b9',
        'azure-identity==1.20.0'
    ],
)