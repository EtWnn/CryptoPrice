import os
from setuptools import setup

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(os.path.join(this_directory, 'CryptoPrice/__about__.py'), encoding='utf-8') as f:
    exec(f.read(), about)

setup(
    name='python-CryptoPrice',
    version=about['__version__'],
    packages=['CryptoPrice',
              'CryptoPrice.retrievers',
              'CryptoPrice.storage',
              'CryptoPrice.utils',
              'CryptoPrice.common'],
    url='https://github.com/EtWnn/CryptoPrice',
    author='EtWnn',
    author_email='',
    license='MIT',
    description='Library to retrieve price or candle history of crypto assets using multiple sources',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    install_requires=['requests',
                      'appdirs',
                      'python-binance',
                      'kucoin-python'],
    keywords='eth bsc price ohlc candle history API Binance Kucoin',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
