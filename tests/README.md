# 🧪 Suite de Tests del TPI - Q-Sec

Este directorio contiene la suite completa de tests automatizados para el proyecto Q-Sec (Simulador Interactivo del Protocolo de Criptografía Cuántica BB84).

## 📋 Estructura de Tests

### 1. **test_app.py** - Tests de la Aplicación Flask

**Propósito:** Validar que la aplicación Flask está correctamente configurada y funciona.

#### Tests incluidos:

- **`TestAppBasics::test_app_exists`**
  - **¿Qué hace?** Verifica que la instancia de Flask (`app`) existe
  - **¿Por qué?** Asegurar que la aplicación se inicializa correctamente
  - **¿Cuándo falla?** Si hay un error en `app/__init__.py` al crear la app

- **`TestAppBasics::test_app_is_testing`**
  - **¿Qué hace?** Verifica que la configuración de testing está activa
  - **¿Por qué?** Los tests deben ejecutarse en modo testing con BD en memoria
  - **¿Cuándo falla?** Si la fixture no configura `TESTING = True`

- **`TestForms::test_login_form_fields`**
  - **¿Qué hace?** Verifica que existe la clase `LoginForm`
  - **¿Por qué?** Asegurar que los formularios de autenticación existen
  - **¿Cuándo falla?** Si no se puede importar `LoginForm` desde `views.forms`

- **`TestForms::test_register_form_fields`**
  - **¿Qué hace?** Verifica que existe la clase `RegisterForm`
  - **¿Por qué?** Asegurar que el formulario de registro está disponible
  - **¿Cuándo falla?** Si no se puede importar `RegisterForm`

- **`TestRoutes::test_home_route_exists`**
  - **¿Qué hace?** Hace una petición GET a `/` y verifica que responde
  - **¿Por qué?** Validar que la ruta home está registrada
  - **¿Cuándo falla?** Si no existe una ruta para `/` o hay error en la lógica

- **`TestRoutes::test_404_error`**
  - **¿Qué hace?** Intenta acceder a una ruta inexistente y verifica que retorna 404
  - **¿Por qué?** Asegurar que Flask maneja correctamente las rutas no existentes
  - **¿Cuándo falla?** Si Flask no retorna 404 para rutas inválidas

---

### 2. **test_models.py** - Tests de los Modelos de Base de Datos

**Propósito:** Validar que los modelos SQLAlchemy funcionan correctamente con la BD.

#### Tests incluidos:

**Clase `TestUserModel`** - Tests del modelo User

- **`test_user_creation`**
  - **¿Qué hace?** Crea un usuario en BD y verifica que se guardó
  - **¿Por qué?** Asegurar que los usuarios se pueden crear y persistir
  - **¿Cuándo falla?** Si hay error en el modelo User o en la BD

- **`test_user_password_hashing`**
  - **¿Qué hace?** Verifica que la contraseña se hashea (no se guarda en texto plano)
  - **¿Por qué?** Seguridad crítica: las contraseñas NO deben guardarse en texto plano
  - **¿Cuándo falla?** Si `set_password()` no hashea correctamente

- **`test_user_check_password`**
  - **¿Qué hace?** Verifica que `check_password()` funciona correctamente
  - **¿Por qué?** Asegurar que se pueden verificar contraseñas durante login
  - **¿Cuándo falla?** Si hay error en la función de verificación de contraseña

- **`test_user_repr`**
  - **¿Qué hace?** Verifica que el usuario tiene una representación útil
  - **¿Por qué?** Para debugging y logs
  - **¿Cuándo falla?** Si el método `__repr__` no está bien implementado

**Clase `TestSimulationSessionModel`** - Tests del modelo SimulationSession

- **`test_session_creation`**
  - **¿Qué hace?** Crea una sesión de simulación y verifica que se guardó
  - **¿Por qué?** Asegurar que se pueden guardar resultados de simulaciones
  - **¿Cuándo falla?** Si hay error en el modelo SimulationSession o relaciones

- **`test_session_with_eve`**
  - **¿Qué hace?** Crea una sesión con espía (Eve) y verifica el estado
  - **¿Por qué?** Validar que se registra correctamente si Eve estaba presente
  - **¿Cuándo falla?** Si el campo `has_eve` o `result` no funciona

- **`test_session_timestamp`**
  - **¿Qué hace?** Verifica que el timestamp se asigna automáticamente
  - **¿Por qué?** Asegurar que se registra cuándo se hizo cada simulación
  - **¿Cuándo falla?** Si el default de timestamp no funciona

