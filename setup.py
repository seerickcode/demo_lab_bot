from setuptools import setup, find_packages

setup(
    name='labbot',
    version='0.0.1',
    license='proprietary',
    description='Lab Session management bot for Slack',

    author='Richard Clark',
    author_email='rick@seerickcode.com',
    url='https://seerickcode.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "click",
    ],
    entry_points='''
        [console_scripts]
        labbot=labbot.cli:cli
    ''',
)
