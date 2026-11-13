# School system preview

A small, runnable prototype of a school portal. It includes an overview dashboard, student directory, course list, assignments, and an attendance form. Demo records are fictional and are created automatically on first run.

## Run it locally

Requirements: Python 3.10 or newer.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app run --debug
```

Open <http://127.0.0.1:5000>. The local preview uses SQLite and saves data in `school_demo.db`. Stop the server with Ctrl+C. To reset the demo data, stop the server and delete `school_demo.db`; it will be recreated on the next run.

## Render hosting and PostgreSQL

The included `render.yaml` describes a Render web service and managed PostgreSQL database. To deploy, connect this GitHub repository to a Render account and create a Blueprint from `render.yaml`. Render account access and any applicable hosting charges are managed by you; this repository change does not create hosting resources or publish a live site.

## Important limitations

This is a feature preview, not a production-ready student information system. It intentionally has no login or role-based access control. Do not enter real student data or expose it publicly. Before using it for a school, add authentication, authorization, audit logging, privacy/retention controls, secure backups, and security testing. The local demo uses SQLite; the Render config uses PostgreSQL.
