import pytest

import specatalog.models.molecules as mol
import specatalog.models.measurements as ms
import specatalog.crud_db.read as r


def test_empty_query(db_with_content):
    filter = r.MeasurementFilter()
    results = r._run_query(filter, None, db_with_content)
    assert len(results) == 6

def test_query_class(db_with_content):
    filter = r.CWEPRFilter()
    results = r._run_query(filter, None, db_with_content)
    assert len(results) == 1
    assert results[0].id == 6

def test_equals(db_with_content):
    filter = r.MeasurementFilter(temperature=50)
    results = r._run_query(filter, None, db_with_content)
    assert all(x.temperature==50 for x in results)
    assert len(results) == 2

def test_not_equals(db_with_content):
    filter = r.MoleculeFilter(id__ne="1")
    results = r._run_query(filter, None, db_with_content)
    assert len(results) == 2
    assert all(x.id != 1 for x in results)

def test_gt(db_with_content):
    filter = r.MeasurementFilter(temperature__gt=100)
    results = r._run_query(filter, None, db_with_content)
    assert len(results)==3
    assert all(x.temperature>100 for x in results)

def test_ge(db_with_content):
    filter = r.MeasurementFilter(temperature__ge=100)
    results = r._run_query(filter, None, db_with_content)
    assert len(results)==4
    assert all(x.temperature>=100 for x in results)

def test_lt(db_with_content):
    filter = r.MeasurementFilter(temperature__lt=100)
    results = r._run_query(filter, None, db_with_content)
    assert len(results)==2
    assert all(x.temperature<100 for x in results)

def test_le(db_with_content):
    filter = r.MeasurementFilter(temperature__le=100)
    results = r._run_query(filter, None, db_with_content)
    assert len(results)==3
    assert all(x.temperature<=100 for x in results)

def test_ordering_asc(db_with_content):
    filter = r.MeasurementFilter()
    ordering = r.MeasurementOrdering(temperature="asc")
    results = r._run_query(filter, ordering, db_with_content)
    temperatures = [x.temperature for x in results]
    assert temperatures == sorted(temperatures)

def test_ordering_desc(db_with_content):
    filter = r.MeasurementFilter()
    ordering = r.MeasurementOrdering(temperature="desc")
    results = r._run_query(filter, ordering, db_with_content)
    temperatures = [x.temperature for x in results]
    assert temperatures == sorted(temperatures, reverse=True)

def test_multi_ordering(db_with_content):
    filter = r.MeasurementFilter()
    ordering = r.MeasurementOrdering(temperature="asc", path="asc")
    results = r._run_query(filter, ordering, db_with_content)
    ms_id = [x.id for x in results]
    assert ms_id == [5, 2, 4, 3, 6, 1]

def test_molecule_in_measurement(db_with_content):
    filter = r.CWEPRFilter()
    results = r._run_query(filter, None, db_with_content)
    assert results[0].molecule.id == 1


def test_enum_conversion(db_with_content):
    import specatalog.helpers.allowed_values_not_adapted as av
    filter = r.MeasurementFilter(solvent=av.Solvents.toluene)
    results = r._run_query(filter, None, db_with_content)
    assert results[0].solvent == "toluene"

# TODO: In den Pydantic-Filter-Modellen fehlen für die Strings alle Operatoren wie z.B. like/ne... das korrigieren & passende tests für die str-Methoden schreiben

# TODO: Tests für like, ilike, contains