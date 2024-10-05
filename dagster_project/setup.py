from setuptools import find_packages, setup

setup(
    name="dagster_project",
    packages=find_packages(exclude=["dagster_project_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "pandas",
        "sqlalchemy==1.4.40",
        "pycoingecko",
        "matplotlib",
        "psycopg2-binary",
        "scikit-learn",
        "scipy"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
