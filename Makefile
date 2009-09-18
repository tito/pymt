all:
	make -C pymtcore all

test:
	make -C pymtcore test

testimport: all
	PYTHONPATH=pymt:pymtcore/src python tests/test_import.py
