try:
    import setuptools
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION='0.1.0'

setup(
    name='pyhelmmanager',
    packages=setuptools.find_packages(),
    package_data={'pyhelmmanager': ['helm_templates/*.j2']},
    install_requires=['requests', 'docopt', 'jinja2', 'jq', 'tqdm', 'pyyaml', 'numpy'],
    version=VERSION,
    description='create helm charts with template',
    author='Allan',
    author_email='hung.allan@gmail.com',
    url='https://github.com/hungallan/pyhelmmanager',
    download_url='https://github.com/hungallan/pyhelmmanager/tarball/' + VERSION,
    keywords=['utility', 'miscellaneous', 'library'],
    classifiers=[],
    entry_points={                                                                                                                                                                                                                                                             
        'console_scripts': [                                                                                                                                                                                                                                                   
            'pyhelmmanager = pyhelmmanager.pyhelmmanager:main',                                                                                                                                                                                                                          
        ]
    }
)
