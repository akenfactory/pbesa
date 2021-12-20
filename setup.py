from distutils.core import setup
import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'pbesa',
  long_description=long_description,
  long_description_content_type='text/markdown',
  version = '3.1.4',
  license='MIT',
  description = 'An artificial intelligence platform for the implementation of multi-agent systems based on python 3 and the BESA model',
  author = 'Enrique Gonzales Guerreo, Cesar Julio Bustacara, Fabian Jose Roldan',
  author_email = 'egonzal@javeriana.edu.co, cbustaca@javeriana.edu.co, fjroldan@akenfactory.com',
  url = 'https://github.com/akenfactory/pbesa.git',
  download_url = 'https://github.com/akenfactory/pbesa/archive/3.1.4.tar.gz',
  keywords = ['agent', 'multi-agent', 'system', 'artificial', 'intelligence'],
  packages=setuptools.find_packages(),
  install_requires=[            # I get to this in a second
    'pymongo==3.12.0',
    'scrapy==2.5.0',
    'pygame==2.1.0'
  ],
  classifiers=[  # Optional
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 5 - Production/Stable',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.8',
  ],
)
