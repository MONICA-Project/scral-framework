from setuptools import setup, find_packages

setup(name='scral_ogc', version='1.0', packages=find_packages())
setup(name='scral_core', version='1.0', packages=find_packages(),
      install_requires=['requests', 'paho-mqtt', 'arrow', 'config_parser', 'flask', 'cherrypy'])
setup(name='phonometer_rest', version='1.0', packages=find_packages(),
      install_requires=['requests', 'paho-mqtt', 'arrow', 'config_parser'])
