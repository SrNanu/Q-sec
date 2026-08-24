"""
Tests para la simulación del protocolo BB84
"""
import pytest
import sys
import os

# Agregar el directorio TPI al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from business.bb84_simulation import (
        generate_random_bits,
        generate_random_bases,
        encode_qubit,
        measure_qubit,
        simulate_bb84
    )
    BB84_AVAILABLE = True
except ImportError as e:
    # Si hay incompatibilidad de versiones, saltamos estos tests
    BB84_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason=f"BB84 simulation no disponible: {e}")


@pytest.mark.skipif(not BB84_AVAILABLE, reason="BB84 simulation no disponible")
class TestBB84Simulation:
    """Tests para la simulación del protocolo BB84"""
    
    def test_generate_random_bits(self):
        """Test: generar bits aleatorios"""
        n = 100
        bits = generate_random_bits(n)
        
        assert len(bits) == n
        assert all(bit in [0, 1] for bit in bits)
    
    def test_generate_random_bits_distribution(self):
        """Test: distribución de bits aleatorios"""
        n = 1000
        bits = generate_random_bits(n)
        
        # Contar 0s y 1s (debería ser aproximadamente 50/50)
        zeros = bits.count(0)
        ones = bits.count(1)
        
        # Verificar que no está totalmente sesgado
        assert 400 < zeros < 600
        assert 400 < ones < 600
    
    def test_generate_random_bases(self):
        """Test: generar bases aleatorias"""
        n = 100
        bases = generate_random_bases(n)
        
        assert len(bases) == n
        assert all(basis in [0, 1] for basis in bases)
    
    def test_generate_random_bases_distribution(self):
        """Test: distribución de bases aleatorias"""
        n = 1000
        bases = generate_random_bases(n)
        
        # Contar bases (debería ser aproximadamente 50/50)
        base_plus = bases.count(0)
        base_x = bases.count(1)
        
        # Verificar que no está totalmente sesgado
        assert 400 < base_plus < 600
        assert 400 < base_x < 600
    
    def test_encode_qubit_bit_0_base_plus(self):
        """Test: codificar bit 0 en base +"""
        qc = encode_qubit(0, 0)
        
        assert qc is not None
        # El circuito debe tener 1 qubit
        assert qc.num_qubits == 1
    
    def test_encode_qubit_bit_1_base_plus(self):
        """Test: codificar bit 1 en base +"""
        qc = encode_qubit(1, 0)
        
        assert qc is not None
        assert qc.num_qubits == 1
    
    def test_encode_qubit_bit_0_base_x(self):
        """Test: codificar bit 0 en base x"""
        qc = encode_qubit(0, 1)
        
        assert qc is not None
        assert qc.num_qubits == 1
    
    def test_encode_qubit_bit_1_base_x(self):
        """Test: codificar bit 1 en base x"""
        qc = encode_qubit(1, 1)
        
        assert qc is not None
        assert qc.num_qubits == 1
    
    def test_measure_qubit(self):
        """Test: medir un qubit"""
        # Crear un qubit codificado
        qc = encode_qubit(0, 0)
        
        # Intentar medir
        result = measure_qubit(qc, 0)
        
        assert result is not None
    
    def test_bb84_protocol_basics(self):
        """Test: básicos del protocolo BB84"""
        n = 256
        
        # Alice genera bits y bases
        alice_bits = generate_random_bits(n)
        alice_bases = generate_random_bases(n)
        
        # Bob genera bases
        bob_bases = generate_random_bases(n)
        
        # Verificar que tenemos los datos correctos
        assert len(alice_bits) == n
        assert len(alice_bases) == n
        assert len(bob_bases) == n
        assert all(b in [0, 1] for b in alice_bits)
        assert all(b in [0, 1] for b in alice_bases)
        assert all(b in [0, 1] for b in bob_bases)


@pytest.mark.skipif(not BB84_AVAILABLE, reason="BB84 simulation no disponible")
class TestBB84FullProtocol:
    """
    Tests de extremo a extremo sobre simulate_bb84(): validan la regla de negocio
    central del protocolo (detección de espionaje vía QBER), no solo sus piezas sueltas.
    """

    def test_simulate_bb84_without_eve_yields_secure_key(self):
        """Sin espía, el canal es ideal: la tasa de error debe ser nula y la clave, segura."""
        result = simulate_bb84(key_length=256, has_eve=False)

        assert result['success'] is True
        assert result['result'] == 'secure'
        assert result['error_rate'] == 0.0
        assert result['final_key'] is not None
        assert result['key_length_final'] > 0

    def test_simulate_bb84_without_eve_never_raises_false_alarm(self):
        """Repetido varias veces, sin espía no debería aparecer nunca un falso positivo."""
        for _ in range(10):
            result = simulate_bb84(key_length=128, has_eve=False)
            assert result['result'] == 'secure'
            assert result['error_rate'] == 0.0

    def test_simulate_bb84_with_eve_is_usually_detected(self):
        """
        Con espía presente, la interceptación-reenvío introduce un QBER promedio del 25%,
        muy por encima del umbral de seguridad (11%). Sobre 20 corridas independientes,
        la probabilidad de que el espía pase inadvertido en todas ellas por azar es
        estadísticamente insignificante (~9% de no detección por corrida individual),
        por lo que se espera detectarlo en una amplia mayoría de los casos.
        """
        n_runs = 20
        detected = 0
        for _ in range(n_runs):
            result = simulate_bb84(key_length=256, has_eve=True)
            assert result['success'] is True
            if result['result'] == 'compromised':
                detected += 1

        detection_rate = detected / n_runs
        assert detection_rate >= 0.6, (
            f"Se esperaba detectar al espía en la mayoría de las corridas, "
            f"pero solo se detectó en {detected}/{n_runs} ({detection_rate:.0%})."
        )

    def test_simulate_bb84_with_eve_has_higher_error_rate_than_without(self):
        """La tasa de error promedio con espía debe ser sensiblemente mayor que sin espía."""
        no_eve_rates = [simulate_bb84(key_length=256, has_eve=False)['error_rate'] for _ in range(5)]
        eve_rates = [simulate_bb84(key_length=256, has_eve=True)['error_rate'] for _ in range(10)]

        avg_no_eve = sum(no_eve_rates) / len(no_eve_rates)
        avg_eve = sum(eve_rates) / len(eve_rates)

        assert avg_no_eve == 0.0
        assert avg_eve > avg_no_eve
        assert avg_eve > 0.15  # muy por encima del ruido esperado sin intervención
