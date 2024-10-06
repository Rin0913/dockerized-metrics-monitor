.PHONY: up down restart

DOCKER_COMPOSE := $(shell if [ -x "$$(command -v docker-compose)" ]; then echo "docker-compose"; else echo "docker compose"; fi)

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart: down up
