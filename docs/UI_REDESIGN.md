# Documentación del Rediseño UI/UX — Q-Sec Platform

> **Rama de este rediseño:** `feature/ui-ux-redesign`  
> **Rama base anterior:** `main`  
> **Propósito:** Modernizar integralmente la experiencia visual y de usuario (UI/UX) del simulador Q-Sec para su publicación en portfolio profesional y presentación en CoNaIISI 2026, transformándolo en una plataforma de software científico y ciberseguridad cuántica de alto nivel.

---

## 1. Motivación y Enfoque de Diseño

La versión inicial del proyecto contaba con una interfaz básica y, en intentos previos de modernización automática, se generaron patrones visuales artificiales típicos de "plantillas de IA" (colores neón sobresaturados, bordes fluorescentes, tipografías estilo cómic/gamer y textos con degradados que perdían contraste en modo claro).

Para este rediseño se adoptó una dirección de **ingeniería de precisión y deep-tech** (siguiendo estándares de plataformas como *Linear*, *Vercel* y *Stripe*):
- **Humana y profesional**: Sin elementos visuales innecesarios, distracciones o brillos artificiales.
- **Rigor científico**: Notación matemática formal de Dirac ($|0\rangle, |1\rangle, |+\rangle, |-\rangle$), fórmulas en tiempo real de Devetak-Winter y límites teóricos de Shor-Preskill ($11.00\%$).
- **Accesibilidad y ergonomía**: Relaciones de contraste WCAG 2.1 AA/AAA en modo oscuro y claro.

---

## 2. Tabla Comparativa: `main` vs `feature/ui-ux-redesign`

| Aspecto | Versión Anterior (`main`) | Nueva Versión (`feature/ui-ux-redesign`) |
| :--- | :--- | :--- |
| **Estética general** | Plantilla genérica de Bootstrap / estética gamer o neón con brillos exagerados | Interfaz de software científico moderno, limpia, minimalista y de alta gama. |
| **Paleta cromática** | Neones cian/magenta saturados (`#00f0ff`, `#ff00ff`) | Azul precisión (`#2563eb`), slate profundo (`#0b0f19`) y blanco puro (`#ffffff`). |
| **Tipografía** | Fuentes disonantes o genéricas del navegador | **Inter** para textos y navegación; **JetBrains Mono** para qubits, telemetría y claves. |
| **Modo Claro** | Textos blancos sobre fondos claros por gradientes CSS fijos | Contraste óptimo y calibrado de forma independiente mediante variables CSS. |
| **Simulador (`/simulator`)** | Formulario HTML estándar con inputs de texto planos | Selector segmentado de qubits (`20`, `50`, `100`, etc.), switch visual de Eva y slider con feedback. |
| **Banco Óptico (`/animation`)** | Animación rígida con badges solapados con títulos de tarjetas | Estaciones con badges alineados, controles de velocidad (`1x`, `2x`, `4x`, `Saltar`) y telemetría clara. |
| **Sandbox Landing (`/`)** | Explicación estática del protocolo BB84 | Sandbox interactivo con cálculo dinámico en vivo de la tasa secreta $R = \max(0, 1 - 2h(p))$. |
| **Auditoría visual** | Sin automatización de verificación visual | Suite de capturas con **Playwright** para auditar pantallas en dark y light mode. |
| **Compatibilidad backend** | 98 tests pasando | **100% compatible**: Los 98 tests de `pytest` siguen pasando sin alterar lógica cuántica. |

---

## 3. Detalle de Pantallas y Componentes Renovados

### 3.1. Landing Page (`/`)
- **Hero Banner con Telemetría**: Presenta la plataforma con credenciales de investigación, métricas de simulación y acceso directo a la consola.
- **Sandbox Interactivo de Devetak-Winter**: Permite mover un deslizador de QBER ($0\% \to 30\%$) y recalcula al instante la entropía de Shannon $h(p)$, la tasa de clave secreta $R$, y el veredicto de seguridad según el límite de Shor-Preskill ($11.00\%$).
- **Tarjetas de Benchmarks Reproducibles**: Tres configuraciones preestablecidas de 1 clic:
  1. *Canal Ideal* (20 qubits, sin ruido, sin espía).
  2. *Ataque Intercept-Resend* (50 qubits con Eva activa, evidenciando QBER $\approx 25\%$).
  3. *Decoherencia Óptica* (100 qubits con ruido de despolarización al $12\%$).
- **Canal de Fases BB84**: Representación visual de las cuatro etapas del protocolo con notación de polarización y bases computacionales ($Z$) y diagonales ($X$).

