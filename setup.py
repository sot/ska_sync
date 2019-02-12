from setuptools import setup, find_packages

from ska_sync.version import __version__

setup(name='ska_sync',
      author='Tom Aldcroft',
      description='Synchronize data files for Ska3 runtime environment',
      author_email='aldcroft@head.cfa.harvard.edu',
      entry_points={'console_scripts': ['ska_sync = ska_sync.main:main']},
      version=__version__,
      license='BSD',
      zip_safe=False,
      packages=find_packages(),
      package_data={'ska_sync': ['ska_sync_config']},
      )
