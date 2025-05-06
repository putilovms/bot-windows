PORT ?= 8080
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) app:app

dev:
	uv run app.py