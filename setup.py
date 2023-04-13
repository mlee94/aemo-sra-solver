from pathlib import Path
from setuptools import setup

from aemo.sra.solver import __version__

REQUIREMENTS = Path(__file__).parents[0].joinpath("requirements.txt").read_text()

setup(
    name='aemo-sra-solver',
    entry_points={'console_scripts': ['mycode=mycode.py:main']},
    version=__version__,
    python_requires='>3.7',
    url='',
    author='Michael Lee',
    author_email='michaelleeacc@gmail.com',
    py_modules=['aemo-sra-solver'],
    install_requires=REQUIREMENTS,
)