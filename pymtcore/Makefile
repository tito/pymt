all:
	scons

clean:
	scons -c

test: all
	PYTHONPATH=src python tests/launch.py

simple:
	PYTHONPATH=src python examples/simple.py
