from setuptools import setup, find_packages

setup(
    name="niceguiEditor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "nicegui>=1.3.5",
        "plotly>=5.14.0",
    ],
    author="",
    author_email="",
    description="NiceGUI 기반 에디터 라이브러리",
    keywords="nicegui,editor,ui",
    url="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
) 