import distutils.core
import sys

import bzlib  # import version info

with open('README.rst') as fh:
    readme = fh.read()
with open('CHANGES') as fh:
    changes = fh.read()
long_description = '\n\n'.join((readme, changes))

distutils.core.setup(
    name='bugzillatools',
    version=bzlib.version,
    description='Bugzilla CLI client, XML-RPC binding and VCS plugins',
    author='Fraser Tweedale',
    author_email='frase@frase.id.au',
    url='https://github.com/frasertweedale/bugzillatools',
    packages=['bzlib', 'bzrlib.plugins.bugzillatools'],
    package_dir={
        'bzlib': 'bzlib',
        'bzrlib.plugins.bugzillatools': 'plugin-bzr',
    },
    scripts=['bin/bugzilla'],
    data_files=[
        ('doc/bugzillatools', ['doc/.bugzillarc.sample']),
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Version Control',
    ],
    long_description=long_description,
)
