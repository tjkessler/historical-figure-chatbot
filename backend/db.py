import glob
import os
import yaml

from contextlib import contextmanager
import sqlite3

from backend.config import DB_PATH


@contextmanager
def get_db():
    """
    Context manager for SQLite database connection.

    Yields
    ------
    sqlite3.Connection
        A connection to the SQLite database.
    """

    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Initialize the SQLite database by executing the schema script.
    """

    with get_db() as conn:
        with open(os.path.join(
            os.path.dirname(__file__), "schema.sql"
         ), "r") as f:
            conn.executescript(f.read())
        conn.commit()


def populate_personas_from_yaml():
    """
    Populate the personas table in the database with data from YAML files in
    the personas directory.
    """

    personas_dir = os.path.join(os.path.dirname(__file__), "../personas")
    yaml_files = glob.glob(os.path.join(personas_dir, "*.yaml"))
    with get_db() as conn:
        for yfile in yaml_files:
            with open(yfile, "r") as f:
                data = yaml.safe_load(f)
                name = data.get("name", "")
                era = data.get("era", "")
                bio = data.get("bio", "")
                # Check if persona already exists by name
                cur = conn.execute(
                    "SELECT id FROM personas WHERE name = ?",
                    (name,)
                )
                if not cur.fetchone():
                    conn.execute(
                        "INSERT INTO personas (name, era, bio) VALUES (?, ?, ?)",
                        (name, era, bio)
                    )
        conn.commit()
