# AI Medical Report Analysis System — Backend

FastAPI, SQLAlchemy 2.x, Alembic, and MySQL Community Server. Medical documents
are stored in the local upload directory; MySQL stores document references,
metadata, extracted data, analyses, prescriptions, and audit events.

> Educational prototype only. It does not diagnose, prescribe, or replace
> qualified medical advice.

## Architecture

- MySQL is the only application database. The application connects through
  PyMySQL using `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`.
  SQLAlchemy builds the URL using `URL.create`, so special characters in
  credentials are escaped correctly.
- Alembic owns schema changes. The API never calls `create_all()` and never
  drops/recreates a database on startup.
- SQLAlchemy 2.x models cover users, uploaded documents, OCR results, report
  analyses, laboratory values, prescription records/items, medical references,
  RAG metadata, and audit events. Laboratory measurements use `DECIMAL(20, 8)`
  while `value_text` and `unit` preserve the originally extracted value.
- Uploaded document binaries remain in `data/uploads`; large files are not
  stored in MySQL. OCR text uses MySQL `MEDIUMTEXT` for the configured upload
  limit and supports existing review and analysis workflows.
- RAG is replaceable and offline by default. `RETRIEVAL_MODE=local_tfidf`
  performs local lexical TF-IDF-like relevance scoring; it does not use a vector
  database or semantic embeddings. `RETRIEVAL_MODE=mock` enables deterministic
  mock retrieval for tests. Retrieval uses only reference documents explicitly
  ingested into this database; startup does not add sample references. Neither
  mode requires a paid embedding service. The
  configured local MySQL Server version is checked at startup; native MySQL
  vector search is not assumed or used.
- Gemini can be selected with `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, and
  `GEMINI_MODEL` in the backend-only `.env` file. `GEMINI_TIMEOUT_SECONDS`
  defaults to 180 seconds. The key is sent to Google in
  an HTTP header, not embedded in the request URL or frontend. Report values
  and retrieved reference passages are sent to the configured provider to generate
  explanations. Missing provider configuration and provider errors are returned
  explicitly; the application does not silently substitute mock output. Use
  `LLM_PROVIDER=mock` for offline development.

## Requirements

- Windows, macOS, or Linux
- Python 3.11+
- Locally installed and running MySQL Community Server 8.0+
- MySQL administrator credentials only for the one-time local setup (never for
  the application)
- Tesseract OCR for scanned images and PDF pages. If it is unavailable, scanned
  pages are reported as unextracted and the frontend allows manual text entry.
  Set `TESSERACT_CMD` if the executable is not on `PATH`.

## Local setup (Windows PowerShell)

Run these commands from the `backend` directory.

1. Create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. Copy the template, choose different values for `DB_PASSWORD` and
   `DB_MIGRATION_PASSWORD`, and generate a private JWT secret:

   ```powershell
   Copy-Item .env.example .env
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Put the printed value in `SECRET_KEY` in `.env`. The API refuses to start
   with a missing or short secret. `LLM_PROVIDER=mock` is the default and
   requires no paid credentials. `DATABASE_URL` in the template is illustrative;
   runtime configuration is safely built from the `DB_*` values.

3. Open `sql/mysql_setup.sql`, replace all example passwords (using the same
   application and migration passwords as in `.env`), then run the
   script in a local MySQL administrator session. For the default MySQL 8
   Windows installation:

   ```powershell
   Get-Content -Raw .\sql\mysql_setup.sql | & 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe' -u root -p
   ```

   The setup script creates `medical_report_db` and the separate
   `medical_report_test` database, plus separate local users. The application
   application user gets DML permissions only. A separate migration user gets
   DML plus schema privileges, all scoped to `medical_report_db`. Do not put
   the MySQL administrator password in `.env`.

4. Update both passwords in `.env`. Check application connectivity:

   ```powershell
   python scripts/check_db.py
   ```

   This prints the server version and selected database, but masks the password.
The API refuses to start with a missing password, unavailable database, or
missing/short JWT secret. `/ready` reports ready only when the database schema
is at the current Alembic migration head.

5. Apply schema migrations and launch the API:

   ```powershell
   alembic upgrade head
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

   Startup does not create tables or add sample reference documents; run migrations first.

   To enable Gemini, set these in `backend/.env` and restart the backend:

   ```dotenv
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-3.8-flash
   GEMINI_TIMEOUT_SECONDS=180
   ```

   Keep the key in this ignored local file; never put it in frontend variables,
   source code, or commits. Missing credentials and provider errors are returned
   explicitly. Select `LLM_PROVIDER=mock` for offline operation.

Swagger UI is at `http://127.0.0.1:8000/docs`; health and readiness endpoints
are `/health` and `/ready`.

### SQL setup commands

The included [mysql_setup.sql](./sql/mysql_setup.sql) contains the executable
setup. The equivalent core commands are:

```sql
CREATE DATABASE IF NOT EXISTS medical_report_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'medical_app'@'127.0.0.1'
  IDENTIFIED BY 'your_local_application_password';
CREATE USER IF NOT EXISTS 'medical_migrator'@'127.0.0.1'
  IDENTIFIED BY 'your_local_migration_password';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON medical_report_db.* TO 'medical_app'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES, DROP
  ON medical_report_db.* TO 'medical_migrator'@'127.0.0.1';
```

`DROP` is scoped to the application database and is required by migration
downgrades. The running API does not use the migration account.

## Migrations

```powershell
# Apply all migrations
alembic upgrade head

# Inspect the current schema revision
alembic current

# Create a migration after changing models (review it before applying)
alembic revision --autogenerate -m "describe schema change"

# Apply a specific next migration
alembic upgrade head
```

For an intentional rollback, review the migration first and then run
`alembic downgrade -1`. Keep each migration under `alembic/versions/` in source
control. Never use `Base.metadata.create_all()` as a deployment mechanism.

## Tests

The regular offline suite uses a private in-memory SQLite database and applies
the real Alembic migration chain to it. It never touches the development
database. Run from `backend`:

```powershell
pytest -v
```

For actual MySQL connectivity, migration, CRUD, constraints, rollback, and
ownership-isolation verification, point the integration tests only at the
dedicated local test database. Do not use `medical_report_db` here:

```powershell
$env:MYSQL_TEST_DATABASE_URL = 'mysql+pymysql://medical_test:URL_ENCODED_TEST_PASSWORD@127.0.0.1:3306/medical_report_test'
pytest -v tests/test_mysql_integration.py
Remove-Item Env:MYSQL_TEST_DATABASE_URL
```

URL-encode special characters in the test password.

The integration tests reject non-local hosts and database names that do not
look like test databases. They apply migrations to `medical_report_test`, and
test records are rolled back or deleted. The test suite also includes a
deliberately unreachable local port to verify database failure messages.

## Sample API requests

Register and log in, then use the returned access token:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"patient@example.test","password":"a-local-test-password"}'

curl.exe -X POST http://127.0.0.1:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"patient@example.test","password":"a-local-test-password"}'
```

Upload a report (replace `<TOKEN>` with the login response token):

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/documents/upload `
  -H "Authorization: Bearer <TOKEN>" `
  -F "file=@data/sample_reports/synthetic_cbc_report.pdf"
```

Analyze it, replacing `<DOCUMENT_ID>` with the upload response ID:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/documents/<DOCUMENT_ID>/analyze" `
  -H "Authorization: Bearer <TOKEN>"
```

## Docker option

Docker Compose runs only the API container and connects it to the locally
installed MySQL service through `host.docker.internal`. Create and configure
`backend/.env` and apply migrations on the host first. The database itself is
not containerized:

```powershell
docker compose up --build
```
