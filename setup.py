from setuptools import find_packages, setup

setup(name="agentic_trading_bot",
    version="0.0.1",
    author="parjanya",
    author_email="padityashukla26@gmail.com",
    packages=find_packages(),
    install_requires= ['langchain', 'lancedb', 'langgraph', 'polygon', 'tavily-python']
    )