import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.db.session import engine


def main() -> int:
    try:
        with engine.connect() as connection:
            version = connection.execute(text("SELECT VERSION()")).scalar_one()
            database = connection.execute(text("SELECT DATABASE()")).scalar_one()
        print(f"Connected to MySQL Server {version}; database={database}")
        print(f"Configured URL: {settings.DATABASE_URL.render_as_string(hide_password=True)}")
        return 0
    except SQLAlchemyError as exc:
        print(
            "MySQL connection failed. Verify that MySQL is running and DB_* values in "
            f".env are correct. Driver error: {exc}"
        )
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
