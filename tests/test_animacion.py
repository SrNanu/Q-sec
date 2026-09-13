"""
Tests de los datos que recibe la animacion.

La animacion pide la simulacion a /api/run-simulation y dibuja los bits que
vienen en la respuesta. Durante un tiempo esas listas llegaban vacias y la
pantalla mostraba bits generados al azar en el navegador.
"""
import pytest


@pytest.fixture
def logueado(client):
    client.post('/register', data={'username': 'animador', 'password': 'password123'})
    client.post('/login', data={'username': 'animador', 'password': 'password123'})
    return client


def ejecutar(client, **cuerpo):
    datos = {'key_length': 64, 'has_eve': False}
    datos.update(cuerpo)
    resp = client.post('/api/run-simulation', json=datos)
    assert resp.status_code == 200
    return resp.get_json()


class TestDatosDeLaAnimacion:

    def test_la_api_devuelve_los_bits_reales(self, logueado):
        datos = ejecutar(logueado)

        assert datos['success'] is True
        for campo in ('alice_bits', 'alice_bases', 'bob_bits', 'bob_bases'):
            assert len(datos[campo]) == 64, f'{campo} llego vacio o incompleto'

    def test_sin_espia_los_bits_de_bob_coinciden_con_los_de_alice(self, logueado):
        datos = ejecutar(logueado, key_length=128)

        for i in range(128):
            if datos['alice_bases'][i] == datos['bob_bases'][i]:
                assert datos['bob_bits'][i] == datos['alice_bits'][i]

    def test_con_espia_llegan_las_mediciones_de_eve(self, logueado):
        datos = ejecutar(logueado, has_eve=True)
        assert len(datos['eve_bits']) == 64
        assert len(datos['eve_bases']) == 64

    def test_sin_espia_no_llegan_mediciones_de_eve(self, logueado):
        assert ejecutar(logueado)['eve_bits'] == []

    def test_la_pagina_de_la_animacion_ya_no_inventa_bits(self, logueado):
        html = logueado.get('/animation?key_length=64&has_eve=0').data.decode()
        assert 'Math.random()' not in html
        assert 'data.alice_bits' in html and 'data.bob_bits' in html
