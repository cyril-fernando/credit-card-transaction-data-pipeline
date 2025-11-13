from setuptools import find_packages, setup

setup(
    name="fraud_detection_dagster",
    packages=find_packages(exclude=["fraud_detection_dagster_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
