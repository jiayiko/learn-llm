"""Setup configuration for Scout Agent."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scout-agent",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Intelligent GitHub project discovery and analysis agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/scout-agent",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langchain==0.1.0",
        "langchain-google-genai==0.0.11",
        "langgraph==0.0.60",
        "pydantic==2.5.0",
        "PyGithub==2.1.1",
        "python-dotenv==1.0.0",
        "streamlit==1.28.0",
        "sentence-transformers==2.2.2",
        "scikit-learn==1.3.2",
        "numpy==1.24.3",
    ],
    entry_points={
        "console_scripts": [
            "scout-agent=src.ui.app:main",
        ],
    },
)
