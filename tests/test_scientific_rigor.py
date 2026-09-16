"""
Unit and Integration Tests for Scientific Rigor:
- Shannon Binary Entropy calculation
- Asymptotic Secret Key Rate (Shor-Preskill / Devetak-Winter bound)
- Quantum channel depolarizing noise model
- Zero-friction Guest Mode execution and routes
"""
import pytest
from business.bb84_simulation import (
    binary_entropy,
    calculate_secret_key_rate,
    simulate_bb84
)


class TestQuantumInformationMetrics:
    """Mathematical validation of security and information metrics"""

    def test_binary_entropy_boundaries(self):
        """h(0) = 0, h(1) = 0, h(0.5) = 1.0"""
        assert binary_entropy(0.0) == 0.0
        assert binary_entropy(1.0) == 0.0
        assert binary_entropy(-0.1) == 0.0
        assert binary_entropy(1.1) == 0.0
        assert pytest.approx(binary_entropy(0.5), rel=1e-5) == 1.0

    def test_binary_entropy_intermediate(self):
        """Verify binary entropy matches standard values"""
        # h(0.11) approx 0.5003 bits
        assert 0.49 < binary_entropy(0.11) < 0.51
        # Monotonicity from 0 to 0.5
        assert binary_entropy(0.05) < binary_entropy(0.10) < binary_entropy(0.25)

    def test_secret_key_rate_ideal_channel(self):
        """R(0) = 1 - 2*h(0) = 1.0"""
        assert calculate_secret_key_rate(0.0) == 1.0

    def test_secret_key_rate_threshold_cutoff(self):
        """At and above 11% QBER, asymptotic key rate drops to 0.0"""
        assert calculate_secret_key_rate(0.11) == 0.0
        assert calculate_secret_key_rate(0.15) == 0.0
        assert calculate_secret_key_rate(0.25) == 0.0

    def test_secret_key_rate_positive_for_low_qber(self):
        """For QBER = 5%, R should be around 1 - 2*0.2864 approx 0.427"""
        rate = calculate_secret_key_rate(0.05)
        assert 0.40 < rate < 0.45


class TestNoisyQuantumChannel:
    """Validation of depolarizing noise model in BB84 simulation"""

    def test_simulation_with_channel_noise_produces_errors(self):
        """
        With severe depolarizing noise (e.g., 0.35) and NO eavesdropper,
        environmental decoherence induces QBER > 0 and reduces key rate.
        """
        result = simulate_bb84(key_length=256, has_eve=False, noise_rate=0.35)
        assert result['success'] is True
        assert result['noise_rate'] == 0.35
        assert 'shannon_entropy' in result
        assert 'secret_key_rate' in result
        # Environmental decoherence causes errors without Eve
        assert result['error_rate'] > 0.0

    def test_zero_noise_retains_ideal_behavior(self):
        """Noise rate 0.0 behaves strictly as ideal channel"""
        result = simulate_bb84(key_length=128, has_eve=False, noise_rate=0.0)
        assert result['success'] is True
        assert result['error_rate'] == 0.0
        assert result['secret_key_rate'] == 1.0
        assert result['result'] == 'secure'


class TestGuestModeZeroFriction:
    """Validation of unauthenticated public access (Zero Friction)"""

    def test_guest_can_access_simulator_page(self, client):
        """GET /simulator does not redirect to login for guests"""
        resp = client.get('/simulator')
        assert resp.status_code == 200
        assert b'BB84 Protocol Simulator' in resp.data

    def test_guest_can_access_animation_page(self, client):
        """GET /animation does not redirect to login for guests"""
        resp = client.get('/animation?key_length=20&has_eve=0')
        assert resp.status_code == 200

    def test_guest_can_call_run_simulation_api(self, client):
        """
        POST /api/run-simulation allows unauthenticated requests,
        executing simulation in-memory without error or 403.
        """
        payload = {
            'key_length': 32,
            'has_eve': False,
            'noise_rate': 0.0
        }
        resp = client.post('/api/run-simulation', json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['session']['is_guest'] is True
        assert data['session']['id'] is None
        assert 'secret_key_rate' in data['simulation_details']
