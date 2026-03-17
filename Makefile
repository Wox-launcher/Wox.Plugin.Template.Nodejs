.PHONY: help init check-init check-dev-deps install reinstall clean lint format build test package dev

DIST_DIR := dist
SRC_DIR := src
PYTHON ?= python3
PLUGIN_NAME := {{.Name}}
BIN_DIR := ./node_modules/.bin
ESLINT := $(BIN_DIR)/eslint
PRETTIER := $(BIN_DIR)/prettier
JEST := $(BIN_DIR)/jest
NCC := $(BIN_DIR)/ncc
BABEL := $(BIN_DIR)/babel
NODEMON := $(BIN_DIR)/nodemon

help:
	@echo "Available commands:"
	@echo "  make init     - Initialize template values interactively"
	@echo "  make install  - Install project dependencies"
	@echo "  make reinstall - Reinstall project dependencies from scratch"
	@echo "  make clean    - Clean build directory"
	@echo "  make build    - Build project"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code"
	@echo "  make package  - Build and package plugin"

init:
	$(PYTHON) scripts/init-wox-project.py

check-init:
	@$(PYTHON) scripts/init-wox-project.py --check-initialized

check-dev-deps:
	@node -e 'const missing = []; for (const name of ["eslint", "prettier", "jest", "@vercel/ncc", "@babel/cli", "nodemon"]) { try { require.resolve(name); } catch { missing.push(name); } } if (missing.length) { console.error("Development dependencies are not installed. Run '\''make install'\'' first."); console.error("Missing packages: " + missing.join(", ")); process.exit(1); }'

install: check-init
	pnpm install

reinstall: check-init
	rm -rf $(DIST_DIR) ./node_modules
	pnpm install

clean:
	rm -rf $(DIST_DIR)

dev: check-init check-dev-deps
	$(NODEMON) --watch $(SRC_DIR) --watch images --watch plugin.json --ext json,ts,js,mjs,png --exec "$(MAKE) build"

lint: check-init check-dev-deps
	$(ESLINT) $(SRC_DIR)

format: check-init check-dev-deps
	$(PRETTIER) --write "$(SRC_DIR)/**/*" "**/*.json" README.md

build: check-init check-dev-deps lint format
	rm -rf $(DIST_DIR)
	$(NCC) build $(SRC_DIR)/index.ts -o $(DIST_DIR)
	$(BABEL) $(DIST_DIR) --out-dir $(DIST_DIR)
	cp -r images $(DIST_DIR)
	cp plugin.json $(DIST_DIR)

test: check-init check-dev-deps
	$(JEST)

package: check-init build
	cd $(DIST_DIR) && zip -r ../wox.plugin.$(PLUGIN_NAME).wox .
	rm -rf $(DIST_DIR)
	@echo "Plugin packaged to wox.plugin.$(PLUGIN_NAME).wox"
