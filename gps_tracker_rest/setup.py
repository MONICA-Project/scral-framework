from setuptools import setup, find_packages

setup(name='scral_ogc', version='1.0', packages=find_packages())
setup(name='scral_module', version='1.0', packages=find_packages(),
      install_requires=['requests', 'paho-mqtt', 'arrow', 'config_parser'])
setup(name='gps_tracker', version='1.0', packages=find_packages(), install_requires=['scral_ogc'])
setup(name='gps_tracker_rest', version='1.0', packages=find_packages(),
      install_requires=['requests', 'arrow', 'config_parser', 'flask', 'cherrypy'])
