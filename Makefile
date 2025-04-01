VENV_DIR = .venv

all: $(VENV_DIR)
	$(VENV_DIR)/bin/python3 manage.py runserver

$(VENV_DIR): requirements.txt
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt
	$(VENV_DIR)/bin/python3 manage.py migrate
	cat dump.sql | $(VENV_DIR)/bin/python3 manage.py dbshell

clean:
	rm -rf $(VENV_DIR)
	rm -rf db.sqlite3

re: clean all

.PHONY: run migrate clean re