YELLOW = \033[1;33m
BLUE = \033[1;34m
GREEN = \033[1;32m
CYAN = \033[1;36m
BOLD = \033[1m
RESET = \033[0m

VENV_DIR = .venv
PYTHON_BIN = python3
SQLITE_DB = db.sqlite3
DUMP_FILE = dump.sql

define help_message =
	@echo -n "$(YELLOW)$(BOLD)[Makefile]$(RESET)"
	@echo "$(BOLD)${1}$(RESET)"
endef

all: list

list:
	@echo
	@echo "${BLUE}${BOLD}Available recipes:"
	@echo "  ${GREEN}${BOLD}list             ${CYAN}- Show this help message"
	@echo "  ${GREEN}${BOLD}up               ${CYAN}- Run the server"
	@echo "  ${GREEN}${BOLD}migrate-invoices ${CYAN}- Run migrations for invoices app"
	@echo "  ${GREEN}${BOLD}debug            ${CYAN}- Run python shell"
	@echo "  ${GREEN}${BOLD}debugdb          ${CYAN}- Run database shell"
	@echo "  ${GREEN}${BOLD}test             ${CYAN}- Run tests"
	@echo "  ${GREEN}${BOLD}clean            ${CYAN}- Clean up database"
	@echo "  ${GREEN}${BOLD}fclean           ${CYAN}- Clean up database and virtual environment"
	@echo "  ${GREEN}${BOLD}re               ${CYAN}- Clean up all and run the server"
	@echo

up: $(VENV_DIR) $(SQLITE_DB)
	$(call help_message, "Running server...")
	$(VENV_DIR)/bin/$(PYTHON_BIN) manage.py runserver

$(VENV_DIR): requirements.txt
	$(call help_message, "Creating virtual environment...")
	$(PYTHON_BIN) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

$(SQLITE_DB): $(DUMP_FILE)
	$(call help_message, "Running migrations...")
	$(VENV_DIR)/bin/$(PYTHON_BIN) manage.py migrate
	$(call help_message, "Dumping database...")
	cat dump.sql | $(VENV_DIR)/bin/$(PYTHON_BIN) manage.py dbshell

migrate-invoices:
	$(call help_message, "Running migrations...")
	$(VENV_DIR)/bin/$(PYTHON_BIN) manage.py makemigrations invoices
	$(VENV_DIR)/bin/$(PYTHON_BIN) manage.py migrate

debug:
	$(call help_message, "Running python shell...")
	$(VENV_DIR)/bin/$(PYTHON_BIN) manage.py shell

debugdb:
	$(call help_message, "Running database shell...")
	$(VENV_DIR)/bin/$(PYTHON_BIN) manage.py dbshell

test:
	$(call help_message, "Running tests...")
	$(VENV_DIR)/bin/$(PYTHON_BIN) manage.py test

clean:
	rm -rf $(SQLITE_DB)

fclean: clean
	rm -rf $(VENV_DIR)

re: fclean up

.PHONY: list up migrate-invoices debug debugdb test clean fclean re