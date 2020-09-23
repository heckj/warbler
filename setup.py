import pathlib
from datetime import datetime
from setuptools import setup, find_packages

current_path = pathlib.Path(__file__).parent

NAME = 'warbler'
ver_path = pathlib.Path(current_path, "warbler", "version.py")
_ver = {}
exec(ver_path.open("r").read(), _ver)
version = _ver["__version__"]
now = datetime.utcnow()
desc_path = pathlib.Path(current_path, "README.md")
long_description = desc_path.open("r").read()

setup(
    name=NAME,
    version=version,
    packages=find_packages(),
    platforms=['POSIX', 'MacOS', 'Windows'],
    python_requires='>=3.7.0',
    install_requires=[
        "textacy"
    ],
    # entry_points={
    #     'console_scripts': [
    #         'warbler = warbler.__main__:main'
    #     ],
    # },

    author='Joseph Heck',
    maintainer='Joseph Heck',
    maintainer_email='heckj@mac.com',
    author_email='heckj@mac.com',
    description='Content-focused language server for markdown that highlights the use of passive voice developed by Joseph Heck',
    url='https://github.com/heckj/warbler',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    license='Copyright (c) {} Joseph Heck'.format(now.year),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='markdown language passive-voice nlp'
)
