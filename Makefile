# Makefile for Django “Kitoblarda_2” loyihasi

VENV      := .venv
PYTHON    := $(VENV)/bin/python
PIP       := $(VENV)/bin/pip
PROJECT_DIR := .
PORT      ?= 8000

.PHONY: help venv install update-requirements makemigrations migrate mig runserver \
        createsuperuser shell test lint clean

help:
	@echo "Makefile yordamchi:"
	@echo ""
	@echo "  make venv                     # Virtualenv yaratadi (agar yo‘q bo‘lsa)"
	@echo "  make install                  # venv yaratib, pip-paketlarni o'rnatadi"
	@echo "  make update-requirements     # requirements.txt yangilaydi"
	@echo "  make makemigrations           # Django makemigrations-ni bajaradi"
	@echo "  make migrate                  # Django migrate-ni bajaradi"
	@echo "  make mig                      # makemigrations → migrate ketma-ket bajaradi"
	@echo "  make runserver                # Django serverni ishga tushiradi"
	@echo "  make createsuperuser          # Django superuser yaratish"
	@echo "  make shell                    # Django shell ochadi"
	@echo "  make test                     # Testlarni ishga tushiradi"
	@echo "  make lint                     # Lint tekshiruvini ishga tushiradi"
	@echo "  make clean                    # .pyc va __pycache__ fayllarni o‘chiradi"

venv:
	@echo "==> Virtualenv tekshirilmoqda..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "    → Virtualenv mavjud emas. Yaratilyapti…"; \
		python3 -m venv $(VENV); \
		echo "    → Virtualenv yaratildi: $(VENV)"; \
	else \
		echo "    → Virtualenv allaqachon mavjud: $(VENV)"; \
	fi

install: venv
	@echo "==> pip-paketlarni o‘rnatish boshlandi…"
	@$(PIP) install --upgrade pip
	@if [ -f "requirements.txt" ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		echo "    ! requirements.txt topilmadi."; \
	fi
	@echo "    → O‘rnatish tugadi."

update-requirements: venv
	@echo "==> requirements.txt yangilanmoqda…"
	@$(PIP) freeze > requirements.txt
	@echo "    → requirements.txt yangilandi."

makemigrations: venv
	@echo "==> Django makemigrations boshlanyapti…"
	@$(PYTHON) $(PROJECT_DIR)/manage.py makemigrations
	@echo "    → makemigrations tugadi."

migrate: venv
	@echo "==> Django migrate boshlanyapti…"
	@$(PYTHON) $(PROJECT_DIR)/manage.py migrate
	@echo "    → migrate tugadi."

.PHONY: mig
mig: makemigrations migrate

runserver: venv mig
	@echo "==> Django serverni ishga tushiryapti (0.0.0.0:$(PORT))…"
	@$(PYTHON) $(PROJECT_DIR)/manage.py runserver 0.0.0.0:$(PORT)

createsuperuser: venv
	@echo "==> Django superuser yaratish interaktiv rejimda…"
	@$(PYTHON) $(PROJECT_DIR)/manage.py createsuperuser

shell: venv
	@$(PYTHON) $(PROJECT_DIR)/manage.py shell

test: venv
	@echo "==> Testlarni ishga tushiryapti…"
	@$(PYTHON) $(PROJECT_DIR)/manage.py test
	@echo "    → Testlar tugadi."

lint: venv
	@echo "==> Lint tekshiruvi (flake8) boshlandi…"
	@if command -v flake8 > /dev/null; then \
		flake8 . ; \
	else \
		echo "    ! flake8 o‘rnatilmagan."; \
	fi

clean:
	@echo "==> __pycache__ va .pyc fayllarni o‘chirilyapti…"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "    → Tozalash tugadi."