- **`test_session_repr`**
  - **¿Qué hace?** Verifica que la sesión tiene una representación útil
  - **¿Por qué?** Para debugging y logs
  - **¿Cuándo falla?** Si el método `__repr__` no está bien implementado

---

### 3. **test_integration.py** - Tests de Integración

**Propósito:** Validar flujos completos del usuario y la aplicación.

#### Tests incluidos:

**Clase `TestUserFlow`** - Flujos completos de usuario

- **`test_user_can_register`**
  - **¿Qué hace?** Simula el registro completo de un usuario
  - **¿Por qué?** Validar el flujo end-to-end de registro
  - **¿Cuándo falla?** Si hay error en la creación de usuarios

- **`test_user_can_authenticate`**
  - **¿Qué hace?** Crea un usuario y verifica autenticación
  - **¿Por qué?** Asegurar que se pueden autenticar usuarios correctamente
  - **¿Cuándo falla?** Si la verificación de contraseña falla

- **`test_user_can_simulate`**
  - **¿Qué hace?** Crea un usuario y una sesión de simulación
  - **¿Por qué?** Validar que los usuarios pueden ejecutar simulaciones
  - **¿Cuándo falla?** Si hay error en la relación entre User y SimulationSession

- **`test_user_can_view_history`**
  - **¿Qué hace?** Crea múltiples simulaciones y verifica que se recuperan
  - **¿Por qué?** Asegurar que el historial de simulaciones funciona
  - **¿Cuándo falla?** Si las consultas a BD no funcionan correctamente

**Clase `TestBB84Integration`** - Tests de integración BB84

- **`test_bb84_simulation_recorded`**
  - **¿Qué hace?** Simula una ejecución de BB84 y verifica que se guardó
  - **¿Por qué?** Validar que los resultados del protocolo BB84 se persisten
  - **¿Cuándo falla?** Si hay error al guardar resultados de simulación

---

### 4. **test_bb84.py** - Tests del Protocolo BB84

**Propósito:** Validar las funciones de generación aleatoria y simulación cuántica.

**Nota:** Estos tests **no** se saltean si falla la importación de `qiskit-aer`: un error de importación hace fallar la suite, para que un problema real no quede oculto detrás de un CI en verde.

#### Tests incluidos:

- **`test_generate_random_bits`**
  - **¿Qué hace?** Verifica que se generan bits aleatorios correctamente
  - **¿Por qué?** Los bits aleatorios son fundamentales para BB84
  - **¿Cuándo falla?** Si la función no retorna la cantidad correcta

- **`test_generate_random_bits_distribution`**
  - **¿Qué hace?** Verifica que la distribución de bits es ~50/50 (0s y 1s)
  - **¿Por qué?** Asegurar que el generador es verdaderamente aleatorio
  - **¿Cuándo falla?** Si hay sesgo en la generación aleatoria

- **`test_generate_random_bases`**
  - **¿Qué hace?** Verifica que se generan bases aleatorias
  - **¿Por qué?** Las bases son necesarias para el protocolo
  - **¿Cuándo falla?** Si la función no funciona correctamente

- **`test_generate_random_bases_distribution`**
  - **¿Qué hace?** Verifica que la distribución de bases es ~50/50
  - **¿Por qué?** Asegurar aleatoriedad en la selección de bases
  - **¿Cuándo falla?** Si hay sesgo en la generación

- **`test_encode_qubit_*`** (4 tests)
  - **¿Qué hace?** Verifica la codificación de qubits en diferentes combinaciones
  - **¿Por qué?** La codificación cuántica es el corazón del protocolo BB84
  - **¿Cuándo falla?** Si hay error con Qiskit o los circuitos cuánticos

- **`test_measure_qubit`**
  - **¿Qué hace?** Verifica la medición de qubits
  - **¿Por qué?** La medición es crítica en el protocolo cuántico
  - **¿Cuándo falla?** Si hay error en la simulación cuántica

- **`test_bb84_protocol_basics`**
  - **¿Qué hace?** Verifica que los pasos básicos del protocolo funcionan
  - **¿Por qué?** Validar la lógica completa del protocolo
  - **¿Cuándo falla?** Si hay error en la implementación del protocolo

