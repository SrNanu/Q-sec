"""
Tests del repositorio de usuarios.
"""
import sqlite3

from werkzeug.security import generate_password_hash

from app import create_app
from config import TestingConfig
from datos import user_repository


def _base_con_usernames_duplicados(ruta):
    """Una base sin el índice unique de username: el mismo escenario que
    tendría cualquier qsec.db creado antes de que ese índice existiera."""
    con = sqlite3.connect(ruta)
    con.executescript("""
        CREATE TABLE user (
            id INTEGER NOT NULL,
            username VARCHAR(80) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME,
            PRIMARY KEY (id)
        );
    """)
    for id_ in (1, 2):
        con.execute(
            'INSERT INTO user (id, username, password_hash) VALUES (?, ?, ?)',
            (id_, 'duplicado', generate_password_hash('password123')),
        )
    con.commit()
    con.close()


def _app_sobre(ruta):
    class ConfigArchivo(TestingConfig):
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{ruta}'
    return create_app(ConfigArchivo)


class TestUsernameDuplicado:
    """Regresión: get_user_by_username no puede reventar con
    MultipleResultsFound si una base vieja tiene usernames repetidos, algo
    que la migración automática no puede corregir (no borra ni fusiona
    filas)."""

    def test_no_revienta_con_usernames_duplicados(self, tmp_path):
        ruta = tmp_path / 'qsec.db'
        _base_con_usernames_duplicados(ruta)

        app = _app_sobre(ruta)
        with app.app_context():
            usuario = user_repository.get_user_by_username('duplicado')
            assert usuario is not None

    def test_el_login_por_la_web_no_devuelve_500(self, tmp_path):
        ruta = tmp_path / 'qsec.db'
        _base_con_usernames_duplicados(ruta)

        client = _app_sobre(ruta).test_client()
        resp = client.post(
            '/login',
            data={'username': 'duplicado', 'password': 'password123'},
            follow_redirects=True,
        )
        assert resp.status_code == 200
