from setuptools import setup

setup(
	name = 'Tristo Mietitore',
	version = '0.1',
	description = 'A tool to distribute and collect practice and exam assignements',
	author = 'Massimo Santini',
	author_email = 'santini@di.unimi.it',
	url = 'http://santini.di.unimi.it/',
	packages = [ 'tm', ],
	include_package_data = True,
	install_requires = [ "Flask>=0.9", ],
	entry_points = {
		'console_scripts': [
			'tm-mkconf = tm.mkconf:main',
			'tm-debug = tm.web:main'
			]
		}
)
