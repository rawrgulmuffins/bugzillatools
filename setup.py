from distutils.core import setup

file = open('README')
long_description = file.read()
file.close()

setup(
    name='bugzillatools',
    version='0.1dev',
    description='Bugzilla CLI client and XML-RPC interface library',
    author='Fraser Tweedale',
    author_email='frasert@jumbolotteries.com',
    url='http://www.jumbointeractive.com/',
    packages=['bzlib'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4',
        'Topic :: Software Development :: Bug Tracking',
    ],
    long_description=long_description,
)
