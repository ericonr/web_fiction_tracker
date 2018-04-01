from setuptools import setup

setup(
    name='web_fiction_tracker',
    packages=['web_fiction_tracker'],
    include_package_data=True,
    install_requires=[
        'flask',
        'bs4',
    ],
)