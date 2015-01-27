from setuptools import setup

setup(
    name='stratosphere',
    version='0.1.0',
    description='AWS CloudFormation orchestration library',
    author='Rob Zienert',
    author_email='rob@robzienert.com',
    license='MIT License',
    packages=['stratosphere'],
    setup_requires=['pep8', 'pyflakes', 'moto'],
    install_requires=['toposort', 'requests', 'boto'],
    scripts=[],
    test_suite='tests',
    tests_require=[],
    use_2to3=True
)
