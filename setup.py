from setuptools import setup

# TODO: Split server components to an "extras" optional subpackage.
setup(
    name='scalems',
    version='0',
    packages=['scalems', 'scalems._grpc', 'scalems.worker'],
    url='',
    license='',
    author='SCALE-MS team',
    author_email='',
    description='',
    requires=['googleapis-common-protos', # provides google.longrunning
              'protobuf', # provides google.protobuf
              ]
)
