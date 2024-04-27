migrate:
	venv\scripts\python -m alembic revision --autogenerate
	venv\scripts\python -m alembic upgrade head

run:
	venv\scripts\python -m uvicorn main:app --reload