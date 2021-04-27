setup: virtualenv/bin/activate virtualenv/lib/python3.9/.installed

virtualenv/bin/activate:
	virtualenv -p python3.9 virtualenv

virtualenv/.pip-21.0.1-installed: virtualenv/bin/activate
	./virtualenv/bin/pip install --index-url=https://pypi.python.org/simple/ pip==21.0.1 && touch $@

virtualenv/lib/python3.9/.installed: virtualenv/bin/activate virtualenv/.pip-21.0.1-installed
	 . ./virtualenv/bin/activate && pip install -r ./requirements.txt && touch virtualenv/lib/python3.9/.installed && python manage.py migrate

run:
	python manage.py runserver

clean:
	rm -rf virtualenv
	@echo "Cleaned."