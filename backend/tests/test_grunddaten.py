from tests.conftest import auth_header


def test_klasse_anlegen_erzeugt_standardgruppe(client, grunddaten, db_session):
    from app.models import Gruppe

    resp = client.post(
        "/klassen",
        json={"bezeichnung": "2c", "jahrgangsstufe": 2},
        headers=auth_header(grunddaten["schulleitung"]),
    )
    assert resp.status_code == 201
    klasse_id = resp.json()["id"]

    gruppen = db_session.query(Gruppe).filter(Gruppe.klasse_id == klasse_id).all()
    assert len(gruppen) == 1
    assert gruppen[0].bezeichnung == "2c"
