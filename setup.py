from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

tests_require = [
  'pytest',
  'pytest-cov',
  'testfixtures',
]

setup(
  name='operator-courier',
  packages=['operatorcourier'],
  version='2.1.10',
  description='Build, verify and push operators',
  author='AOS Marketplace',
  author_email='aos-marketplace@redhat.com',
  url='https://github.com/operator-framework/operator-courier',
  entry_points={
    'console_scripts': ['operator-courier=operatorcourier.cli:main'],
  },
  keywords=['operator', 'courier'],
  install_requires=[
    'pyyaml',
    'requests',
    'validators',
    'semver'
  ],
  python_requires='>=3.6, <4',
  setup_requires=['pytest-runner'],
  tests_require=tests_require,
  extras_require={
    'test': tests_require,
  },
  long_description=long_description,
  long_description_content_type="text/markdown",
  license="Apache License 2.0",
  include_package_data=True,
  classifiers=[
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
