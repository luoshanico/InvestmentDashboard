from setuptools import setup, find_packages

setup(
    name='Investment Dashboard',
    version='1.0',
    description='An investment dashboard. Track total value over time',
    license="No licensing",
    author='Nico Worrall',
    author_email='foomail@foo.example',
    url="http://www.google.com/",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=[
        'streamlit', 
        'numpy', 
        'pandas',  
        'yfinance', 
        'datetime'], 
        #external packages as dependencies
    scripts=[
        'project/api_helpers.py',
        'project/assets_page.py',
        'project/calculations.py',
        'project/colour_palette.py',
        'project/dashboard_page.py',
        'project/db_helpers.py',
        'project/reset_page.py',
        'project/transactions_page.py',
        ]
    )