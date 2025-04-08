YELLOW = \033[1;33m
BLUE = \033[1;34m
GREEN = \033[1;32m
CYAN = \033[1;36m
BOLD = \033[1m
RESET = \033[0m

PROJECT_NAME = revving-app

define help_message =
	@echo -n "$(YELLOW)$(BOLD)[Makefile]$(RESET)"
	@echo "$(BOLD)${1}$(RESET)"
endef

include .env

all: list

list:
	@echo
	@echo "${BLUE}${BOLD}Available recipes:"
	@echo "  ${GREEN}${BOLD}list             ${CYAN}- Show this help message"
	@echo "  ${GREEN}${BOLD}up               ${CYAN}- Run the containerized application"
	@echo "  ${GREEN}${BOLD}build            ${CYAN}- Build the container image"
	@echo "  ${GREEN}${BOLD}down             ${CYAN}- Stop the containerized application"
	@echo "  ${GREEN}${BOLD}test             ${CYAN}- Run tests in the containerized application"
	@echo "  ${GREEN}${BOLD}clean            ${CYAN}- Stop and remove the database volume"
	@echo "  ${GREEN}${BOLD}fclean           ${CYAN}- Stop and remove all containers and volumes"
	@echo "  ${GREEN}${BOLD}re               ${CYAN}- Clean up all and run the containerized application"
	@echo

up: build
	$(call help_message, "Running the containerized application...")
	docker compose --project-name=${PROJECT_NAME} up -d
	$(call help_message, "Waiting for application to be ready...")
	@until docker compose --project-name=${PROJECT_NAME} exec django curl -sSf "http://localhost:8000" >/dev/null 2>&1; do \
		echo -n "$(YELLOW)$(BOLD)[Makefile]$(RESET)" ; \
		echo " $(BOLD)...$(RESET)" ; \
		sleep 3 ; \
	done
	$(call help_message, "Application is ready!")
	$(call help_message, "You can access it at http://localhost:${DJANGO_PORT}")

build:
	$(call help_message, "Building the container image...")
	docker compose --project-name=${PROJECT_NAME} build

down:
	$(call help_message, "Stopping the containerized application...")
	docker compose --project-name=${PROJECT_NAME} down

test: up
	$(call help_message, "Running tests from container...")
	docker compose --project-name=${PROJECT_NAME} exec django make test

clean: down
	$(call help_message, "Removing the database volume...")
	docker volume rm -f ${PROJECT_NAME}_postgres-data

fclean: clean
	$(call help_message, "Removing container image...")
	docker rmi -f ${PROJECT_NAME}-django

re: fclean up

.PHONY: all list up build down test clean fclean re