setup(
	name='project1',
	version='1.0',
	author='Nicholas Cejda',
	authour_email='ncejda@ou.edu',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)
