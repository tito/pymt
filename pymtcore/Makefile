all:
	swig -python -c++ -external-runtime src/pymtcore_swig.h
	scons

clean:
	scons -c

test: all
	PYTHONPATH=src python tests/launch.py --verbose
