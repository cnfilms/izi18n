import setuptools

setuptools.setup(
    name="izi18n",
    version="1.0.0",
    author="Joel ONIPOH",
    author_email="technique@cinego.net",
    description="Python internalization",
    packages=setuptools.find_packages(),
    install_requires=[r.strip() for r in open('requirements.txt').read().splitlines()],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.3'
)
