import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="checking",
    version="0.9.1",
    author="Lex Draven",
    author_email="lexman2@yandex.ru",
    description="A small library for unit-testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kotolex/checking",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
