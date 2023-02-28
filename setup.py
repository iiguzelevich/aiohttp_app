from setuptools import setup, find_packages
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.absolute()


def get_version():
    with open(BASE_DIR / 'VERSION') as file:
        return file.readline().strip()


def get_license():
    with open(BASE_DIR / 'LICENSE') as file:
        return file.read().strip()


def get_desc():
    with open(BASE_DIR / 'README.md') as file:
        return file.read().strip()


def get_packages():
    with open(BASE_DIR / 'requirements.txt') as file:
        return [
            package.strip()
            for package in file
            if package or not package.startswith('#')
        ]


setup(
    name='anet',
    version=get_version(),
    author='Igor',
    author_email='ii1@gmail.com',
    packages=find_packages(
        '.',
        include=['anet', 'anet.*'],
        exclude=['*tests*.py', 'test*']
    ),
    package_dir={'anet.*': 'anet'},
    include_package_data=True,
    license=get_license(),
    description='...',
    long_description=get_desc(),
    long_description_content_type='text/markdown',
    install_requires=['lib', 'lib'],
    python_requires='>3.9',
    classifiers=[
        'Development Status :: 3 - Alpha'
        if 'dev' in get_version()
        else 'Development Status :: 4 Beta'
        if 'rc' in get_version()
        else 'Development Status :: 5 Production/Stable'
    ],
    entry_points={
        'console_scripts': ['anet_runer = anet.app:run']
    }
)
