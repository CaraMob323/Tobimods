from setuptools import setup, find_packages


with open("README.rst", "r") as file:
    readme = file.read()

with open("LICENSE", "r") as file:
    license = file.read()

with open("requeriments.txt", "r") as file:
    requeriments = file.read()

setup(
    name='TobiMods',
    version='0.0.1',
    description='R2modman but poor',
    long_description=readme,
    author='Cara',
    author_email='caramob321@gmail.com',
    url='https://github.com/CaraMob323/TOBIMODS',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires = requeriments
)