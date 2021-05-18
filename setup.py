# SPDX-License-Identifier: MIT
from bobber import __version__
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='nvidia-bobber',
    version=__version__,
    description='Containerized testing of system components that impact AI workload performance',
    long_description=long_description,
    packages=['bobber',
              'bobber/lib',
              'bobber/lib/analysis',
              'bobber/lib/docker',
              'bobber/lib/system',
              'bobber/lib/tests'],
    include_package_data=True,
    package_data={'': ['lib/docker/Dockerfile',
                       'test_scripts/call_dali_multi.sh',
                       'test_scripts/dali_multi.sh',
                       'test_scripts/fio_fill_single.sh',
                       'test_scripts/fio_multi.sh',
                       'test_scripts/mdtest_multi.sh',
                       'test_scripts/nccl_multi.sh',
                       'test_scripts/setup_fio.sh']},
    license='MIT',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['bobber=bobber.bobber:main']
    },
    install_requires=[
        'docker >= 4.3.1',
        'numpy >= 1.9.5',
        'pyyaml >= 5.4.0',
        'tabulate >= 0.8.7',
        'six>=1.15.0'
    ]
)
