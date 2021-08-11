#!/usr/bin/env python
"""Py-ART: Python ARM Radar Toolkit

The Python ARM Radar Toolkit, Py-ART, is an open source Python module containing
a growing collection of weather radar algorithms and utilities build on top of
the Scientific Python stack and distributed under the 3-Clause BSD license.
Py-ART is used by the Atmospheric Radiation Measurement (ARM) Climate Research
Facility for working with data from a number of precipitation and cloud radars,
but has been designed so that it can be used by others in the radar and
atmospheric communities to examine, processes, and analyse data from many types
of weather radars.

"""


DOCLINES = __doc__.split("\n")

import os
import sys
import subprocess
import glob
from setuptools import dist, setup, find_packages

from setuptools.extension import Extension
dist.Distribution().fetch_build_eggs(['Cython>=0.28', 'numpy>=1.10'])
import numpy

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins

import os
import sys


def guess_rsl_path():
    return {'darwin': '/usr/local/trmm',
            'linux2': '/usr/local/trmm',
            'linux': '/usr/local/trmm',
            'win32': 'XXX'}[sys.platform]


def get_rsl_lib_and_include_path():
    rsl_path = os.environ.get('RSL_PATH')
    if rsl_path is None:
        rsl_path = guess_rsl_path()
    rsl_lib_path = os.path.join(rsl_path, 'lib')
    rsl_include_path = os.path.join(rsl_path, 'include')
    return rsl_lib_path, rsl_include_path


def check_rsl_path(rsl_lib_path, rsl_include_path):
    ext = {'darwin': 'dylib',
           'linux2': 'so',
           'linux': 'so',
           'win32': 'DLL'}[sys.platform]
    lib_file = os.path.join(rsl_lib_path, 'librsl.' + ext)
    if os.path.isfile(lib_file) is False:
        return False

    inc_file = os.path.join(rsl_include_path, 'rsl.h')
    if os.path.isfile(inc_file) is False:
        return False
    return True


rsl_lib_path, rsl_include_path = get_rsl_lib_and_include_path()

def pyart_extensions():
    rsl_extensions = []
    if check_rsl_path(rsl_lib_path, rsl_include_path):
        rsl_extensions = [
            Extension('_fourdd_interface', sources=[
                'pyart/correct/src/dealias_fourdd.c',
                'pyart/correct/src/sounding_to_volume.c',
                'pyart/correct/src/helpers.c',
            ]),
        ]

    return [
        Extension('pyart.__check_build._check_build', sources=[
            'pyart/__check_build/_check_build.pyx',
        ]),
        Extension('pyart.correct._unwrap_1d', sources=[
            'pyart/correct/_unwrap_1d.pyx',
        ]),
        Extension('pyart.correct._unwrap_2d', sources=[
            'pyart/correct/_unwrap_2d.pyx',
            'pyart/correct/unwrap_2d_ljmu.c',
        ]),
        Extension('pyart.correct._unwrap_3d', sources=[
            'pyart/correct/_unwrap_3d.pyx',
            'pyart/correct/unwrap_3d_ljmu.c',
        ]),
        Extension('pyart.correct._fast_edge_finder', sources=[
            'pyart/correct/_fast_edge_finder.pyx',
        ]),
        Extension('pyart.io._sigmetfile', sources=[
            'pyart/io/_sigmetfile.pyx',
        ]),
        Extension('pyart.io.nexrad_interpolate', sources=[
            'pyart/io/nexrad_interpolate.pyx',
        ]),
        Extension('pyart.map.ckdtree', sources=[
            'pyart/map/ckdtree.pyx',
        ]),
        Extension('pyart.map._load_nn_field_data', sources=[
            'pyart/map/_load_nn_field_data.pyx',
        ]),
        Extension('pyart.map._gate_to_grid_map', sources=[
            'pyart/map/_gate_to_grid_map.pyx',
        ]),
        Extension('pyart.retrieve._kdp_proc', sources=[
            'pyart/retrieve/_kdp_proc.pyx',
        ]),
    ] + rsl_extensions

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: C',
    'Programming Language :: Cython',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Framework :: Matplotlib']

NAME = 'arm_pyart'
MAINTAINER = "Py-ART Developers"
MAINTAINER_EMAIL = "zsherman@anl.gov, scollis@anl.gov"
DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = "\n".join(DOCLINES[2:])
URL = "https://github.com/ARM-DOE/pyart"
DOWNLOAD_URL = "https://github.com/ARM-DOE/pyart"
LICENSE = 'BSD'
PLATFORMS = ["Linux", "Mac OS-X", "Unix"]
MAJOR = 1
MINOR = 11
MICRO = 6
ISRELEASED = False
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)
SCRIPTS = glob.glob('scripts/*')

# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = "Unknown"

    return GIT_REVISION


# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

# This is a bit hackish: we are setting a global variable so that the main
# pyart __init__ can detect if it is being loaded by the setup routine, to
# avoid attempting to load components that aren't built yet. While ugly, it's
# a lot more robust than what was previously being used.
builtins.__PYART_SETUP__ = True


def write_version_py(filename='pyart/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM PYART SETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of pyart.version messes up the build under Python 3.
    FULLVERSION = VERSION
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists('pyart/version.py'):
        # must be a source distribution, use existing version file
        try:
            from pyart.version import git_revision as GIT_REVISION
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "pyart/version.py and the build directory "
                              "before building.")
    else:
        GIT_REVISION = "Unknown"

    if not ISRELEASED:
        FULLVERSION += '.dev+' + GIT_REVISION[:7]

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version': FULLVERSION,
                       'git_revision': GIT_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()

#
# def configuration(parent_package='', top_path=None):
#     from numpy.distutils.misc_util import Configuration
#     config = Configuration(None, parent_package, top_path)
#     config.set_options(ignore_setup_xxx_py=True,
#                        assume_default_configuration=True,
#                        delegate_options_to_subpackages=True,
#                        quiet=True)
#
#     config.add_subpackage('pyart')
#     config.add_data_files(('pyart', '*.txt'))
#
#     return config

TEST_DEPENDENCIES = [
    'cartopy',
    'hypothesis',
    'pytest',
    'numpy>=1.10',
    'xarray',
]

DEV_DEPENDENCIES = [
   'pip-tools'
] + TEST_DEPENDENCIES


def setup_package():
    setup(
        name=NAME,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        classifiers=CLASSIFIERS,
        platforms=PLATFORMS,
        # configuration=configuration,
        packages=find_packages(include=['pyart']),
        python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
        setup_requires=[
            'Cython>=0.28',
            'numpy>=1.10',
            'semver',
            'setuptools>=18.0',
        ],
        install_requires=[
            'numpy>=1.10',
            'scipy',
            'matplotlib',
            'netcdf4',
        ],
        extras_require={
            'cartopy': ['cartopy'],
            'cvxopt': ['cvxopt'],
            'cylp': ['cylp'],
            'gdal': ['gdal'],
            'h5py': ['h5py'],
            'pyglpk': ['glpk'],
            'wradlib': ['wradlib'],
            'xarray': ['xarray'],
            # 'trmm_rsl': ['trmm_rsl'],
            'basemap': ['basemap'],    # conda only, no pypi package exists
            'dev': DEV_DEPENDENCIES,
            'test': TEST_DEPENDENCIES,
        },
        ext_modules=pyart_extensions(),
        include_dirs=[
            numpy.get_include(),
            rsl_include_path,
        ],
        scripts=SCRIPTS,
    )
    # rewrite version file
    write_version_py()

if __name__ == '__main__':
    setup_package()
