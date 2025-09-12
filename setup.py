#!/usr/bin/env python3
# setup.py - 项目安装脚本

from setuptools import setup, find_packages

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="comprehensive-stock-analyzer",
    version="1.0.0",
    author="AI Stock Analyzer Team",
    author_email="contact@stockanalyzer.com",
    description="全维度AI选股系统 - 基于OpenBB + AkShare的智能股票分析平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/comprehensive-stock-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "stock-analyzer=comprehensive_stock_analyzer:main",
        ],
    },
    keywords="stock analysis, AI, machine learning, finance, trading, OpenBB, AkShare",
    project_urls={
        "Bug Reports": "https://github.com/your-username/comprehensive-stock-analyzer/issues",
        "Source": "https://github.com/your-username/comprehensive-stock-analyzer",
        "Documentation": "https://github.com/your-username/comprehensive-stock-analyzer/wiki",
    },
)