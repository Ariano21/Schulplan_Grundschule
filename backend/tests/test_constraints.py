from tests.conftest import auth_header


def _basis_payload(g):
    return {
        "halbjahr_id": g["halbjahr"].id,
        "gruppe_id": g["gruppe_a"].id,
        "lehrer_id": g["lehrer_a"].id,
        "fach_id": g["fach"].id,
        "raum_id": g["raum_a"].id,
        "zeitslot_id": g["zeitslot"].id,
    }


def test_erste_unterrichtseinheit_wird_angelegt(client, grunddaten):
    resp = client.post(
        "/unterrichtseinheiten", json=_basis_payload(grunddaten), headers=auth_header(grunddaten["schulleitung"])
    )
    assert resp.status_code == 201
    assert resp.json()["id"] > 0


def test_h1_lehrer_kollision_wird_blockiert(client, grunddaten):
    headers = auth_header(grunddaten["schulleitung"])
    client.post("/unterrichtseinheiten", json=_basis_payload(grunddaten), headers=headers)

    kollidierend = _basis_payload(grunddaten)
    kollidierend["gruppe_id"] = grunddaten["gruppe_b"].id  # andere Gruppe, gleicher Lehrer + Zeitslot
    kollidierend["raum_id"] = grunddaten["raum_b"].id

    resp = client.post("/unterrichtseinheiten", json=kollidierend, headers=headers)

    assert resp.status_code == 409
    konflikte = resp.json()["detail"]["konflikte"]
    regeln = {k["regel"] for k in konflikte}
    assert "H1" in regeln


def test_h2_gruppen_kollision_wird_blockiert(client, grunddaten):
    headers = auth_header(grunddaten["schulleitung"])
    client.post("/unterrichtseinheiten", json=_basis_payload(grunddaten), headers=headers)

    kollidierend = _basis_payload(grunddaten)
    kollidierend["lehrer_id"] = grunddaten["lehrer_b"].id  # anderer Lehrer, gleiche Gruppe + Zeitslot
    kollidierend["raum_id"] = grunddaten["raum_b"].id

    resp = client.post("/unterrichtseinheiten", json=kollidierend, headers=headers)

    assert resp.status_code == 409
    regeln = {k["regel"] for k in resp.json()["detail"]["konflikte"]}
    assert "H2" in regeln


def test_h3_raum_kollision_wird_blockiert(client, grunddaten):
    headers = auth_header(grunddaten["schulleitung"])
    client.post("/unterrichtseinheiten", json=_basis_payload(grunddaten), headers=headers)

    kollidierend = _basis_payload(grunddaten)
    kollidierend["lehrer_id"] = grunddaten["lehrer_b"].id
    kollidierend["gruppe_id"] = grunddaten["gruppe_b"].id  # anderer Lehrer + Gruppe, gleicher Raum + Zeitslot

    resp = client.post("/unterrichtseinheiten", json=kollidierend, headers=headers)

    assert resp.status_code == 409
    regeln = {k["regel"] for k in resp.json()["detail"]["konflikte"]}
    assert "H3" in regeln


def test_konfliktobjekt_verweist_auf_kollidierende_einheit(client, grunddaten):
    headers = auth_header(grunddaten["schulleitung"])
    erste = client.post("/unterrichtseinheiten", json=_basis_payload(grunddaten), headers=headers)
    erste_id = erste.json()["id"]

    kollidierend = _basis_payload(grunddaten)
    kollidierend["gruppe_id"] = grunddaten["gruppe_b"].id
    kollidierend["raum_id"] = grunddaten["raum_b"].id

    resp = client.post("/unterrichtseinheiten", json=kollidierend, headers=headers)
    konflikt = resp.json()["detail"]["konflikte"][0]
    assert konflikt["kollidierende_einheit_id"] == erste_id


def test_gleiche_gruppe_anderer_zeitslot_ist_kein_konflikt(client, grunddaten):
    headers = auth_header(grunddaten["schulleitung"])
    client.post("/unterrichtseinheiten", json=_basis_payload(grunddaten), headers=headers)

    # neuer Zeitslot am gleichen Tag, 45 Minuten später -> keine Kollision
    import datetime

    from app.database import SessionLocal
    from app.models import Zeitslot

    db = SessionLocal()
    neuer_slot = Zeitslot(
        schule_id=grunddaten["schule"].id,
        wochentag=1,
        start_zeit=datetime.time(8, 45),
        end_zeit=datetime.time(9, 30),
        ist_pause=False,
    )
    db.add(neuer_slot)
    db.commit()
    db.refresh(neuer_slot)
    db.close()

    zweite = _basis_payload(grunddaten)
    zweite["zeitslot_id"] = neuer_slot.id

    resp = client.post("/unterrichtseinheiten", json=zweite, headers=headers)
    assert resp.status_code == 201
