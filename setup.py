import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="NHXDB",
    version="1.0b1",
    author="Ch. Muhammad Sohaib",
    author_email="chmuhammadsohaib@gmail.com",
    description="A lightweight Database Module with a blend of SQL like Language and NoSQL syntax",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chmuhammadsohaib/NHXDB",
    packages=setuptools.find_packages(),
    keywords = 'NHXDB NHXTech chmuhammadsohaib NHX Database',
    license="MIT",
    install_requires=[
        "ast",
        "hashlib"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)