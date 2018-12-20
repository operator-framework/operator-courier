from setuptools import setup
setup(
  name='operator-courier',
  packages=['command'],
  version='4.0.8',
  description='Build, verify and push operators',
  author='AOS Marketplace',
  author_email='aos-marketplace@redhat.com',
  url='https://github.com/kevinrizza/operator-courier', 
  entry_points = {
    'console_scripts': ['operator-courier=command.cli:main'],
  },
  keywords = ['operator', 'courier'],
  test_suite='nose.collector',
  tests_require=['nose'],
)
