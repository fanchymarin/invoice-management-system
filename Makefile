YELLOW = \033[1;33m
BOLD = \033[1m
RESET = \033[0m
VENV_DIR = .venv

define help_message =
	@echo -n "$(YELLOW)$(BOLD)[Makefile]$(RESET)"
	@echo "$(BOLD)${1}$(RESET)"
endef

all: $(VENV_DIR)
	$(call help_message, "Running server...")
	$(VENV_DIR)/bin/python3 manage.py runserver

$(VENV_DIR): requirements.txt
	$(call help_message, "Creating virtual environment...")
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt
	$(call help_message, "Running migrations...")
	$(VENV_DIR)/bin/python3 manage.py migrate
	$(call help_message, "Dumping database...")
	cat dump.sql | $(VENV_DIR)/bin/python3 manage.py dbshell

migrate:
	$(call help_message, "Running migrations...")
	$(VENV_DIR)/bin/python3 manage.py makemigrations invoices
	$(VENV_DIR)/bin/python3 manage.py migrate

debug:
	$(call help_message, "Running python shell...")
	$(VENV_DIR)/bin/python3 manage.py shell

debugdb:
	$(call help_message, "Running database shell...")
	$(VENV_DIR)/bin/python3 manage.py dbshell

clean:
	rm -rf $(VENV_DIR)
	rm -rf db.sqlite3

re: clean all

.PHONY: run migrate debug debugdb clean re