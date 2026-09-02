from setuptools import setup, find_packages

setup(
    name="orcaopta",
    version="0.1.0",
    description="Multi-cloud operator brain for SRE automation, observability, and intelligent remediation.",
    author="Samuel",
    author_email="orcaprojectstack@gmail.com",
    license="MIT",

    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.10",

    install_requires=[
        # Core utilities
        "pyyaml",
        "rich",
        "python-dotenv",
        "typer",
        "orjson",
        "click",

        # Cloud backends
        "minio",
        "cryptography",
        "ossaudit",

        # Optional ML (small footprint)
        #"sentence-transformers",
       # "faiss-cpu",
    ],

    include_package_data=True,
)