- **`TestBB84FullProtocol`** (4 tests)
  - **¿Qué hace?** Ejecuta `simulate_bb84()` de punta a punta, con y sin espía
  - **¿Por qué?** Valida la regla de negocio central: sin espía el QBER es 0 y la clave es segura; con espía el QBER sube y se detecta
  - **¿Cuándo falla?** Si la detección de espionaje deja de funcionar

- **`TestRegresionClaveCorta::test_key_length_minimo_nunca_explota`**
  - **¿Qué hace?** Corre 60 simulaciones con `key_length=10`, el mínimo del formulario
  - **¿Por qué?** Con menos de 4 bits tamizados el cálculo del QBER dividía por cero
  - **¿Cuándo falla?** Si vuelve a aparecer la excepción

- **`TestTrazaDelProtocolo`** (5 tests)
  - **¿Qué hace?** Verifica los bits y bases que devuelve la simulación
  - **¿Por qué?** La animación los dibuja: la clave tamizada tiene que corresponder a las bases coincidentes, sin espía Bob tiene que medir lo que envió Alice, y con espía Eve mide cada qubit
  - **¿Cuándo falla?** Si la traza deja de ser coherente con el protocolo

- **`TestResultadosIntermedios`** (2 tests)
  - **¿Qué hace?** Verifica el tamaño de la muestra usada para el QBER
  - **¿Por qué?** Es el 25% de la clave tamizada con un máximo de 20 bits, y esos bits se descartan de la clave final
  - **¿Cuándo falla?** Si cambia la regla de la muestra

---

### 5. **test_config.py** - Tests de Configuración

**Propósito:** Validar la configuración por entorno y la construcción de la aplicación.

- Producción no arranca con la `SECRET_KEY` de desarrollo
- Las URL `postgres://` que entregan Render y Heroku se corrigen a `postgresql://`
- La factory `create_app()` registra todas las rutas
- Ningún test usa la instancia global de la app, que apunta a `qsec.db`

---

### 6. **test_esquema.py** - Tests de Actualización del Esquema

**Propósito:** Simular a alguien que ya tenía un `qsec.db` creado y actualiza el código.

- Al arrancar, la app agrega las columnas nuevas que le falten a la base
- Los usuarios y sesiones existentes se conservan y el login sigue funcionando
- Arrancar de nuevo no vuelve a modificar nada

---

### 7. **test_animacion.py** - Tests de los Datos de la Animación

**Propósito:** Verificar que la animación recibe los datos reales de la simulación.

- `/api/run-simulation` devuelve los bits y bases de Alice, Bob y Eve
- Sin espía, los bits de Bob coinciden con los de Alice donde coinciden las bases
- La página de la animación ya no genera bits con `Math.random()`

---

## 🚀 Cómo ejecutar los tests

### Ejecutar todos los tests:
```bash
pytest tests/ -v
```

### Ejecutar un archivo específico:
```bash
pytest tests/test_models.py -v
```

### Ejecutar un test específico:
```bash
pytest tests/test_models.py::TestUserModel::test_user_creation -v
```

### Ejecutar con cobertura:
```bash
pytest tests/ -v --cov=app --cov=business --cov=datos --cov=views
```

---

## 📊 Cobertura de Tests

- **Modelos (BD):** ✅ 100%
- **Autenticación:** ✅ Registrado
- **Rutas:** ✅ Básico
- **Formularios:** ✅ Básico
- **Protocolo BB84:** ✅ Protocolo completo, traza y resultados intermedios
- **Datos de la animación:** ✅ La API entrega los bits reales
- **Bases existentes:** ✅ Actualización automática del esquema

---

## 🔍 Fixtures principales: `app` y `client`

Están definidas una sola vez en `tests/conftest.py` y todos los tests las comparten:
1. `app` construye la aplicación con `create_app(TestingConfig)` y una BD SQLite en memoria
2. Antes de crear tablas verifica que la base no apunte a `qsec.db`
3. Crea todas las tablas y las borra al terminar cada test
4. `client` devuelve un cliente para hacer requests sobre esa app

> Antes cada archivo tenía su propia fixture y cambiaba la base a `:memory:` después de importar la app, cuando la conexión ya estaba ligada a `qsec.db`: correr la suite borraba la base de desarrollo.

Esto garantiza que cada test es independiente y no afecta a otros.

---

## ✅ Ciclado de CI/CD

Este proyecto tiene un workflow de GitHub Actions que ejecuta automáticamente:
1. **Tests** - Valida toda la lógica
2. **Flake8** - Valida el estilo del código

Corre en cada push a `main` y en cada pull request contra `main`.

