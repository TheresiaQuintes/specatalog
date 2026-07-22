from pathlib import Path
import json
import shutil
import sqlalchemy as alc
from importlib.resources import files
from specatalog.main import archive


def start_gui():
    """
    Entry point für specatalog-gui
    Führt Preflight-Checks aus, bevor die GUI gestartet wird.
    """
    try:
        defaults = _ensure_and_load_defaults()
        _validate_archive(defaults)
        _validate_allowed_values()
        _check_database_connection(defaults)
    except Exception as exc:
        _show_startup_error(exc)
        return

    # GUI erst JETZT importieren
    from specatalog.gui.SpecatalogGui import main

    main()


# ─────────────────────────────
# Preflight Checks
# ─────────────────────────────


def _ensure_and_load_defaults() -> dict:
    home_defaults = Path.home() / ".specatalog" / "defaults.json"

    if not home_defaults.exists():
        home_defaults.parent.mkdir(exist_ok=True)
        shutil.copy(files("specatalog.user") / "defaults.json", home_defaults)

    try:
        with home_defaults.open("r") as f:
            return json.load(f)
    except Exception as exc:
        raise RuntimeError(
            f"Defaults-Datei konnte nicht gelesen werden:\n{home_defaults}"
        ) from exc


def _validate_archive(defaults: dict) -> Path:
    try:
        base_path = Path(archive.archive).expanduser().resolve()
    except Exception as exc:
        raise RuntimeError(f"An exception occured during loading of the archive: {exc}")

    if not archive.exists(""):
        raise RuntimeError(f"No archive folder at:\n{base_path}")



def _validate_allowed_values():

    if not archive.exists("allowed_values.py"):
        raise RuntimeError(f"allowed_values.py could not be found at:\n{archive.archive}")

    try:
        from specatalog.main import ALLOWED_VALUES
    except Exception as exc:
        raise RuntimeError(f"An exception occured during loading of the allowed values: {exc}")


def _check_database_connection(defaults: dict):
    try:
        usr = defaults["db_usr_name"]
        pwd = defaults["db_password"]
        db = defaults["database_url"]
    except KeyError as exc:
        raise RuntimeError("Database information is missing in defaults.json") from exc

    url = f"postgresql+psycopg2://{usr}:{pwd}@{db}"

    try:
        engine = alc.create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5},
        )
        with engine.connect():
            pass
    except Exception as exc:
        raise RuntimeError(
            "No connection to database is possible.\n"
        ) from exc


# ─────────────────────────────
# Fehleranzeige
# ─────────────────────────────


def _show_startup_error(exc: Exception):
    """
    Zeigt einen sauberen Fehlerdialog an (Qt),
    fällt auf print() zurück, wenn Qt nicht verfügbar ist.
    """

    print("❌ Specatalog could not be started:\n")
    print(exc)
