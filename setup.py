from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
  name='operator-courier',
  packages=['operatorcourier'],
  version='1.0.3',
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
    'regex',
    'validators'
  ],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
  long_description=long_description,
  long_description_content_type="text/markdown",
  license="Apache License 2.0",
  include_package_data=True,
)
