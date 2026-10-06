from app import app


def test_api_relacional_includes_diversidad():
    client = app.test_client()
    response = client.get('/api/relacional?sin_bogota=true')

    assert response.status_code == 200
    data = response.get_json()
    assert 'diversidad' in data
    assert isinstance(data['diversidad'], list)

    if data['diversidad']:
        item = data['diversidad'][0]
        assert 'municipio' in item
        assert 'variedad_servicios' in item
