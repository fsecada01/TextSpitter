import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TextSpitter",
    version="0.3",
    author="Francis Secada",
    author_email="francis.secada@gmail.com",
    description="Python package that spits out text from your document files!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fsecada01/TextSpitter",
    packages=setuptools.find_packages(),
    install_requires=['python-docx>=0.8.6',
                      # 'PyMuPDF',
                      'PyPDF2'
                      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
