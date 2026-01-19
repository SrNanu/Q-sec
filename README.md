<div align="center">

# 🔐 Q-Sec: Simulador Interactivo BB84

### *Criptografía Cuántica al Alcance de Todos*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.2.0-purple.svg)](https://qiskit.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Pytest-red.svg)](tests/)

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
  <img src="https://img.shields.io/badge/Maintained-Yes-green.svg" alt="Maintained">
</p>

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Arquitectura](#-arquitectura) • [Tecnologías](#️-tecnologías)

</div>

---

## 📖 Descripción

**Q-Sec** es una aplicación web educativa que simula el protocolo de **Distribución Cuántica de Claves BB84**, uno de los pilares fundamentales de la criptografía cuántica. El proyecto permite a usuarios sin conocimientos previos en computación cuántica comprender cómo funciona este revolucionario protocolo de seguridad.

A través de una interfaz intuitiva, los usuarios pueden:
- 🔬 Ejecutar simulaciones paso a paso del protocolo BB84
- 👁️ Observar en tiempo real la transmisión y medición de qubits
- 🕵️ Simular ataques de espionaje (Eve) y detectar intrusiones
- 📊 Visualizar resultados y estadísticas de cada simulación
- 📚 Almacenar y consultar historial de simulaciones

> **¿Qué es BB84?** Es el primer protocolo de distribución cuántica de claves, creado por Charles Bennett y Gilles Brassard en 1984. Utiliza los principios de la mecánica cuántica para garantizar comunicaciones absolutamente seguras, donde cualquier intento de espionaje es detectado automáticamente.

---

## ✨ Características

### 🎯 Funcionalidades Principales

- **👤 Sistema de Usuarios**
  - Registro y autenticación segura con Flask-Login
  - Contraseñas cifradas con Werkzeug
  - Sesiones persistentes con cookies seguras

- **⚛️ Simulación Cuántica Realista**
  - Implementación completa del protocolo BB84 con IBM Qiskit
  - Generación aleatoria de bits y bases cuánticas
  - Codificación de qubits en bases rectilínea (+) y diagonal (×)
  - Medición cuántica con colapso de estado

- **🕵️ Detección de Espionaje**
  - Simulación opcional de interceptación por un atacante (Eve)
  - Cálculo automático de tasa de error cuántico (QBER)
  - Alertas de seguridad basadas en anomalías estadísticas

- **📊 Visualización y Análisis**
  - Dashboard interactivo con resultados detallados
  - Historial completo de simulaciones
  - Estadísticas de éxito/compromiso de claves
  - Visualización paso a paso del proceso

- **🏗️ Arquitectura Robusta**
  - Diseño en 3 capas (Presentación, Negocio, Datos)
  - Testing automatizado con Pytest
  - Separación clara de responsabilidades
  - Código modular y mantenible

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/SrNanu/Q-sec
cd Q-Sec-linkedin
```

2. **Crear un entorno virtual** (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno** (opcional)
```bash
# Crear archivo .env en la raíz del proyecto
SECRET_KEY=tu-clave-secreta-super-segura
DATABASE_URL=sqlite:///qsec.db
```

5. **Inicializar la base de datos**
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

6. **Ejecutar la aplicación**
```bash
python run.py
```

7. **Abrir en el navegador**
```
http://localhost:5000
```

---

## 💻 Uso

### Inicio Rápido

1. **Registrarse**: Crea una cuenta con usuario y contraseña
2. **Iniciar Sesión**: Accede a tu dashboard personal
3. **Nueva Simulación**: 
   - Define la longitud de la clave inicial (ej: 100 bits)
   - Decide si incluir un espía (Eve) en la simulación
   - Ejecuta la simulación
4. **Ver Resultados**: Analiza la clave final, tasa de error y estado de seguridad
5. **Consultar Historial**: Revisa todas tus simulaciones anteriores

### Ejemplo de Simulación

```python
# Parámetros de ejemplo
Longitud inicial: 100 bits
Espía activo: Sí

# Resultados típicos
✅ Bits originales: 100
📊 Bases coincidentes: ~50 (50%)
🔐 Clave final: 23 bits seguros
⚠️ QBER: 25.5% → ¡Espía detectado!
```

---

## 🏛️ Arquitectura

El proyecto sigue una **arquitectura en 3 capas** estricta:

<div align="center">
  <img src="docs/diagrams/DDA.png" alt="Diagrama de Arquitectura en 3 Capas" width="600">
</div>

```
┌─────────────────────────────────────────┐
│      CAPA DE PRESENTACIÓN (Views)       │
│  - Rutas Flask (routes.py)              │
│  - Plantillas HTML (templates/)         │
│  - Formularios WTForms (forms.py)       │
│  - Archivos estáticos CSS (static/)     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      CAPA DE NEGOCIO (Business)         │
│  - Controladores (auth, simulation)     │
│  - Lógica BB84 (bb84_simulation.py)    │
│  - Validaciones y reglas de negocio     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│        CAPA DE DATOS (Datos)            │
│  - Modelos SQLAlchemy (models.py)      │
│  - Repositorios (user, session)         │
│  - Gestión de base de datos             │
└─────────────────────────────────────────┘
```

### Estructura del Proyecto

```
Q-Sec-linkedin/
├── 📄 app.py                    # Configuración principal de Flask
├── 📄 run.py                    # Punto de entrada de la aplicación
├── 📄 requirements.txt          # Dependencias del proyecto
├── 📄 pytest.ini                # Configuración de tests
├── 📁 business/                 # Capa de Negocio
│   ├── auth_controller.py       # Lógica de autenticación
│   ├── simulation_controller.py # Lógica de simulaciones
│   └── bb84_simulation.py       # Implementación del protocolo BB84
├── 📁 datos/                    # Capa de Datos
│   ├── models.py                # Modelos de base de datos
│   ├── user_repository.py       # Acceso a datos de usuarios
│   └── session_repository.py    # Acceso a datos de simulaciones
├── 📁 views/                    # Capa de Presentación
│   ├── routes.py                # Rutas de la aplicación
│   ├── forms.py                 # Formularios web
│   ├── templates/               # Plantillas HTML
│   └── static/                  # CSS y recursos estáticos
├── 📁 tests/                    # Suite de tests
│   ├── test_bb84.py             # Tests del protocolo
│   ├── test_models.py           # Tests de modelos
│   ├── test_integration.py      # Tests de integración
│   └── conftest.py              # Configuración de pytest
└── 📁 docs/                     # Documentación
    ├── PROYECTO.md              # Especificación del proyecto
    └── diagrams/                # Diagramas de arquitectura
```

---

## 🛠️ Tecnologías

### Backend & Framework
- **Flask 3.1.2** - Framework web minimalista y potente
- **Flask-Login 0.6.3** - Gestión de sesiones de usuario
- **Flask-SQLAlchemy 3.1.1** - ORM para base de datos
- **Flask-WTF 1.2.2** - Formularios web seguros

### Computación Cuántica
- **IBM Qiskit 2.2.0** - Framework de computación cuántica
- **Qiskit-Aer 0.17.2** - Simulador de circuitos cuánticos
- **NumPy 2.3.3** - Cálculos numéricos y matrices

### Base de Datos
- **SQLite** - Base de datos embebida
- **SQLAlchemy 2.0.43** - ORM Python-SQL

### Testing & Calidad
- **Pytest 8.4.2** - Framework de testing
- **Python-dotenv 1.1.1** - Gestión de variables de entorno

### Utilidades
- **Werkzeug 3.1.3** - Utilidades WSGI (hashing de contraseñas)
- **WTForms 3.2.1** - Validación de formularios

---

## 🧪 Testing

El proyecto incluye una suite completa de tests:

```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/test_bb84.py           # Tests del protocolo BB84
pytest tests/test_models.py         # Tests de modelos de datos
pytest tests/test_integration.py    # Tests de integración

# Con reporte de cobertura
pytest --cov=business --cov=datos --cov=views
```

### Cobertura de Tests

- ✅ Protocolo BB84 completo
- ✅ Detección de espionaje
- ✅ Autenticación de usuarios
- ✅ Persistencia de simulaciones
- ✅ Integración entre capas

---

## 🎓 Conceptos Cuánticos

### El Protocolo BB84

1. **Preparación (Alice)**
   - Genera bits aleatorios: `[0, 1, 1, 0, ...]`
   - Elige bases aleatorias: `[+, ×, +, ×, ...]`
   - Codifica qubits según base y bit

2. **Transmisión**
   - Los qubits viajan por el canal cuántico
   - Eve puede interceptar (opcional)

3. **Medición (Bob)**
   - Elige bases aleatorias independientes
   - Mide los qubits recibidos

4. **Reconciliación**
   - Alice y Bob comparan bases públicamente
   - Descartan bits con bases diferentes
   - Verifican errores para detectar espías

### Estados Cuánticos

| Bit | Base + | Base × |
|-----|--------|--------|
| 0   | \|0⟩   | \|+⟩   |
| 1   | \|1⟩   | \|-⟩   |

---

## 📝 Documentación Adicional

- 📋 [Especificación del Proyecto](docs/PROYECTO.md)
- 🔍 [Tests README](tests/README.md)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📜 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 👤 Autores

**Santino Cataldi**
- 💼 LinkedIn: https://www.linkedin.com/in/santino-cataldi/

**Lucio Nahuel Cosentino**
- 💼 LinkedIn: https://www.linkedin.com/in/lucio-nahuel-cosentino-6bb057215/

**Tomás Wardoloff**
- 💼 LinkedIn: https://www.linkedin.com/in/tomaswardoloff/

**Gaspar Martinez**
- 💼 LinkedIn: https://www.linkedin.com/in/gasparmartinez12/
---

## 📑 Nota sobre el Repositorio

Este repositorio es una versión **refactorizada y "standalone"** del proyecto original desarrollado para la universidad.
El código fuente ha sido migrado y limpiado para facilitar su despliegue y análisis técnico en este portafolio.

Si se desea consultar el historial completo de commits y el desarrollo colaborativo original, se puede visitar el repositorio fuente:
🔗 **[Ver Repositorio Original / Historial de Desarrollo](https://github.com/Tomas-Wardoloff/frro-python-2025-12/tree/TPI)**

---

<div align="center">

### ⭐ Si te gustó el proyecto, considera darle una estrella!

**Made with ❤️ and ⚛️ (Quantum Love)**

</div>