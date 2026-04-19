# Artanis AI Agent Guide

## Architecture Overview
Artanis is an enterprise web platform with a Python backend (FastAPI/SQLAlchemy) and React frontend (TanStack Start). The backend uses a modular subsystem architecture with multiprocessing workers. The ECF (Enterprise Component Framework) provides ORM entities (`ecf/tbl/`), business objects (`ecf/bo/`), and service layers.

Key components:
- `src/artanis/`: Core platform (server, config, subsystems like ASGI, REST API, WebSocket)
- `ecf/`: Framework modules (entities in `tbl/`, services in `api/`, common in `core/`)
- `frontend/`: TanStack Start React app with file-based routing

Data flows from REST/WebSocket endpoints through ECF services to SQLAlchemy entities, with background tasks via TaskIQ/Redis.

## Critical Workflows
- **Backend startup**: `bin/artanis` or `python -m artanis` loads config, configures DB (asyncpg), loads ECF modules (`ecf.tbl`, `ecf.bo`), starts subsystems
- **Frontend dev**: `cd frontend && npm run dev` (Vite server)
- **Build**: Python via PDM (`pyproject.toml`), frontend `npm run build`
- **Debugging**: Check `env/log/`, use `ecf.core.ecfexceptions.ECFServiceError` for errors
- **Database**: Auto-migrates via `artanis.sqlentity.entrypoint.setup_all()` on startup

## Project Conventions
- **ORM**: Extend `artanis.sqlentity.sqlorm.Entity`, fields like `efususid = Field(String(24), primary_key=True)`
- **Services**: API services extend `ecf.core.apisvc.APIService`, MVC extend `ecf.core.mvcsvc.MVCService`
- **Tasks**: Use `artanis.taskiq.broker.task_broker` for background jobs
- **Hashing**: `ecf.core.ecfutils.get_hash_key()` for passwords
- **Config**: Properties in `env/conf/artanis.properties`, accessed via `artanis.config.Configuration`
- **Imports**: First-party `artanis`, `ecf`; use absolute imports
- **Code style**: Black (100 chars), isort, mypy strict; copyright headers required

## Integration Points
- **Database**: PostgreSQL via asyncpg, entities auto-loaded from `ecf.tbl.*`
- **Tasks**: Redis via taskiq-redis, broker in `artanis.taskiq.broker`
- **Frontend**: TanStack Router for routing, server functions for API calls
- **Auth**: User entities in `ecf.tbl.efusrs`, check via `efusrs.check_user_auth()`

Reference: `ecf/tbl/efusrs.py` (user model), `ecf/core/entrypoint.py` (startup), `src/artanis/server.py` (subsystems)</content>
<parameter name="filePath">/data/u01/projects/BAG/artanis/AGENTS.md
