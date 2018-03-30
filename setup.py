from setuptools import setup, find_packages

setup(
    name="Confession Manager",
    version="1.1",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url="https://github.com/LevyCory/confession_manager",
    author="Cory Levy",
    install_requires=[
        "facebook-sdk",
        "httplib2",
        "requests",
        "google-api-python-client"
    ],
    entry_points={
        "console_scripts": [
            "confession_manager=bot.server:main"
        ]
    }
)
