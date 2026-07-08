import specatalog.crud_db.update as up
import specatalog.models.measurements as ms
import specatalog.models.molecules as mol


def test_update_one(db_with_content):
    entry = db_with_content.query(ms.CWEPR).first()
    update_model = up.CWEPRUpdate(attenuation="25dB")
    up._update_model(entry, update_model, db_with_content)
    entry_new = db_with_content.query(ms.CWEPR).first()
    assert entry_new.attenuation == "25dB"


def test_update_two(db_with_content):
    entry = db_with_content.query(ms.CWEPR).first()
    update_model = up.CWEPRUpdate(attenuation="25dB", temperature=298)
    up._update_model(entry, update_model, db_with_content)
    entry_new = db_with_content.query(ms.CWEPR).first()
    assert entry_new.attenuation == "25dB"
    assert entry_new.temperature == 298


def test_update_enum(db_with_content):
    import specatalog.helpers.allowed_values_not_adapted as av

    entry = db_with_content.query(ms.CWEPR).first()
    update_model = up.CWEPRUpdate(frequency_band=av.FrequencyBands.q)
    up._update_model(entry, update_model, db_with_content)
    entry_new = db_with_content.query(ms.CWEPR).first()
    assert entry_new.frequency_band == "q"


def test_update_name(db_with_content):
    import specatalog.helpers.allowed_values_not_adapted as av

    entry = db_with_content.query(mol.TDP).first()
    update_model = up.TDPUpdate(
        doublet=av.Doublets.no1, linker=av.Linker.bi, chromophore=av.Chromophores.bdp0
    )
    up._update_model(entry, update_model, db_with_content)
    entry_new = db_with_content.query(mol.TDP).first()
    assert entry_new.name == "bdp0-bi-no1"


# TODO: _automatic_name_update testen
# TODO: read/update von date-Feldern?
