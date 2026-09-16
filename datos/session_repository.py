"""
Capa de Datos - Repositorio de Sesiones de Simulación
Contiene todas las operaciones de acceso a datos relacionadas con sesiones
"""
from datos.models import SimulationSession, db


def create_session(user_id, key_length, has_eve, result, final_key=None, error_rate=None,
                   sifted_length=None, sample_size=None, noise_rate=0.0, secret_key_rate=None):
    """
    Crea una nueva sesión de simulación en la base de datos

    Args:
        user_id (int): ID del usuario que ejecuta la simulación
        key_length (int): Longitud de la clave inicial
        has_eve (bool): Si hay espía o no
        result (str): Resultado de la simulación ('secure' o 'compromised')
        final_key (str, optional): La clave final generada
        error_rate (float, optional): Tasa de error cuántico
        sifted_length (int, optional): Bits de la clave tamizada
        sample_size (int, optional): Bits usados para estimar el QBER
        noise_rate (float, optional): Nivel de ruido cuántico despolarizante
        secret_key_rate (float, optional): Tasa asintótica de clave secreta

    Returns:
        SimulationSession: La sesión creada
    """
    session = SimulationSession(
        user_id=user_id,
        key_length=key_length,
        has_eve=has_eve,
        result=result,
        final_key=final_key,
        error_rate=error_rate,
        sifted_length=sifted_length,
        sample_size=sample_size,
        noise_rate=noise_rate,
        secret_key_rate=secret_key_rate
    )
    db.session.add(session)
    db.session.commit()
    return session


def get_session_by_id(session_id):
    """
    Obtiene una sesión por su ID

    Args:
        session_id (int): ID de la sesión

    Returns:
        SimulationSession: La sesión encontrada o None
    """
    return db.session.get(SimulationSession, session_id)


def get_user_sessions(user_id, limit=None):
    """
    Obtiene todas las sesiones de un usuario

    Args:
        user_id (int): ID del usuario
        limit (int, optional): Límite de resultados

    Returns:
        list: Lista de sesiones ordenadas por fecha descendente
    """
    query = (
        db.select(SimulationSession)
        .filter_by(user_id=user_id)
        .order_by(SimulationSession.timestamp.desc())
    )

    if limit:
        query = query.limit(limit)

    return list(db.session.execute(query).scalars())


def get_all_sessions(limit=None):
    """
    Obtiene todas las sesiones del sistema

    Args:
        limit (int, optional): Límite de resultados

    Returns:
        list: Lista de sesiones ordenadas por fecha descendente
    """
    query = db.select(SimulationSession).order_by(SimulationSession.timestamp.desc())

    if limit:
        query = query.limit(limit)

    return list(db.session.execute(query).scalars())


def delete_session(session_id):
    """
    Elimina una sesión de la base de datos

    Args:
        session_id (int): ID de la sesión a eliminar

    Returns:
        bool: True si se eliminó correctamente, False si no existe
    """
    session = get_session_by_id(session_id)
    if session:
        db.session.delete(session)
        db.session.commit()
        return True
    return False


def count_sessions_by_result(user_id):
    """
    Cuenta las sesiones de un usuario agrupadas por resultado.

    La agregación se hace en SQL: antes las estadísticas del dashboard traían
    todas las filas del usuario a memoria sólo para contarlas.

    Args:
        user_id (int): ID del usuario

    Returns:
        dict: cantidad de sesiones por resultado, sólo con los resultados que
            tienen al menos una sesión (por ejemplo {'secure': 3, 'compromised': 1})
    """
    filas = db.session.execute(
        db.select(SimulationSession.result, db.func.count(SimulationSession.id))
        .filter_by(user_id=user_id)
        .group_by(SimulationSession.result)
    ).all()
    return {resultado: cantidad for resultado, cantidad in filas}
