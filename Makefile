setup: requirements.txt
	pip install -r requirements.txt

run:
	python main.py /dev/tty.usbmodem1101 8 8

run_old:
	python old_code.py