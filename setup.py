from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='rf_client',
    version='1.0.0',
    description='High level RedForester client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
    url='https://github.com/RedForester/rf_client',
    author='Red Forester',
    author_email='tech@redforester.com',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'rf_api_client ~= 0.1.0',
        'rf_event_listener ~= 0.0.0'
    ],
    extras_require={
        'dev': [
            'pytest ~= 5.4',
            'pytest-asyncio ~= 0.12',
            'flake8 ~= 3.8'
        ],
    },
    include_package_data=True,
    zip_safe=False
)
