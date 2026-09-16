"""
Tests de la actualización automática del esquema.

Simulan a un integrante del equipo que ya tenía un qsec.db creado con el modelo
anterior y actualiza el código: la aplicación tiene que seguir funcionando con
sus datos, sin que tenga que borrar la base ni correr nada a mano.
"""
import sqlite3

from sqlalchemy import inspect

from app import create_app
from config import TestingConfig
from datos import db, user_repository
from datos.esquema import agregar_columnas_faltantes

# Esquema tal como lo creaba la versión anterior del modelo (sin user.created_at)
ESQUEMA_ANTERIOR = """
CREATE TABLE user (
    id INTEGER NOT NULL,
    username VARCHAR(80) NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_user_username ON user (username);
CREATE TABLE simulation_session (
    id INTEGER NOT NULL,
    key_length INTEGER NOT NULL,
    has_eve BOOLEAN NOT NULL,
    result VARCHAR(50) NOT NULL,
    final_key TEXT,
    error_rate FLOAT,
    timestamp DATETIME NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES user (id)
);
"""


def _base_anterior(ruta):
    """Crea una base con el esquema viejo y un usuario con una simulación."""
    from werkzeug.security import generate_password_hash

    con = sqlite3.connect(ruta)
    con.executescript(ESQUEMA_ANTERIOR)
    con.execute(
        'INSERT INTO user (id, username, password_hash) VALUES (1, ?, ?)',
        ('veterano', generate_password_hash('password123')),
    )
    con.execute(
        "INSERT INTO simulation_session (key_length, has_eve, result, final_key, "
        "error_rate, timestamp, user_id) VALUES (256, 0, 'secure', '0101', 0.0, "
        "'2025-11-01 10:00:00', 1)"
    )
    con.commit()
    con.close()


def _app_sobre(ruta):
    class ConfigArchivo(TestingConfig):
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{ruta}'
    return create_app(ConfigArchivo)


class TestBaseExistente:

    def test_la_app_arranca_sobre_una_base_vieja_y_agrega_las_columnas(self, tmp_path):
        ruta = tmp_path / 'qsec.db'
        _base_anterior(ruta)

        app = _app_sobre(ruta)

        with app.app_context():
            columnas = {c['name'] for c in inspect(db.engine).get_columns('user')}
            assert 'created_at' in columnas
            columnas = {c['name'] for c in inspect(db.engine).get_columns('simulation_session')}
            assert {'sifted_length', 'sample_size'} <= columnas

    def test_los_datos_existentes_se_conservan(self, tmp_path):
        ruta = tmp_path / 'qsec.db'
        _base_anterior(ruta)

        app = _app_sobre(ruta)

        with app.app_context():
            usuario = user_repository.verify_user_password('veterano', 'password123')
            assert usuario is not None, 'el usuario existente ya no puede entrar'
            assert usuario.created_at is None  # las filas viejas quedan vacías
            assert len(usuario.sessions) == 1

    def test_el_login_por_la_web_sigue_funcionando(self, tmp_path):
        ruta = tmp_path / 'qsec.db'
        _base_anterior(ruta)

        client = _app_sobre(ruta).test_client()
        resp = client.post('/login', data={'username': 'veterano', 'password': 'password123'},
                           follow_redirects=True)
        assert resp.status_code == 200
        assert b'Dashboard' in resp.data

    def test_es_idempotente(self, tmp_path):
        ruta = tmp_path / 'qsec.db'
        _base_anterior(ruta)

        app = _app_sobre(ruta)
        _app_sobre(ruta)  # arrancar de nuevo no tiene que fallar

        with app.app_context():
            assert agregar_columnas_faltantes(db.engine, db.metadata) == []

    def test_una_base_nueva_no_necesita_cambios(self, tmp_path):
        app = _app_sobre(tmp_path / 'nueva.db')
        with app.app_context():
            assert agregar_columnas_faltantes(db.engine, db.metadata) == []


class TestEnsancheDeColumnas:
    """SQLite ignora la longitud de un VARCHAR, pero Postgres/MySQL la
    imponen: sin ensanchar password_hash a 255, una base creada antes de ese
    cambio de modelo rechazaría el hash scrypt (~162 caracteres) de Werkzeug.
    """

    def test_detecta_un_varchar_que_quedo_corto(self):
        from sqlalchemy import String

        from datos.esquema import _es_ensanche_seguro

        columna_en_base = {'name': 'password_hash', 'type': String(128)}
        columna_modelo = db.Column('password_hash', String(255))
        assert _es_ensanche_seguro(columna_en_base, columna_modelo)

    def test_no_angosta_ni_toca_un_tipo_igual_o_mas_chico(self):
        from sqlalchemy import String

        from datos.esquema import _es_ensanche_seguro

        columna_en_base = {'name': 'password_hash', 'type': String(255)}
        assert not _es_ensanche_seguro(columna_en_base, db.Column('x', String(255)))
        assert not _es_ensanche_seguro(columna_en_base, db.Column('x', String(80)))

    def test_no_toca_una_base_sqlite_aunque_el_varchar_haya_quedado_corto(self, tmp_path):
        """En SQLite ensanchar no es necesario ni posible: se ignora."""
        ruta = tmp_path / 'qsec.db'
        _base_anterior(ruta)

        app = _app_sobre(ruta)

        with app.app_context():
            columnas = inspect(db.engine).get_columns('user')
            password_hash = next(c for c in columnas if c['name'] == 'password_hash')
            # SQLAlchemy refleja el tipo declarado en el CREATE TABLE original
            assert password_hash['type'].length == 128
            # pero un usuario nuevo, con un hash largo, se puede crear sin error
            assert user_repository.create_user('nuevo', 'password123') is not None
