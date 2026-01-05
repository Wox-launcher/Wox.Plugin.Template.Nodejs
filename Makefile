.PHONY: help install clean build publish test lint format

DIST_DIR := dist
SRC_DIR := src
PLUGIN_NAME := $(shell node -p "require('./package.json').name")

help:
	@echo "Available commands:"
	@echo "  make install  - Install project dependencies"
	@echo "  make clean    - Clean build directory"
	@echo "  make build    - Build project"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code"
	@echo "  make package  - Build and package plugin"

install:
	pnpm install

clean:
	pnpm run clean

lint:
	pnpm run lint
	pnpm run prettier:check

format:
	pnpm run prettier:write

build: lint format
	pnpm run build

test:
	pnpm test

package: build
	cd $(DIST_DIR) && zip -r ../wox.plugin.$(PLUGIN_NAME).wox .
	@echo "Plugin packaged to wox.plugin.$(PLUGIN_NAME).wox"
