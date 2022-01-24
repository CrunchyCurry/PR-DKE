from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='Strecken-Informationsystem SIS',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
)