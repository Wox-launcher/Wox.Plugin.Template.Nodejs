.PHONY: help init check-init check-dev-deps install reinstall clean lint format build test package dev

PLUGIN_NAME := {{.Name}}

DIST_DIR := dist
SRC_DIR := src
PYTHON ?= python3
ESLINT := pnpm exec eslint
PRETTIER := pnpm exec prettier
JEST := pnpm exec jest
NCC := pnpm exec ncc
BABEL := pnpm exec babel
NODEMON := pnpm exec nodemon
POWERSHELL := powershell -NoProfile -ExecutionPolicy Bypass -Command

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
ifeq ($(OS),Windows_NT)
	$(POWERSHELL) "foreach ($$path in @('$(DIST_DIR)', 'node_modules')) { if (Test-Path $$path) { Remove-Item -Recurse -Force $$path } }"
else
	rm -rf $(DIST_DIR) ./node_modules
endif
	pnpm install

clean:
ifeq ($(OS),Windows_NT)
	$(POWERSHELL) "if (Test-Path '$(DIST_DIR)') { Remove-Item -Recurse -Force '$(DIST_DIR)' }"
else
	rm -rf $(DIST_DIR)
endif

dev: check-init check-dev-deps
	$(NODEMON) --watch $(SRC_DIR) --watch images --watch plugin.json --ext json,ts,js,mjs,png --exec "$(MAKE) build"

lint: check-init check-dev-deps
	$(ESLINT) $(SRC_DIR)

format: check-init check-dev-deps
	$(PRETTIER) --write "$(SRC_DIR)/**/*" "**/*.json" README.md

build: check-init check-dev-deps lint format
ifeq ($(OS),Windows_NT)
	$(POWERSHELL) "if (Test-Path '$(DIST_DIR)') { Remove-Item -Recurse -Force '$(DIST_DIR)' }"
else
	rm -rf $(DIST_DIR)
endif
	$(NCC) build $(SRC_DIR)/index.ts -o $(DIST_DIR)
	$(BABEL) $(DIST_DIR) --out-dir $(DIST_DIR)
ifeq ($(OS),Windows_NT)
	$(POWERSHELL) "Copy-Item 'images' -Destination '$(DIST_DIR)' -Recurse"
	$(POWERSHELL) "Copy-Item 'plugin.json' -Destination '$(DIST_DIR)'"
else
	cp -r images $(DIST_DIR)
	cp plugin.json $(DIST_DIR)
endif

test: check-init check-dev-deps
	$(JEST)

package: check-init build
ifeq ($(OS),Windows_NT)
	$(POWERSHELL) "if (Test-Path 'wox.plugin.$(PLUGIN_NAME).zip') { Remove-Item -Force 'wox.plugin.$(PLUGIN_NAME).zip' }; if (Test-Path 'wox.plugin.$(PLUGIN_NAME).wox') { Remove-Item -Force 'wox.plugin.$(PLUGIN_NAME).wox' }; Compress-Archive -Path '$(DIST_DIR)\\*' -DestinationPath 'wox.plugin.$(PLUGIN_NAME).zip'; Move-Item 'wox.plugin.$(PLUGIN_NAME).zip' 'wox.plugin.$(PLUGIN_NAME).wox'"
	$(POWERSHELL) "if (Test-Path '$(DIST_DIR)') { Remove-Item -Recurse -Force '$(DIST_DIR)' }"
else
	cd $(DIST_DIR) && zip -r ../wox.plugin.$(PLUGIN_NAME).wox .
	rm -rf $(DIST_DIR)
endif
