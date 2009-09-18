all:
	scons

clean:
	scons -c

test: all
	PYTHONPATH=src python tests/launch.py

simple: all
	PYTHONPATH=src python examples/simple.py
