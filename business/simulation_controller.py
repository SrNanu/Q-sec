"""
Capa de Negocio - Controlador de Simulación
Contiene la lógica de negocio del protocolo BB84
NO accede directamente a la base de datos, usa la capa de datos
"""
from datos import session_repository


def get_user_simulation_history(user_id, limit=10):
    """
    Obtiene el historial de simulaciones de un usuario
    
    Args:
        user_id (int): ID del usuario
        limit (int): Número máximo de resultados
    
    Returns:
        list: Lista de sesiones en formato diccionario
    """
    sessions = session_repository.get_user_sessions(user_id, limit)
    return [session.to_dict() for session in sessions]


def get_user_statistics(user_id):
    """
    Obtiene estadísticas de las simulaciones de un usuario
    Regla de negocio: Calcula métricas agregadas

    El conteo se resuelve en SQL en vez de traer todas las filas del usuario a
    memoria sólo para contarlas.

    Args:
        user_id (int): ID del usuario

    Returns:
        dict: Estadísticas del usuario
    """
    por_resultado = session_repository.count_sessions_by_result(user_id)

    secure = por_resultado.get('secure', 0)
    compromised = por_resultado.get('compromised', 0)
    total = sum(por_resultado.values())

    return {
        'total_simulations': total,
        'secure_simulations': secure,
        'compromised_simulations': compromised,
        'success_rate': round((secure / total) * 100, 2) if total > 0 else 0.0
    }


def run_bb84_simulation(user_id, key_length, has_eve, noise_rate=0.0):
    """
    Ejecuta la simulación completa del protocolo BB84 con Qiskit.
    Soporta modo invitado (user_id=None) sin persistencia en base de datos.
    
    Args:
        user_id (int or None): ID del usuario que ejecuta la simulación (None para modo invitado)
        key_length (int): Longitud de la clave inicial (10 a 1000 qubits)
        has_eve (bool): Si incluir un espía o no
        noise_rate (float): Nivel de ruido del canal despolarizante [0.0, 1.0]
    
    Returns:
        dict: Resultado de la simulación
    """
    # Validaciones de negocio
    if key_length < 10:
        return {
            'success': False,
            'message': 'Key length must be at least 10 qubits'
        }
    
    if key_length > 1000:
        return {
            'success': False,
            'message': 'Key length cannot exceed 1000 qubits'
        }
    
    try:
        noise_rate = max(0.0, min(1.0, float(noise_rate)))
    except (ValueError, TypeError):
        noise_rate = 0.0
    
    try:
        # Importar la simulación BB84
        from business.bb84_simulation import simulate_bb84
        
        # Ejecutar la simulación cuántica
        sim_result = simulate_bb84(key_length, has_eve, noise_rate=noise_rate)
        
        if not sim_result['success']:
            return sim_result
        
        # Si el usuario está autenticado, guardar en base de datos
        if user_id is not None:
            session = session_repository.create_session(
                user_id=user_id,
                key_length=key_length,
                has_eve=has_eve,
                result=sim_result['result'],
                final_key=sim_result.get('final_key'),
                error_rate=sim_result.get('error_rate'),
                sifted_length=sim_result.get('key_length_after_sifting'),
                sample_size=sim_result.get('sample_size'),
                noise_rate=noise_rate,
                secret_key_rate=sim_result.get('secret_key_rate')
            )
            session_data = session.to_dict()
        else:
            # Modo Invitado (Guest Mode): sesión efímera en memoria
            from datetime import datetime
            session_data = {
                'id': None,
                'key_length': key_length,
                'has_eve': has_eve,
                'result': sim_result['result'],
                'final_key': sim_result.get('final_key'),
                'error_rate': sim_result.get('error_rate'),
                'noise_rate': noise_rate,
                'secret_key_rate': sim_result.get('secret_key_rate'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sifted_length': sim_result.get('key_length_after_sifting'),
                'sample_size': sim_result.get('sample_size'),
                'user_id': None,
                'is_guest': True
            }
        
        return {
            'success': True,
            'message': sim_result['message'],
            'session': session_data,
            'alice_bits': sim_result.get('alice_bits', []),
            'bob_bits': sim_result.get('bob_bits', []),
            'eve_bits': sim_result.get('eve_bits', []),
            'alice_bases': sim_result.get('alice_bases', []),
            'bob_bases': sim_result.get('bob_bases', []),
            'eve_bases': sim_result.get('eve_bases', []),
            'simulation_details': {
                'key_length_initial': sim_result.get('key_length_initial'),
                'key_length_after_sifting': sim_result.get('key_length_after_sifting'),
                'key_length_final': sim_result.get('key_length_final'),
                'matching_bases': sim_result.get('matching_bases'),
                'sample_size': sim_result.get('sample_size'),
                'error_rate': sim_result.get('error_rate'),
                'shannon_entropy': sim_result.get('shannon_entropy'),
                'secret_key_rate': sim_result.get('secret_key_rate'),
                'noise_rate': noise_rate
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Simulation error: {str(e)}'
        }
