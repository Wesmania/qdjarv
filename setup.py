from setuptools import setup

long_desc = open("README.md", "r").read()

setup(name="qdjarv",
      version="0.1",
      description="Quick and dirty jsonapi response validator",
      long_description=long_desc,
      long_description_content_type="text/markdown",
      url="https://github.com/Wesmania/qdjarv",
      author="Igor Kotrasinski",
      author_email='i.kotrasinsk@gmail.com',
      license='MIT',
      packages=['qdjarv'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      )
