SHELL := bash
.SHELLFLAGS := -eux -o pipefail -c
MAKEFLAGS += --no-builtin-rules

.DEFAULT_GOAL := help
.PHONY: help run watch build test test-cov stop ps shell logs revision migrate

# Fix docker build and docker compose build using different backends
COMPOSE_DOCKER_CLI_BUILD = 1
DOCKER_BUILDKIT = 1
# Fix docker build on M1/M2
DOCKER_DEFAULT_PLATFORM = linux/amd64


run: ## Запуск/перезапуск проекта локально в docker compose со сборкой образов
	docker compose up --build --wait;

revision: ## Сгенерировать новую ревизию
	docker compose run --rm --build api alembic revision --autogenerate -m "$(msg)"

migrate: ## Накатить миграции на
	docker compose run --rm --build api alembic upgrade head

clear: ## Удалить все лишние артефакты докера (не только этого проекта)
	docker system prune -f --volumes
