# Artanis AI Agent Guide

## Project Overview

Artanis is ongoing project to develop an enterprise web application platform built as a standardized 
in-house tech stack in Busana Apparel Group. It combine a python async backend with React frontend, 
using a modular subsystem architecture.  All application logic, were defined as enterprise core 
framework (ECF).

Artanis contains four project:
- The artanis platform itself located at `./src/artanis`
- Template page project for OpenAPI functionality at `./templates`
- React based Frontend at `./frontend`
- Application logic located at `./ecf`

Mostly business logic which are top level project are serviced in the Application logic folder 
located at `./ecf` while others (artanis, template, and frontend) are categorized as 
supporting platform.

---
## Commands

### Backend
```bash
# Run the server
bin/artanis -c env/conf/artanis.properties server
python -m artanis -c env/conf/artanis.properties server

# Linting / formatting
black src/ ecf/           # 100-char line length, Python 3.14 target
isort src/ ecf/           # import sorting
mypy src/                 # strict type checking (excludes fastapi/starlette/sqlalchemy/uvloop)
```

### Frontend (`cd frontend` first)
```bash
npm install
npm run dev        # Vite dev server on port 5173
npm run build      # Production build → src/artanis/asgi/templates/frontend/
npm run test       # Vitest
npm run preview    # Preview production build
```

## Architecture

### Component Layout

| Directory | Purpose |
|-----------|---------|
| `src/artanis/` | Core platform: server, config, subsystems, helpers |
| `ecf/tbl/` | ORM entities (SQLModel/SQLAlchemy) — auto-loaded on startup |
| `ecf/bo/` | Business objects |
| `ecf/api/` | API service implementations |
| `ecf/mvc/` | MVC controller implementations |
| `ecf/core/` | Shared service base classes, utilities, exceptions, startup hook |
| `ecf/res/` | Resource files: XML menu/view definitions, JSON config, reference data |
| `frontend/` | TanStack Start (React 19) app with file-based routing |
| `env/conf/` | Runtime config (`artanis.properties`) |
| `env/log/` | Log files — first place to check for errors |

### Backend Startup Sequence (`src/artanis/entrypoint.py`)
1. Load config → initialize Redis pool
2. Apply patches (`patch.py` — SQLModel integration)
3. Configure DI container (`component/`)
4. Configure database (asyncpg/PostgreSQL, auto-migrations via `setup_all()`)
5. Load ECF modules: `ecf.tbl.*` (ORM entities), `ecf.bo.*` (business objects)
6. Run `ecf.core.entrypoint:do_startup()` for app-specific init

### Subsystems (`src/artanis/subsys/`)
Each subsystem runs as an independent ASGI service managed by `SupervisorSubsystem`:
- `restapi.py` — FastAPI REST endpoints
- `interactive.py` — Server-rendered MVC
- `websocket.py` — WebSocket real-time
- `eventbus.py` — Event pub/sub (TaskIQ + Redis)
- `scheduler.py` — Cron-like scheduled tasks
- `auth.py` — LDAP3 authentication

### Data Flow
```
HTTP/WebSocket → Subsystem → ECF api/mvc Service → SQLAlchemy ORM (ecf/tbl/)
Background tasks → artanis.taskiq.broker (task_broker) → Redis queue
Events → EventBus → Redis pub/sub
```

## Code Conventions

**ORM Entities** — extend `artanis.sqlentity.sqlorm.Entity`:
```python
from artanis.sqlentity.sqlorm import Entity
from sqlmodel import Field
from sqlalchemy import String

class MyEntity(Entity, table=True):
    __tablename__ = "my_table"
    myid = Field(String(24), primary_key=True)
```

**API Services** — extend `ecf.core.apisvc.APIService` and placed the file at `./ecf/api/`:
```python
from ecf.core.apisvc import APIService

class MyService(APIService):
    description = "My endpoint"
```

**API function** - annotate with `@publish` with service path 
definition and optionally the HTTP methods [`GET`, `POST`, `PUT`, `DELETE`]: 
```python
from ecf.core.apisvc import APIService
from starlette.requests import Request

class MyService(APIService):
    description = "My endpoint"
    
    
    @published(path='/my-function', methods=["GET"])
    async def my_function(self, req: Request) -> str:
        ...
```

**MVC Services** — extend `ecf.core.mvcsvc.MVCService`

**Background Tasks** — use `task_broker`:
```python
from artanis.taskiq.broker import task_broker

@task_broker.task
async def my_task(param: str) -> None:
    ...
```

**Config access**:
```python
from artanis.config import Configuration

config = Configuration.get_default_instance(create_instance=False)
value = config.get_property_value(config.SOME_PROPERTY, default)
```

**Password hashing**: `ecf.core.ecfutils.get_hash_key()`

**Exceptions**: `ecf.core.ecfexceptions.ECFServiceError`

**Auth**: User entity at `ecf/tbl/efusrs.py`, check via `efusrs.check_user_auth()`

**Imports**: Use absolute imports; first-party packages are `artanis` and `ecf`.

**Code style**: Black 100-char lines, isort, mypy strict. Copyright headers required on source files.

## Frontend Architecture

- **Routing**: TanStack Router v1, file-based under `frontend/src/routes/`
- **Data fetching**: TanStack Query v5 + Axios (`frontend/src/services/http/`)
- **UI**: Kendo UI React (primary) + Ant Design (antd)
- **State**: React Query for server state, store in `frontend/src/store/`
- **Build output**: `src/artanis/asgi/templates/frontend/` (served by StaticSubsystem)

## Key Reference Files

- `ecf/tbl/efusrs.py` — User/auth entity
- `ecf/core/entrypoint.py` — App startup hook
- `src/artanis/server.py` — Subsystem orchestration
- `src/artanis/config.py` — Configuration singleton
- `src/artanis/taskiq/broker.py` — Task and event brokers
- `ecf/core/apisvc.py` / `ecf/core/mvcsvc.py` — Service base classes
