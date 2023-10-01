import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dynamodump",
    version="1.9.0",
    author="Benny Chew",
    author_email="noreply@bennychew.com",
    description="Simple backup and restore for Amazon DynamoDB using AWS SDK for Python (boto3)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bchew/dynamodump",
    project_urls={
        "Releases": "https://github.com/bchew/dynamodump/releases",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    packages=["dynamodump"],
    python_requires=">=3.8",
    install_requires=["boto3==1.26.165", "six==1.16.0"],
    entry_points={
        "console_scripts": ["dynamodump=dynamodump.dynamodump:main"],
    },
)
