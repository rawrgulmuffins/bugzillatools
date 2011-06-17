from distutils.core import setup

with open('README') as fh:
    long_description = fh.read()

setup(
    name='bugzillatools',
    version='0.1.2',
    description='Bugzilla CLI client and XML-RPC interface library',
    author='Fraser Tweedale',
    author_email='frasert@jumbolotteries.com',
    url='https://gitorious.org/bugzillatools',
    packages=['bzlib'],
    scripts=['bin/bugzilla'],
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
