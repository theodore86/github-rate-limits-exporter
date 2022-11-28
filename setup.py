""" github_rate_limits_exporter packaging """

from os.path import dirname, join, realpath
import setuptools


CUR_DIR = dirname(realpath(__file__))
VERSION_FILE = join(CUR_DIR, "github_rate_limits_exporter", "_version.py")
LONG_DESCRIPTION = join(CUR_DIR, "README.md")
REQUIREMENTS = join(CUR_DIR, "requirements.txt")


with open(join(LONG_DESCRIPTION), "r", encoding="utf-8") as rh:
    DESCRIPTION = rh.read()

PROJECT = {}
with open(VERSION_FILE, "r", encoding="utf-8") as vh:
    exec(vh.read(), PROJECT)  # pylint: disable=w0122

with open(REQUIREMENTS, encoding="utf-8") as rfh:
    REQUIRES = rfh.readlines()


CLASSIFIERS = """
Development Status :: 5 - Production/Stable
Intended Audience :: System Administrators
Topic :: System :: Monitoring
License :: Other/Proprietary License
License :: OSI Approved :: MIT License
Natural Language :: English
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Topic :: Software Development :: Documentation
""".strip().splitlines()

setuptools.setup(
    author=PROJECT["__author__"],
    author_email=PROJECT["__author_email__"],
    url=PROJECT["__url__"],
    python_requires=">=3.7",
    name=PROJECT["__title__"],
    version=PROJECT["__version__"],
    package_dir={"": "."},
    packages=["github_rate_limits_exporter"],
    license=PROJECT["__license__"],
    platforms=PROJECT["__platforms__"],
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    description=PROJECT["__description__"],
    classifiers=CLASSIFIERS,
    install_requires=REQUIRES,
    entry_points={
        "console_scripts": [
            "github-rate-limits-exporter=github_rate_limits_exporter.__main__:main"
        ]
    },
)
