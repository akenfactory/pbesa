from setuptools import setup, find_packages



setup(
    name='pbesa',
    version='4.0.23',
    packages=find_packages(),
    install_requires=[
        'pymongo>=4.6.3',
        'requests>=2.32.3',
        'azure-ai-projects>=1.0.0b6',
        'azure-ai-inference>=1.0.0b9',
        'azure-identity>=1.21.0',
        'pandas>=2.2.3',
        'scikit-learn>=1.6.1',
    ],
)