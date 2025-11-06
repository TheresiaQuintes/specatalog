from main import session
from sqlalchemy.exc import SQLAlchemyError


def safe_commit(session):
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Fehler beim Commit:", e)


def validate_enum(value, enum_cls, field_name="unknown"):
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(value)
    except ValueError:
        allowed = [e.value for e in enum_cls]
        raise ValueError(f"Ungültiger Wert '{value}' für {field_name}. Erlaubt: {allowed}")
