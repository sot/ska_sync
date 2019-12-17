from setuptools import setup, find_packages

setup(name='ska_sync',
      author='Tom Aldcroft',
      description='Synchronize data files for Ska3 runtime environment',
      author_email='aldcroft@head.cfa.harvard.edu',
      entry_points={'console_scripts': ['ska_sync = ska_sync.main:main']},
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      license='BSD',
      zip_safe=False,
      packages=find_packages(),
      package_data={'ska_sync': ['ska_sync_config']},
      )
