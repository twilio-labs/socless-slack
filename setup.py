# Copyright 2018 Twilio, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
from setuptools import setup, find_packages


setup(
    name='socless-slack',
    version='1.5.0',
    description='SOCless Slack integrations',
    author='Ubani Balogun',
    classifiers=[
        'Intended Audience :: Developers :: Security',
        'Topic :: Security Orchestration :: Security Automation',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='socless security orchestration automation slack',
    packages=[],
    install_requires=[],
    tests_require=['tox']
)