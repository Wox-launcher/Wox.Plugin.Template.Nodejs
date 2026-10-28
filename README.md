> For developer

    Please run `make init` to initialize the project.

# {{.Name}}

A Wox plugin template using the Node.js SDK. Wox requires Node.js 20 or later.

## Develop

Install Node.js, pnpm, Python 3 and Make, then run:

```sh
make init
make install
make test
make build
```

`make dev` rebuilds when source files change. `make lint` checks the code and `make format` formats it. The build is written to `dist/`.

## Package

```sh
make package
```

Open the resulting `.wox` file in Wox to install it. The example requires Wox 2.4.8 or later.

## Install from the store

```sh
wpm install {{.Name}}
```
