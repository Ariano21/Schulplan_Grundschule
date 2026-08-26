from tests.conftest import auth_header


def test_lehrkraft_kann_keine_klasse_anlegen(client, grunddaten):
    resp = client.post(
        "/klassen",
        json={"bezeichnung": "2c", "jahrgangsstufe": 2},
        headers=auth_header(grunddaten["lehrkraft"]),
    )
    assert resp.status_code == 403


def test_lehrkraft_kann_keinen_lehrer_loeschen(client, grunddaten):
    resp = client.delete(
        f"/lehrer/{grunddaten['lehrer_b'].id}",
        headers=auth_header(grunddaten["lehrkraft"]),
    )
    assert resp.status_code == 403


def test_lehrkraft_darf_grunddaten_lesen(client, grunddaten):
    resp = client.get("/klassen", headers=auth_header(grunddaten["lehrkraft"]))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_schulleitung_kann_klasse_anlegen(client, grunddaten):
    resp = client.post(
        "/klassen",
        json={"bezeichnung": "2c", "jahrgangsstufe": 2},
        headers=auth_header(grunddaten["schulleitung"]),
    )
    assert resp.status_code == 201


def test_ohne_token_wird_abgelehnt(client, grunddaten):
    resp = client.get("/klassen")
    assert resp.status_code == 401


def test_lehrkraft_kann_keine_unterrichtseinheit_anlegen(client, grunddaten):
    resp = client.post(
        "/unterrichtseinheiten",
        json={
            "halbjahr_id": grunddaten["halbjahr"].id,
            "gruppe_id": grunddaten["gruppe_a"].id,
            "lehrer_id": grunddaten["lehrer_a"].id,
            "fach_id": grunddaten["fach"].id,
            "raum_id": grunddaten["raum_a"].id,
            "zeitslot_id": grunddaten["zeitslot"].id,
        },
        headers=auth_header(grunddaten["lehrkraft"]),
    )
    assert resp.status_code == 403


def test_grunddaten_gesperrt_wenn_halbjahr_veroeffentlicht(client, grunddaten, db_session):
    from app.models import HalbjahrStatus

    grunddaten["halbjahr"].status = HalbjahrStatus.veroeffentlicht
    db_session.add(grunddaten["halbjahr"])
    db_session.commit()

    resp = client.post(
        "/klassen",
        json={"bezeichnung": "2c", "jahrgangsstufe": 2},
        headers=auth_header(grunddaten["schulleitung"]),
    )
    assert resp.status_code == 409