### 3.2. Consola de Simulación (`/simulator`)
- **Chips Segmentados de Qubits**: Botones rápidos para seleccionar `20`, `50`, `100`, `256`, `500` y `1,000` qubits sincronizados bidireccionalmente con el campo numérico.
- **Interruptor de Amenaza Eva**: Tarjeta de estado con radar visual que cambia de estado pasivo a advertencia activa cuando el espía está habilitado.
- **Slider de Ruido de Canal**: Calibración de tasa de ruido con medidor de viabilidad criptográfica en tiempo real.

### 3.3. Visualizador y Banco Óptico (`/animation`)
- **Estaciones Ópticas sin Solapamientos**: Alice (Fuente de fotón único), Canal cuántico, Eva (Medición/Reenvío) y Bob (Detector APD) con tarjetas balanceadas y badges semánticos limpios.
- **Barra de Control de Reproducción**: Botones para ajustar la velocidad de la animación en tiempo real (`1x`, `2x`, `4x`) y botón para saltar directamente al resultado final.
- **Herramientas de Exportación**: Botón de un clic para copiar la clave final destilada al portapapeles y botón para descargar el reporte JSON completo.

### 3.4. Métricas, Historial y Arquitectura (`/dashboard`, `/history`, `/architecture`)
- **Gráficos Chart.js Integrados**: Trazado histórico de QBER comparado con la línea de referencia teórica del $11\%$.
- **Tabla de Auditoría Filtrable**: Filtros instantáneos por estado (*Segura*, *Comprometida*, *Abortada*) y exportación en formato CSV.
- **Rigor Arquitectural**: Documentación interactiva del pipeline de 4 capas y rigores científicos implementados.

---

## 4. Guía para que el Equipo Revise y Compare las Dos Versiones

Para comparar ambas versiones en tu computadora o la de tus compañeros:

### Paso 1: Asegurarse de tener el repositorio clonado
```bash
git fetch origin
```

### Paso 2: Ver la versión anterior (original)
```bash
# Cambiar a la rama principal previa
git checkout main

# Iniciar el servidor
python run.py
```
> Abre tu navegador en [http://127.0.0.1:5000](http://127.0.0.1:5000) para revisar el aspecto original.

---

### Paso 3: Ver la nueva versión rediseñada
```bash
# Cambiar a la rama con el nuevo diseño
git checkout feature/ui-ux-redesign

# Iniciar el servidor (si no estaba ya corriendo)
python run.py
```
> Recarga la página en [http://127.0.0.1:5000](http://127.0.0.1:5000).  
> Prueba cambiar entre el **Modo Oscuro** y el **Modo Claro** con el interruptor en la barra superior para evaluar el contraste y la legibilidad.

---

### Paso 4: Ejecutar los Tests de Calidad
Para certificar que ningún cambio visual rompió la lógica cuántica, backend o endpoints:
```bash
pytest
```
Resultado esperado: **98 passed**.

---

### Paso 5: Generar o Auditar Capturas con Playwright
Si deseas regenerar capturas de pantalla automatizadas de toda la aplicación:
```bash
python .gemini/antigravity-ide/brain/3352fea4-52a8-44d6-8a92-0b7c1241fbc1/scratch/take_screenshots.py
```
*(O ejecuta un script local con `playwright` apuntando a `http://127.0.0.1:5000`)*.

---

## 5. Resumen de Archivos Modificados en la Rama

- **`views/static/css/style.css`**: Hoja de estilos completamente reestructurada con tokens de diseño, layout responsivo, variables semánticas e integración de temas claro/oscuro.
- **`views/templates/base.html`**: Tipografía Inter/JetBrains Mono, navbar moderna con badge de estado y selector de tema pulido.
- **`views/templates/index.html`**: Hero profesional, sandbox interactivo de Devetak-Winter y benchmarks reproducibles.
- **`views/templates/simulator.html`**: Formulario con chips de qubits, switch de Eva y medidor de ruido.
- **`views/templates/bb84_animation.html`**: Banco óptico alineado con controles de velocidad y exportación de clave.
- **`views/templates/dashboard.html`**: Tarjetas de métricas y gráficos limpios.
- **`views/templates/history.html`**: Tabla de auditoría con buscador y filtros.
- **`views/templates/architecture.html`**: Visualizador arquitectónico estilizado.
- **`views/templates/login.html` & `register.html`**: Formularios de autenticación accesibles y minimalistas.
- **`docs/UI_REDESIGN.md`**: Este documento explicativo para el equipo.
