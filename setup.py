from os import path

from setuptools import find_namespace_packages, setup


NAMESPACE = "cro"
PACKAGE_PATH = f"{NAMESPACE}.respondent.resolve"
PACKAGE_NAME = f"{NAMESPACE}-respondent-resolve"

TEST_DEPS = ["pytest"]
LINT_DEPS = ["black", "pylint", "flake8", "mypy"]
DOCS_DEPS = ["sphinx"]

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=f"{PACKAGE_NAME}",
    version="0.0.1",
    author="Krystof Pesek",
    description="Package resolving new to existing respondent entries.",
    long_description=f"{LONG_DESCRIPTION}",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src", include=[f"{NAMESPACE}.*"]),
    install_requires=[
        "numpy",
        "pandas",
        "flask",
    ],
    entry_points={
        "console_scripts": [
            f"{PACKAGE_NAME}={PACKAGE_PATH}.__main__:main",
        ]
    },
)
