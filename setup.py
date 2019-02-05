from setuptools import setup
setup(
  name='operator-courier',
  packages=['operatorcourier'],
  version='4.0.8',
  description='Build, verify and push operators',
  author='AOS Marketplace',
  author_email='aos-marketplace@redhat.com',
  url='https://github.com/kevinrizza/operator-courier', 
  entry_points = {
    'console_scripts': ['operator-courier=operatorcourier.cli:main'],
  },
  keywords = ['operator', 'courier'],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
)
