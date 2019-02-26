from setuptools import setup
setup(
  name='operator-courier',
  packages=['operatorcourier'],
  version='1.0.2',
  description='Build, verify and push operators',
  author='AOS Marketplace',
  author_email='aos-marketplace@redhat.com',
  url='https://github.com/operator-framework/operator-courier', 
  entry_points = {
    'console_scripts': ['operator-courier=operatorcourier.cli:main'],
  },
  keywords = ['operator', 'courier'],
  install_requires=[
    'pyyaml', 
    'requests'
  ],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
)
