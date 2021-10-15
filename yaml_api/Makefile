PYTHONPATH = PYTHONPATH=.

# Executables
PYTHON = $(PYTHONPATH) python3
ALEMBIC = $(PYTHONPATH) alembic -c alembic.ini
# Params
DOWNGRADE_DEFAULT = -1

.PHONY: run-script migrations db_upgrade db_downgrade pretty help

run-script:  ## Запустить скрипты
	${PYTHON} -m scripts

migrations:  ## Генерация файлов миграций по изменениям моделей БД
	$(ALEMBIC) revision --autogenerate -m "$(message)"

db_upgrade:  ## Запуск миграцийы схемы БД
	$(ALEMBIC) upgrade head

db_downgrade:  ## Даунгрейд миграций, по умолчанию - к предыдущей ревизии
	$(ALEMBIC) downgrade $(DOWNGRADE_DEFAULT)

pretty:  ## "Причесать" код - isort, black, пр.
	poetry run isort .
	poetry run black .
	poetry run autoflake --in-place --verbose -r .

help:  ## Показать это сообщение
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
