from fastapi.testclient import TestClient

from main_api import app

client = TestClient(app)


def test_read_status():
    response = client.get("/status")
    assert response.status_code == 200

def test_read_status_duplicate():
    response = client.get("/status")
    assert response.json()["__ALLOW_DUPLICATE_TAGS__"] is False

def test_ip_tags():
    response = client.get("/ip-tags/10.20.30.40")
    assert response.status_code == 200
    assert response.json() == ["bar", "123 & abc & XYZ!", "SPAM"]

def test_ip_tags_not_found():
    response = client.get("/ip-tags/70.0.3.4")
    assert response.status_code == 404
    assert response.json() == {"detail": "IP not found in database."}

def test_bad_ip_tags():
    response = client.get("/ip-tags/192.o.1.1")
    assert response.status_code == 400
    assert response.json() == {"detail": "Oops! '192.o.1.1' does not appear to be an IPv4 or IPv6 network"}

def test_ip_tags_report():
    response = client.get("/ip-tags-report/10.20.30.40")
    assert response.status_code == 200

def test_bad_ip_tags_report():
    response = client.get("/ip-tags-report/192.o.1.1")
    assert response.status_code == 400
    assert response.json() == {"detail": "Oops! '192.o.1.1' does not appear to be an IPv4 or IPv6 network"}

def test_ip_tags_report_not_found():
    response = client.get("/ip-tags-report/70.0.3.4")
    assert response.status_code == 200
    assert response.content == b'<TABLE border="1"><TR><TH>Adres IP<TH>Pasuj\xc4\x85ce tagi<TR><TD rowspan="0">70.0.3.4<TD>&nbsp;</TABLE>'
