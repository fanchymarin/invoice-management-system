YELLOW = \033[1;33m
BLUE = \033[1;34m
GREEN = \033[1;32m
CYAN = \033[1;36m
BOLD = \033[1m
RESET = \033[0m

PYTHON_BIN = python
DUMP_FILE = dump.sql.postgres

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
	@echo "  ${GREEN}${BOLD}setup            ${CYAN}- Create virtual environment and install dependencies"
	@echo "  ${GREEN}${BOLD}shell            ${CYAN}- Run python shell"
	@echo "  ${GREEN}${BOLD}dbshell          ${CYAN}- Run database shell"
	@echo "  ${GREEN}${BOLD}test             ${CYAN}- Run tests"
	@echo "  ${GREEN}${BOLD}clean            ${CYAN}- Clean up database"
	@echo "  ${GREEN}${BOLD}fclean           ${CYAN}- Clean up database and virtual environment"
	@echo "  ${GREEN}${BOLD}re               ${CYAN}- Clean up all and run the server"
	@echo

up: setup
	$(call help_message, "Running server...")
	$(PYTHON_BIN) manage.py runserver 0.0.0.0:8000

setup: $(DUMP_FILE)
	$(call help_message, "Installing python dependencies...")
	pip install --no-cache-dir -r requirements.txt
	$(call help_message, "Running migrations...")
	$(PYTHON_BIN) manage.py makemigrations --noinput
	$(PYTHON_BIN) manage.py migrate
	$(call help_message, "Dumping database...")
	$(PYTHON_BIN) manage.py dbshell < $(DUMP_FILE)
	$(call help_message, "Creating superuser...")
	$(PYTHON_BIN) manage.py createsuperuser --noinput || true
	$(call help_message, "Creating users...")
	$(PYTHON_BIN) manage.py shell < create_users.py

shell: setup
	$(call help_message, "Running python shell...")
	$(PYTHON_BIN) manage.py shell

dbshell:
	$(call help_message, "Running database shell...")
	$(PYTHON_BIN) manage.py dbshell

test:
	$(call help_message, "Running tests...")
	$(PYTHON_BIN) manage.py test

clean:
	$(call help_message, "Cleaning up database...")
	$(PYTHON_BIN) manage.py flush --no-input

fclean: clean
	$(call help_message, "Cleaning up migrations and python cache files...")
	git init
	git clean -Xfd
	rm -rf .git	

re: fclean up

.PHONY: list up setup shell dbshell test clean fclean re