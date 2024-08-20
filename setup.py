from setuptools import setup, find_packages



setup(
    name='pbesa',
    version='4.0.0',
    packages=find_packages(),
    install_requires=[
        'pymongo>=4.6.3',
        'requests>=2.32.3',
    ],
)