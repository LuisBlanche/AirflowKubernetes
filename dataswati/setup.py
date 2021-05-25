from setuptools import find_packages, setup

setup(
    name='potability',
    packages=find_packages(),
    version='0.1.0',
    description='A simple ML code to use in an Airflow DAG with KubernetesPodOperator',
    author='lblanche@dataswati.com',
    license='MIT',
)
