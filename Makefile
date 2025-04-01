VENV_DIR = .venv

run: setup
	$(VENV_DIR)/bin/python3 manage.py runserver

setup: venv migrate

venv: requirements.txt
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

migrate:
	$(VENV_DIR)/bin/python3 manage.py migrate

clean:
	rm -rf $(VENV_DIR)
	rm -rf db.sqlite3

.PHONY: run setup venv migrate clean