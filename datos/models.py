"""
Modelos de la Base de Datos
Representan las entidades del dominio
"""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from datos import db


def utc_now():
    """Devuelve el instante actual en UTC (timezone-aware).

    Reemplaza a ``datetime.utcnow``, deprecada desde Python 3.12, que además
    devolvía un datetime naive (sin zona horaria).
    """
    return datetime.now(timezone.utc)


class UTCDateTime(db.TypeDecorator):
    """DateTime que siempre guarda y devuelve un valor UTC timezone-aware.

    SQLite (a diferencia de Postgres) no tiene un tipo de dato con zona
    horaria: cualquier ``datetime`` aware pierde su tzinfo al guardarse y
    vuelve naive al leerse. Como todo lo que escribe esta app usa
    ``utc_now()``, alcanza con reponer ``tzinfo=UTC`` al leer para que el
    round-trip sea consistente en cualquier motor.
    """

    impl = db.DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


class User(db.Model, UserMixin):
    """
    Modelo de Usuario
    Representa a un usuario registrado en el sistema
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    # 255 y no 128: el hash scrypt por defecto de Werkzeug ocupa ~162 caracteres.
    # SQLite ignora la longitud declarada, pero Postgres/MySQL la validan y el
    # registro de usuarios fallaría en produccion.
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(UTCDateTime, nullable=True, default=utc_now)

    # Relación con sesiones de simulación
    sessions = db.relationship(
        'SimulationSession',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Hashea y guarda la contraseña"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password_hash, password)


class SimulationSession(db.Model):
    """
    Modelo de Sesión de Simulación
    Almacena el resultado de cada simulación del protocolo BB84
    """
    __tablename__ = 'simulation_session'

    id = db.Column(db.Integer, primary_key=True)
    key_length = db.Column(db.Integer, nullable=False)
    has_eve = db.Column(db.Boolean, nullable=False, default=False)
    result = db.Column(db.String(50), nullable=False)  # 'secure' o 'compromised'
    final_key = db.Column(db.Text, nullable=True)
    error_rate = db.Column(db.Float, nullable=True)
    timestamp = db.Column(UTCDateTime, nullable=False, default=utc_now, index=True)

    # Resultados intermedios del protocolo. Las sesiones anteriores a estas
    # columnas las tienen vacias.
    sifted_length = db.Column(db.Integer, nullable=True)  # bits de la clave tamizada
    sample_size = db.Column(db.Integer, nullable=True)    # bits usados para estimar el QBER
    noise_rate = db.Column(db.Float, nullable=True, default=0.0)  # tasa de ruido del canal despolarizante
    secret_key_rate = db.Column(db.Float, nullable=True)  # tasa asintotica de clave secreta R

    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<SimulationSession {self.id} - {self.result}>"

    def to_dict(self):
        """Convierte la sesión a diccionario para facilitar el uso"""
        return {
            'id': self.id,
            'key_length': self.key_length,
            'has_eve': self.has_eve,
            'result': self.result,
            'final_key': self.final_key,
            'error_rate': self.error_rate,
            'noise_rate': self.noise_rate if self.noise_rate is not None else 0.0,
            'secret_key_rate': self.secret_key_rate,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sifted_length': self.sifted_length,
            'sample_size': self.sample_size,
            'user_id': self.user_id
        }
