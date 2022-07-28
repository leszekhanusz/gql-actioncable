import os

from setuptools import setup, find_packages

install_requires = [
    "gql[websockets]>=3.4.0,<4.0",
]

dev_requires = [
    "black==22.3.0",
    "check-manifest>=0.42,<1",
    "flake8==3.8.1",
    "isort==4.3.21",
    "mypy==0.910",
]

# Get version from __version__.py file
current_folder = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(current_folder, "gqlactioncable", "__version__.py"), "r") as f:
    exec(f.read(), about)

setup(
    name="gqlactioncable",
    version=about["__version__"],
    description="GraphQL transport for gql for the ActionCable websockets protocol",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/leszekhanusz/gql-actioncable",
    author="Leszek Hanusz",
    author_email="leszek.hanusz@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords="api graphql actioncable protocol gql client",
    packages=find_packages(include=["gqlactioncable*"]),
    # PEP-561: https://www.python.org/dev/peps/pep-0561/
    package_data={"gqlactioncable": ["py.typed"]},
    install_requires=install_requires,
    extras_require={
        "dev": install_requires + dev_requires,
    },
    include_package_data=True,
    zip_safe=False,
    platforms="any",
)
