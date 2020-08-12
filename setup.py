import re

from setuptools import find_packages
from setuptools import setup


def find_version():
    return re.search(r'^__version__ = "(.*)"$',
                     open('asn1editor/__init__.py', 'r').read(),
                     re.MULTILINE).group(1)


setup(name='asn1editor',
      version=find_version(),
      description='ASN.1 editor framework with support for encoding and decoding various codecs.',
      long_description=open('README.md', 'r').read(),
      long_description_content_type='text/markdown',
      author='Florian Fetz',
      author_email='florian.fetz@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development'
      ],
      keywords=['ASN.1', 'asn1', 'editor'],
      url='https://github.com/futsch1/asn1editor',
      packages=find_packages(exclude=['tests', 'examples']),
      install_requires=[
          'asn1tools>=0.153.0',
          'wxpython>= 4.1.0'
      ],
      test_suite="tests",
      python_requires='>=3.6')
