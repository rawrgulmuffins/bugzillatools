import distutils.core
import sys

import bzlib  # import version info

with open('README') as fh:
    long_description = fh.read()

distutils.core.setup(
    name='bugzillatools',
    version=bzlib.version,
    description='Bugzilla CLI client and XML-RPC interface library',
    author='Fraser Tweedale',
    author_email='frasert@jumbolotteries.com',
    url='https://gitorious.org/bugzillatools',
    packages=['bzlib'],
    scripts=['bin/bugzilla'],
    data_files=[
        ('doc/bugzillatools', ['doc/.bugzillarc.sample']),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Bug Tracking',
    ],
    long_description=long_description,
)
