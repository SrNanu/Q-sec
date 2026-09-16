"""
BB84 Protocol Quantum Simulation using Qiskit & Qiskit-Aer.
Implements quantum key distribution, channel noise modeling (depolarizing channel),
eavesdropping detection, QBER estimation, and asymptotic secret key rate calculation.
"""
import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel, depolarizing_error


def binary_entropy(p: float) -> float:
    """
    Calculates the binary Shannon entropy h(p).
    h(p) = -p*log2(p) - (1-p)*log2(1-p), with h(0) = h(1) = 0.
    
    Args:
        p (float): Error probability / QBER.
        
    Returns:
        float: Shannon entropy in bits [0.0, 1.0].
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return float(-p * np.log2(p) - (1.0 - p) * np.log2(1.0 - p))


def calculate_secret_key_rate(qber: float) -> float:
    """
    Calculates the asymptotic secret key rate R under one-way classical post-processing
    (Shor-Preskill / Devetak-Winter bound):
    R >= max(0, 1 - 2 * h(QBER))
    
    Returns 0.0 if QBER >= 11% (the BB84 theoretical threshold).
    
    Args:
        qber (float): Quantum Bit Error Rate in [0.0, 1.0].
        
    Returns:
        float: Asymptotic secret key rate fraction [0.0, 1.0].
    """
    if qber >= 0.11 or qber < 0.0:
        return 0.0
    h_p = binary_entropy(qber)
    rate = 1.0 - 2.0 * h_p
    return max(0.0, float(rate))


def generate_random_bits(n):
    """Generates n random classical bits (0 or 1)"""
    return [random.randint(0, 1) for _ in range(n)]


def generate_random_bases(n):
    """Generates n random bases (0=rectilinear +, 1=diagonal x)"""
    return [random.randint(0, 1) for _ in range(n)]


def encode_qubit(bit, basis):
    """
    Encodes a bit into a qubit state according to the selected basis.
    
    Args:
        bit (int): 0 or 1
        basis (int): 0 (rectilinear +) or 1 (diagonal x)
    
    Returns:
        QuantumCircuit: Circuit with the prepared single-qubit state
    """
    qc = QuantumCircuit(1, 1)
    
    # State preparation in Z basis
    if bit == 1:
        qc.x(0)
    
    # Basis rotation: apply Hadamard for diagonal basis (|+) or |->)
    if basis == 1:
        qc.h(0)
    
    return qc


def measure_qubit(qc, basis):
    """
    Measures a qubit in the specified basis.
    
    Args:
        qc (QuantumCircuit): Single-qubit circuit
        basis (int): Measurement basis (0=+, 1=x)
    
    Returns:
        QuantumCircuit: Circuit with measurement operation added
    """
    # Basis rotation before projective Z measurement
    if basis == 1:
        qc.h(0)
    
    qc.measure(0, 0)
    return qc


def eve_intercept(qc):
    """
    Simulates Eve's intercept-resend attack.
    Eve measures in a random basis and prepares a new qubit to resend to Bob.
    
    Args:
        qc (QuantumCircuit): Intercepted circuit
    
    Returns:
        tuple: (new circuit, Eve basis, Eve measured bit)
    """
    eve_basis = random.randint(0, 1)
    
    # Eve measures in her chosen basis
    if eve_basis == 1:
        qc.h(0)
    qc.measure(0, 0)
    
    simulator = Aer.get_backend('qasm_simulator')
    job = simulator.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    eve_bit = int(list(counts.keys())[0])
    
    # Eve prepares a fresh qubit corresponding to her measurement outcome
    qc_new = QuantumCircuit(1, 1)
    if eve_bit == 1:
        qc_new.x(0)
    if eve_basis == 1:
        qc_new.h(0)
    
    return qc_new, eve_basis, eve_bit


def simulate_bb84(key_length, has_eve=False, noise_rate=0.0):
    """
    Simulates the complete BB84 QKD protocol including quantum state encoding,
    channel transmission with optional depolarizing noise, intercept-resend attack,
    sifting, QBER calculation, and asymptotic secret key rate estimation.
    
    Args:
        key_length (int): Initial number of transmitted qubits
        has_eve (bool): Whether an eavesdropper (Eve) intercepts the channel
        noise_rate (float): Channel depolarizing error parameter [0.0, 1.0]
    
    Returns:
        dict: Complete simulation telemetry, keys, metrics, and trace
    """
    # Step 1: Alice generates random bits and random encoding bases
    alice_bits = generate_random_bits(key_length)
    alice_bases = generate_random_bases(key_length)
    
    # Step 2: Bob generates random measurement bases
    bob_bases = generate_random_bases(key_length)
    
    # Step 3: Configure channel noise model if specified
    noise_model = None
    if noise_rate > 0.0:
        noise_model = NoiseModel()
        error = depolarizing_error(float(noise_rate), 1)
        noise_model.add_all_qubit_quantum_error(error, ['id'])
    
    # Step 4: Transmission and measurement
    bob_results = []
    eve_bases = []
    eve_bits = []
    simulator = Aer.get_backend('qasm_simulator')
    
    for i in range(key_length):
        # Alice prepares the quantum state
        qc = encode_qubit(alice_bits[i], alice_bases[i])
        
        # Environmental channel transmission
        if noise_rate > 0.0:
            qc.id(0)
        
        # Eavesdropper intercept-resend attack
        if has_eve:
            qc, eve_basis, eve_bit = eve_intercept(qc)
            eve_bases.append(eve_basis)
            eve_bits.append(eve_bit)
            if noise_rate > 0.0:
                qc.id(0)
        
        # Bob applies measurement basis rotation and projects
        qc = measure_qubit(qc, bob_bases[i])
        
        # Run quantum circuit
        job = simulator.run(qc, shots=1, noise_model=noise_model) if noise_model else simulator.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        bob_bit = int(list(counts.keys())[0])
        bob_results.append(bob_bit)
    
    # Step 5: Public basis reconciliation (sifting)
    matching_bases_indices = [i for i in range(key_length) if alice_bases[i] == bob_bases[i]]
    alice_key = [alice_bits[i] for i in matching_bases_indices]
    bob_key = [bob_results[i] for i in matching_bases_indices]
    
    # Sifting validation: need at least 4 bits to sample QBER
    if len(alice_key) < 4:
        return {
            'success': False,
            'message': (
                f'Only {len(alice_key)} bases matched out of {key_length} qubits: '
                'at least 4 sifted bits are required to estimate QBER. '
                'Please try again with a larger key length.'
            )
        }
    
    # Step 6: Parameter estimation (QBER sampling)
    sample_size = min(len(alice_key) // 4, 20)  # 25% of sifted key or max 20 bits
    sample_indices = random.sample(range(len(alice_key)), sample_size)
    
    errors = sum(1 for i in sample_indices if alice_key[i] != bob_key[i])
    error_rate = errors / sample_size
    
    # Quantum information security metrics
    shannon_ent = binary_entropy(error_rate)
    secret_key_rate = calculate_secret_key_rate(error_rate)
    
    THRESHOLD = 0.11  # Shor-Preskill threshold for BB84 (11%)
    
    resultado = {
        'success': True,
        'error_rate': error_rate,
        'shannon_entropy': round(shannon_ent, 4),
        'secret_key_rate': round(secret_key_rate, 4),
        'noise_rate': noise_rate,
        'key_length_initial': key_length,
        'key_length_after_sifting': len(alice_key),
        'sample_size': sample_size,
        'matching_bases': len(matching_bases_indices),
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_bits': bob_results,
        'eve_bases': eve_bases,
        'eve_bits': eve_bits,
        'matching_indices': matching_bases_indices,
    }
    
    if error_rate < THRESHOLD:
        # Discard the revealed sample bits to form the final secret key
        final_key_bits = [alice_key[i] for i in range(len(alice_key)) if i not in sample_indices]
        final_key = ''.join(map(str, final_key_bits))
        
        resultado.update({
            'result': 'secure',
            'final_key': final_key,
            'key_length_final': len(final_key_bits),
            'message': f'Secure key successfully generated. QBER: {error_rate:.2%} | Secret Key Rate: {secret_key_rate:.3f}',
        })
    else:
        reason = "Eavesdropping detected!" if has_eve else "Severe channel noise / decoherence detected!"
        resultado.update({
            'result': 'compromised',
            'final_key': None,
            'key_length_final': 0,
            'message': f'{reason} High QBER: {error_rate:.2%} (Secret Key Rate: 0.000)',
        })
    
    return resultado
