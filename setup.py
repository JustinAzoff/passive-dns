from setuptools import setup, find_packages
from glob import glob


version = '0.5'

setup(name='passive-dns',
      version=version,
      description="Passive DNS Logger",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='passive dns',
      author='Justin Azoff',
      author_email='JAzoff@uamail.albany.edu',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      extras_require = {
          "server": ["pcapy", "dnspython","tornado"],
          "client": ["requests"],
      },
      scripts=glob('scripts/*'),
      entry_points = {
          'console_scripts': [
              'passive-dns-merge    = passive_dns.merge:main',
              'passive-dns-process  = passive_dns.process:main',
              'passive-dns-search   = passive_dns.search:main',
              'passive-dns-searchserver  = passive_dns.search_server:main',
              'passive-dns-client   = passive_dns.client:main',
              'passive-dns-expload  = passive_dns.expload:main',
              'passive-dns-dump-config = passive_dns.config:dump_config',
          ]
      }
      )
