import os
import re
from glob import iglob

from setuptools import setup, find_packages

requirements = []
with open('requirements.txt') as f:
    # noinspection PyRedeclaration
    requirements = f.read().splitlines()

version = ''
with open('bot-client/starcraft_io/__init__.py') as f:
    # noinspection PyRedeclaration
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if (not version):
    raise RuntimeError("Package version is not set")

if (version.endswith(('a', 'b', 'rc'))):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass

packages = find_packages('src')

readme = ''
with open('README.md') as f:
    # noinspection PyRedeclaration
    readme = f.read()

extras_require = { }
for r in iglob('requirements/requirements-*.txt'):
    with open(r) as f:
        reqs = [ l.strip() for l in f ]
        feature_name = re.match(r'requirements-(.*)\.txt', os.path.basename(r)).group(1).title()
        extras_require[feature_name] = reqs
extras_require.setdefault('all', sum(extras_require.values(), list()))

setup \
(
    name = 'starcraft-io',
    url = 'https://github.com/USSX-Hares/sc2-bank-io',
    version = version,
    packages = packages,
    setup_requires = [ 'wheel' ],
    package_data = { '': [ 'resources/*.conf' ] },
    package_dir = { '': 'bot-client' },
    license = "BSD 2-Clause License",
    description = "An implementation of two-side data-channel between StarCraft II and the outer world",
    long_description = readme,
    long_description_content_type = 'text/markdown',
    include_package_data = True,
    install_requires = requirements,
    extras_require = extras_require,
    python_requires = '>=3.6.0',
    classifiers =
    [
        'Development Status :: 2 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
