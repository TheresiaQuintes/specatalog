from pathlib import Path
import json
import shutil
import importlib
import sqlalchemy as alc
from importlib.resources import files


def start_gui():
    """
    Entry point für specatalog-gui
    Führt Preflight-Checks aus, bevor die GUI gestartet wird.
    """
    try:
        defaults = _ensure_and_load_defaults()
        base_path = _validate_base_path(defaults)
        _validate_allowed_values(base_path)
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
        shutil.copy(
            files("specatalog.user") / "defaults.json",
            home_defaults
        )

    try:
        with home_defaults.open("r") as f:
            return json.load(f)
    except Exception as exc:
        raise RuntimeError(
            f"Defaults-Datei konnte nicht gelesen werden:\n{home_defaults}"
        ) from exc


def _validate_base_path(defaults: dict) -> Path:
    try:
        base_path = Path(defaults["base_path"]).expanduser().resolve()
    except KeyError as exc:
        raise RuntimeError(
            "`base_path` fehlt in defaults.json"
        ) from exc

    if not base_path.exists():
        raise RuntimeError(
            f"Base-Pfad existiert nicht:\n{base_path}"
        )

    if not base_path.is_dir():
        raise RuntimeError(
            f"Base-Pfad ist kein Ordner:\n{base_path}"
        )

    return base_path


def _validate_allowed_values(base_path: Path):
    allowed_values = base_path / "allowed_values.py"

    if not allowed_values.exists():
        raise RuntimeError(
            "allowed_values.py wurde nicht gefunden:\n"
            f"{allowed_values}"
        )

    # Optional: Import-Test
    spec = importlib.util.spec_from_file_location(
        "allowed_values",
        allowed_values
    )
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise RuntimeError(
            "allowed_values.py konnte nicht importiert werden"
        ) from exc


def _check_database_connection(defaults: dict):
    try:
        usr = defaults["usr_name"]
        pwd = defaults["password"]
        db = defaults["database_url"]
    except KeyError as exc:
        raise RuntimeError(
            "Datenbank-Zugangsdaten fehlen in defaults.json"
        ) from exc

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
            "Keine Verbindung zur Datenbank möglich.\n"
            "Bitte Zugangsdaten und Server prüfen."
        ) from exc


# ─────────────────────────────
# Fehleranzeige
# ─────────────────────────────

def _show_startup_error(exc: Exception):
    """
    Zeigt einen sauberen Fehlerdialog an (Qt),
    fällt auf print() zurück, wenn Qt nicht verfügbar ist.
    """

    print("❌ Specatalog konnte nicht gestartet werden:\n")
    print(exc)
