from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="f1-telemetry-delta-calculator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="High-precision Formula 1 telemetry delta calculation for professional visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/f1-telemetry-delta-calculator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="formula1, f1, telemetry, visualization, racing, motorsport",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/f1-telemetry-delta-calculator/issues",
        "Source": "https://github.com/yourusername/f1-telemetry-delta-calculator",
        "3D Visualization Pipeline": "https://github.com/lohithburra01/F1-3D-VISUALIZATION",
    },
)
