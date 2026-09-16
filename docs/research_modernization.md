# Modernización a Estándar de Investigación (OIST Roadmap & Changelog)

Este documento registra los cambios introducidos en la plataforma **Q-Sec** para elevar su rigor científico a nivel de investigación internacional (alineado al perfil de la *Networked Quantum Devices Unit* del Dr. David Elkouss en **OIST**), junto al roadmap de investigación propuesto para extensiones futuras.

---

## 1. Bitácora de Cambios Implementados

### 1.1 Capa Cuántica y Teoría de la Información (`business/bb84_simulation.py`)
- **Canal con Ruido Cuántico Despolarizante**:
  - Implementación con `qiskit_aer.noise.NoiseModel` y `depolarizing_error`.
  - Simula la interacción ambiental y decoherencia en el tránsito de los fotones antes de la estación de Bob.
- **Entropía Binaria de Shannon**:
  - Función analítica $h(p) = -p \log_2(p) - (1-p) \log_2(1-p)$.
  - Casos de borde rigurosos: $\lim_{p \to 0} h(p) = 0$ y $\lim_{p \to 1} h(p) = 0$.
- **Tasa Asintótica de Clave Secreta ($R_\infty$)**:
  - Límite de Devetak-Winter / Shor-Preskill en régimen de clave infinita:
    $$R_\infty = \max\left(0, 1 - 2 h(\text{QBER})\right)$$
  - Corte estricto en el umbral crítico de información cuántica $\text{QBER} \ge 11.00\%$, donde el canal aborta por no garantizar secreto frente a escuchas arbitrarias.

### 1.2 Experiencia de Usuario sin Fricción (`business/simulation_controller.py`, `views/routes.py`)
- **Modo Invitado (Guest Mode)**:
  - Las rutas `/simulator`, `/animation` y `/api/run-simulation` aceptan `user_id=None`.
  - Permite a revisores y evaluadores externos ejecutar experimentos completos sin requerir registro ni login.
  - Para usuarios autenticados, se mantiene la persistencia histórica y estadísticas globales.
- **Presets de Investigación de 1 Clic**:
  - *Ideal Channel*: 32 bits, 0% ruido cuántico, sin espía ($\text{QBER} = 0\%$, $R \approx 1.0$).
  - *Eavesdropping Attack*: 32 bits, espía activo midiendo en bases aleatorias ($\text{QBER} \approx 25\%$, aborto seguro).
  - *Noisy Quantum Channel*: 40 bits, 15% ruido despolarizante ($\text{QBER} > 0\%$, penalización gradual en la tasa secreta).

### 1.3 Animación SVG y Frontend (`views/templates/`, `views/forms.py`)
- **Internacionalización (English-First UI)**:
  - Traducción al inglés técnico formal en navegación, formularios de simulación, panel de métricas, alertas y pie de página.
  - Reconocimiento académico al desarrollo en UTN FRRo y citación al paper presentado en CoNaIISI 2026.
- **Optimización y Sincronización de Animación de Fotones**:
  - Se vinculó el bucle SVG de transmisión al tamaño del lote representativo en pantalla (`Math.min(16, qubits)`), resolviendo el cuello de botella que congelaba el navegador al simular longitudes de 256 o 512 bits.
  - Animación de desvío e intercepción de fotones en presencia de Eve hacia el detector inferior con efectos de resplandor.
  - Reporte instantáneo de métricas en el Paso 6: QBER, Entropía $h(p)$, Tasa $R$ y alerta dinámica de compromiso del canal.

### 1.4 Persistencia y Migraciones (`datos/models.py`, `datos/esquema.py`, `datos/session_repository.py`)
- Extensión del modelo `SimulationSession` con columnas `noise_rate` y `secret_key_rate`.
- Migración no destructiva en arranque: agrega columnas ausentes tanto en SQLite como en PostgreSQL manteniendo compatibilidad absoluta con registros existentes.

### 1.5 Validación y Tests (`tests/`)
- Incorporación de `tests/test_scientific_rigor.py`.
- Cobertura completa de la suite con `pytest`: 96/96 tests pasando (0 fallos).

---

## 2. Roadmap de Investigación (Próximas Mejoras)

Líneas de extensión tecnológica y científica para consolidar el simulador en el área de redes y comunicaciones cuánticas:

### 2.1 Reconciliación de Información y Corrección de Errores Clásica
- **Algoritmo Cascade / Winnow**: Implementar el protocolo interactivo clásico donde Alice y Bob dividen la clave tamizada en bloques y comparan paridades para detectar y corregir errores sin revelar más información que la mínima necesaria.
- **Códigos LDPC / Polar para QKD**: Integración de decodificadores de baja densidad de paridad (LDPC) para alcanzar eficiencias de reconciliación $f \approx 1.05 - 1.15$ del límite de Shannon.

### 2.2 Amplificación de Privacidad Universal
- **Matrices de Toeplitz y Hashing 2-Universal**: Extracción determinista de la clave final reducida a partir del límite inferior de min-entropía condicional $H_{\min}(A|E)$, asegurando que la información mutua entre la clave final y Eve sea inferior a $\epsilon_{\text{sec}}$.

### 2.3 Modelado de Canal Óptico Realista
- **Pérdidas por Distancia en Fibra Monomodo (SMF-28)**: Coeficiente de atenuación estándar $\alpha = 0.2\text{ dB/km}$ a $1550\text{ nm}$, permitiendo ingresar la distancia $L$ en kilómetros y derivar la transmitancia $T = 10^{-\alpha L / 10}$.
- **Detectores de Fotón Único (SPAD/SNSPD)**: Modelado de eficiencia cuántica de detección ($\eta$), tasa de cuentas oscuras (*dark count rate*, $p_{\text{dark}}$) y tiempo de recuperación (*dead time*).

### 2.4 Protocolo de Estados Señuelo (Decoy-State BB84)
- Atenuación de fuentes láser coherentes débiles (WCP) y alternancia entre intensidades de señal ($\mu$) y señuelo ($\nu_1, \nu_2$) para neutralizar ataques de división del número de fotones (*Photon Number Splitting* / PNS).

### 2.5 Extensión a QKD Basado en Entrelazamiento
- Protocolo **E91** (Artur Ekert) o **BBM92** utilizando pares de Bell $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$, permitiendo comprobar la violación de la desigualdad de Bell (parámetro de Clauser-Horne-Shimony-Holt, $|S| \le 2\sqrt{2} \approx 2.828$) como testigo directo de la seguridad física.
