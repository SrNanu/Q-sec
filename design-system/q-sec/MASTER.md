# Design System Master File — Q-Sec Modern Scientific

**Project:** Q-Sec (Quantum Key Distribution Simulator)  
**Target:** Scientific Engineering & Deep-Tech Cybersecurity  
**Design Principles:** Clean, Human, High Precision, High Contrast, Modern Minimalism  

---

## 1. Color Palette

| Role | Hex / Value | CSS Variable | Description |
|------|-------------|--------------|-------------|
| **Primary** | `#2563eb` | `--qsec-primary` | Deep Precision Blue |
| **Primary Hover** | `#1d4ed8` | `--qsec-primary-hover` | Darker blue for active/hover states |
| **Primary Light** | `rgba(37, 99, 235, 0.1)` | `--qsec-primary-light` | Subtle primary wash |
| **Success** | `#059669` | `--qsec-success` | Emerald green (Secure channel) |
| **Danger** | `#dc2626` | `--qsec-danger` | Ruby red (Eve detected / Aborted) |
| **Warning** | `#d97706` | `--qsec-warning` | Amber (Elevated QBER alert) |

### Theme Backgrounds & Surfaces

| Token | Light Theme | Dark Theme (`[data-bs-theme="dark"]`) |
|-------|-------------|---------------------------------------|
| `--bg-page` | `#f8fafc` (Pure Slate) | `#0b0f19` (Obsidian Slate) |
| `--bg-surface` | `#ffffff` (Card white) | `#111827` (Card dark slate) |
| `--bg-surface-secondary` | `#f1f5f9` | `#172033` |
| `--border-subtle` | `#e2e8f0` | `#1f293d` |
| `--border-strong` | `#cbd5e1` | `#374151` |
| `--text-primary` | `#0f172a` | `#f8fafc` |
| `--text-secondary` | `#475569` | `#94a3b8` |
| `--text-muted` | `#64748b` | `#64748b` |

---

## 2. Typography

- **Primary Font (Headings & Body):** `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Monospace Font (Qubits, Key Bits, Telemetry, Code):** `'JetBrains Mono', SFMono-Regular, Consolas, monospace`
- **Dirac Notation:** Rendered cleanly in KaTeX / JetBrains Mono ($|0\rangle, |1\rangle, |+\rangle, |-\rangle$).

---

## 3. Spacing & Elevation

- **Card Radius:** `12px` (`0.75rem`)
- **Pill Radius:** `9999px`
- **Elevation / Shadows:**
  - Light: `0 1px 3px rgba(0, 0, 0, 0.05)`
  - Dark: `0 4px 16px rgba(0, 0, 0, 0.35)`
- **Borders:** 1px hairline solid borders (`--border-subtle`). No fluorescent or multi-colored top borders.
