from setuptools import setup, find_packages

setup(name='scral_ogc', version='1.0', packages=find_packages())
setup(name='scral_core', version='1.0', packages=find_packages(),
      install_requires=['requests', 'paho-mqtt', 'arrow', 'config_parser'])
setup(name='sound_level_meter', version='1.0', packages=find_packages(),
      install_requires=['requests', 'paho-mqtt', 'arrow', 'config_parser', 'flask', 'cherrypy', 'urllib3'])
