import specatalog.crud_db.delete as d
import specatalog.crud_db.read as r
from contextlib import contextmanager
import pytest


def test_delete_object(db_with_content, db_session):
    filter = r.MeasurementFilter(id=1)
    results = r._run_query(filter, None, db_with_content)
    if len(results) == 1:
        obj = results[0]
        d._delete_object(obj, db_session)

        results_new = r._run_query(filter, None, db_with_content)
        assert len(results_new) == 0
    else:
        assert False

def test_delete_molecule(db_with_content):
    import specatalog.crud_db.delete as de

    @contextmanager
    def session_context():
        yield db_with_content

    de.db_session = session_context

    
    de.delete_molecule(1)
    filter_mol = r.MoleculeFilter(id=1)
    filter_ms = r.MeasurementFilter(molecular_id=1)

    results_mol = r._run_query(filter_mol, None, db_with_content)
    results_ms = r._run_query(filter_ms, None, db_with_content)

    assert len(results_mol) == 0
    assert len(results_ms) == 0


def test_delete_non_existent_molecule(db_with_content):
    import specatalog.crud_db.delete as de

    @contextmanager
    def session_context():
        yield db_with_content

    de.db_session = session_context
    with pytest.raises(ValueError):
        de.delete_molecule(6)

def test_delete_measurement(db_with_content):
    import specatalog.crud_db.delete as de

    @contextmanager
    def session_context():
        yield db_with_content

    de.db_session = session_context
    
    de.delete_measurement(1)

    filter_ms = r.MeasurementFilter(id=1)
    results_ms = r._run_query(filter_ms, None, db_with_content)

    assert len(results_ms) == 0

def test_delete_non_existent_measurement(db_with_content):
    import specatalog.crud_db.delete as de
    @contextmanager
    def session_context():
        yield db_with_content
    de.db_session = session_context

    with pytest.raises(ValueError):
        de.delete_measurement(26)