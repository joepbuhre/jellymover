ROOT_DIR:=$(dir $(abspath $(firstword $(MAKEFILE_LIST))))

build:
	docker build . -t jellymover:dev

setdeps:
	pipreqs --encoding=utf8 --force --ignore .venv $(ROOT_DIR)

