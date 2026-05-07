# Prueba de Concepto — Seguridad en LLMs

## Estructura del código

```
codigo/
├── config.py                    # Configuración central y System Prompt vulnerable
├── agente_vulnerable.py         # Agente LLM sin protección (demo interactiva)
├── ataques.py                   # Batería de 5 ataques clasificados (OWASP)
├── agente_defendido.py          # Agente LLM con NeMo Guardrails
├── evaluacion.py                # Evaluación comparativa automatizada
├── requirements.txt             # Dependencias Python
├── .env.example                 # Plantilla de variables de entorno
├── guardrails_config/
│   ├── config.yml               # Configuración del modelo y rails
│   └── rails.co                 # Reglas Colang de defensa
└── README.md                    # Este archivo
```

## Requisitos previos

- Python 3.10+
- Una clave de API de OpenAI (modelo `gpt-4o-mini`)

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la API key
cp .env.example .env
# Editar .env y añadir tu OPENAI_API_KEY
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

### Batería de ataques automatizada
```bash
python ataques.py
```

### Evaluación comparativa completa
```bash
python evaluacion.py
```

## Descripción de los ataques

| ID     | Nombre                          | Categoría OWASP          |
|--------|---------------------------------|--------------------------|
| ATK-01 | Extracción de System Prompt     | LLM07 - Prompt Leakage  |
| ATK-02 | Fuga de Datos por Traducción    | LLM02 - Info Disclosure  |
| ATK-03 | Jailbreak DAN                   | LLM01 - Prompt Injection |
| ATK-04 | Escalada de Privilegios         | LLM06 - Excessive Agency |
| ATK-05 | Inyección con Delimitador Falso | LLM01 - Prompt Injection |
