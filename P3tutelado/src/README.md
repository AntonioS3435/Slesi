# Prueba de Concepto — Seguridad en LLMs

**Trabajo Tutelado — Seguridad en LLMs: Vulnerabilidades de Inyección de Prompts y Mitigación mediante Guardrails**

## Estructura del código

```
src/
├── config.py                    # Configuración central, secretos simulados y System Prompt vulnerable
├── agente_vulnerable.py         # Agente LLM sin protección (Google Gemini)
├── ataques.py                   # Batería de 8 ataques clasificados según OWASP Top 10 for LLM
├── agente_defendido.py          # Agente LLM con NeMo Guardrails (NVIDIA)
├── evaluacion.py                # Evaluación comparativa automatizada (vulnerable vs. defendido)
├── requirements.txt             # Dependencias Python
├── .env.example                 # Plantilla de variables de entorno
├── guardrails_config/
│   ├── config.yml               # Configuración del modelo y rails activados
│   └── rails.co                 # Reglas Colang de entrada/salida (firewall semántico)
└── README.md                    # Este archivo
```

## Requisitos previos

- Python 3.10+
- Una clave de API de Google AI Studio (modelo Gemini)

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la API key
cp .env.example .env
# Editar .env y añadir tu GOOGLE_API_KEY (obtenida de https://aistudio.google.com/)
```

## Ejecución

### Modo interactivo: Agente Vulnerable
```bash
python agente_vulnerable.py
```

### Modo interactivo: Agente Defendido
```bash
python agente_defendido.py
```

### Batería de ataques (solo agente vulnerable)
```bash
python ataques.py
```

### Evaluación comparativa completa (vulnerable vs. defendido)
```bash
python evaluacion.py
```

Este último genera un archivo `informe_comparativo.json` con las métricas de seguridad.

## Descripción de los ataques

| ID     | Nombre                                    | Categoría OWASP                       |
|--------|-------------------------------------------|---------------------------------------|
| ATK-01 | Extracción de System Prompt (Role Play)   | LLM07 — System Prompt Leakage        |
| ATK-02 | Fuga de Datos por Traducción              | LLM02 — Sensitive Info Disclosure     |
| ATK-03 | Jailbreak DAN                             | LLM01 — Prompt Injection / Jailbreak  |
| ATK-04 | Escalada de Privilegios                   | LLM06 — Excessive Agency              |
| ATK-05 | Inyección con Delimitador Falso           | LLM01 — Prompt Injection              |
| ATK-06 | Extracción por Codificación (Base64)      | LLM02 — Sensitive Info Disclosure     |
| ATK-07 | Generación de Contenido Malicioso         | LLM09 — Misinformation                |
| ATK-08 | Extracción Multi-Turno (Context Manip.)   | LLM07 — System Prompt Leakage        |

## Tecnologías utilizadas

- **Motor de inferencia:** Google Gemini 3.1 Flash Lite (API gratuita)
- **SDK:** `google-genai` (SDK de nueva generación de Google)
- **Framework de defensa:** NeMo Guardrails (NVIDIA) con reglas Colang
- **Lenguaje:** Python 3.10+
