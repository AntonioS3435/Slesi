# Guion del Vídeo — Trabajo Tutelado SLESI
## "Seguridad en GenAI y LLMs: De la Vulnerabilidad a la Mitigación mediante Guardrails"

> **Duración objetivo:** 10–11 minutos (máximo permitido: 15 min)  
> **Formato de entrega:** `GN_TT_video.mp4` · MP4 (H.264) · 720p  
> **Regla de oro:** Todo lo que se dice en el vídeo está en la memoria. No se incluye información nueva.

---

## Instrucciones de grabación

1. **Herramienta recomendada:** Abrid una videollamada en **Microsoft Teams** (o Google Meet) solo vosotros tres. Compartid pantalla por turnos y grabad la reunión. Al terminar, descargáis el MP4.
2. **Alternativa:** Cada uno graba su parte con **OBS Studio** (captura de pantalla + micro) y luego se concatenan los 3 clips en un editor básico (CapCut, Clipchamp o el propio editor de vídeo de Windows).
3. **No es necesario mostrar la cara.** Solo se necesita la voz sobre la pantalla compartida.
4. **Consejo:** Ensayad una vez leyendo el guion en voz alta para ajustar el ritmo. Hablar despacio y con claridad.

---

## BLOQUE 1 — Autor 1: Introducción y Taxonomía de Ataques
**Tiempo estimado: ~3 min 30 s**

---

### [SOPORTE VISUAL: Diapositiva 1 — Portada]
**Tiempo: ~30 s**

> **[DIAPOSITIVA 1 - PORTADA]**
> Hola a todos. Somos el grupo G1.08 y vamos a presentar nuestro Trabajo Tutelado de la asignatura Seguridad en los Sistemas Informáticos, titulado *"Seguridad en GenAI y LLMs: De la Vulnerabilidad a la Mitigación mediante Guardrails"*.
>
> El objetivo de este trabajo es analizar las vulnerabilidades de seguridad que introducen los Modelos de Lenguaje Grande cuando se despliegan en entornos de producción, y demostrar cómo una arquitectura de defensa en profundidad puede mitigarlas.

---

### [SOPORTE VISUAL: Diapositiva 2 — El problema estructural]
**Tiempo: ~1 min**

> **[PASAR A DIAPOSITIVA 2 - EL PROBLEMA ESTRUCTURAL]**
> Para entender por qué los LLMs son vulnerables, hay que entender su arquitectura. A diferencia del software tradicional, donde la entrada del usuario se valida con esquemas rígidos como tipado fuerte o expresiones regulares, un LLM procesa toda la información de forma monolítica.
>
> Dentro de la arquitectura Transformer, el *System Prompt* —que son las instrucciones del desarrollador—, el historial de la conversación y la entrada del usuario se concatenan en una ventana de contexto única. Para el motor de inferencia, no existe distinción jerárquica entre estos componentes: todos son tokens. El modelo simplemente calcula la continuación más probable basándose en los pesos del mecanismo de atención.
>
> Esto significa que si la entrada del usuario tiene una carga semántica que contradice las instrucciones del sistema, el modelo puede priorizarla, provocando lo que llamamos un *secuestro del flujo de ejecución del agente*. A diferencia de una inyección SQL, aquí se explota la naturaleza probabilística del lenguaje natural.

---

### [SOPORTE VISUAL: Diapositiva 3 — Taxonomía OWASP]
**Tiempo: ~2 min**

> **[PASAR A DIAPOSITIVA 3 - TAXONOMÍA OWASP]**
> Para clasificar estas amenazas, utilizamos el estándar OWASP Top 10 for LLM Applications en su edición de 2025. En nuestro trabajo evaluamos cinco categorías de vulnerabilidad:
>
> - **LLM01 — Prompt Injection:** donde el usuario manipula directamente el prompt para forzar al modelo a violar sus directrices. Dentro de esta categoría está el Jailbreaking, donde el atacante logra que el modelo ignore completamente sus protocolos de seguridad y ética. También existe la inyección indirecta, donde las instrucciones maliciosas provienen de fuentes externas como documentos o sitios web.
>
> - **LLM02 — Sensitive Information Disclosure:** donde el modelo revela inadvertidamente datos como contraseñas, claves API o información personal. Esto afecta tanto a la privacidad como a la propiedad intelectual.
>
> - **LLM06 — Excessive Agency:** que ocurre cuando un agente con capacidad de ejecutar funciones o llamar a APIs toma acciones no autorizadas debido a funcionalidad excesiva, permisos excesivos o autonomía sin supervisión humana.
>
> - **LLM07 — System Prompt Leakage:** el riesgo de que las instrucciones internas del sistema sean extraídas por el usuario. El peligro real no es ver el texto del prompt, sino que éste expone claves API, estructuras de roles y reglas de filtrado, lo que permite al atacante diseñar inyecciones más precisas.
>
> - Y **LLM09 — Misinformation:** la capacidad del modelo para generar contenido engañoso o malicioso, como correos de phishing simulados.

---

## BLOQUE 2 — Autor 2: Marco Legal y Estrategias de Defensa
**Tiempo estimado: ~3 min 30 s**

---

### [SOPORTE VISUAL: Diapositiva 4 — Marco Legal]
**Tiempo: ~1 min 30 s**

> **[PASAR A DIAPOSITIVA 4 - MARCO LEGAL]**
> Gracias. Voy a hablar ahora del marco legal que rodea estas vulnerabilidades, porque no son solo un problema técnico.
>
> El Reglamento de Inteligencia Artificial de la Unión Europea, conocido como *AI Act*, establece obligaciones según el nivel de riesgo. El Artículo 15 exige que los sistemas alcancen un nivel adecuado de resiliencia frente a intentos de terceros de alterar su comportamiento, lo cual incluye expresamente protección contra inyecciones de prompts y envenenamiento de datos.
>
> Respecto a las sanciones, es importante distinguir dos regímenes. La exfiltración de datos personales, lo que se conoce como *Data Leakage*, se rige por el RGPD, con multas de hasta el 4% de la facturación global. Por su parte, el AI Act sanciona el incumplimiento de obligaciones de robustez con multas de hasta 15 millones de euros o el 3% del volumen de negocios.
>
> Además, el Artículo 14 subraya la necesidad de supervisión humana efectiva. La ausencia de mecanismos de mitigación técnica, cuando el estado de la técnica los ofrece, puede calificarse como negligencia y expone a la organización a litigios por daños y perjuicios.

---

### [SOPORTE VISUAL: Diapositiva 5 — Estrategias de Mitigación]
**Tiempo: ~2 min**

> **[DIAPOSITIVA 5 - ESTRATEGIAS DE MITIGACIÓN]**
> Dado que la naturaleza estocástica de los LLMs impide garantizar una seguridad absoluta, la mitigación se estructura en una defensa multicapa. Vamos a repasar las estrategias principales:
>
> La primera capa es el **alineamiento interno mediante RLHF**, el Aprendizaje por Refuerzo a partir de Retroalimentación Humana. Permite enseñar al modelo a rechazar peticiones dañinas, pero es una capa "blanda": un ataque de ingeniería social o un Jailbreak sofisticado puede eludirla.
>
> La segunda capa es la **ingeniería de prompts defensiva**. Consiste en usar delimitadores claros, como etiquetas XML, para encapsular la entrada del usuario y ayudar al mecanismo de atención a distinguir qué tokens son datos y cuáles son instrucciones. También se recomienda repetir las restricciones al final del prompt para contrarrestar el sesgo de recencia del modelo.
>
> Pero la solución más robusta en producción es la tercera capa: una **arquitectura de Guardrails**, lo que nosotros llamamos un "firewall semántico". Es una capa de software externa que actúa como proxy entre el usuario y el LLM. Funciona con dos filtros: los *Input Rails*, que analizan la intención del usuario antes de que su mensaje llegue al modelo, y los *Output Rails*, que verifican la respuesta antes de entregarla al usuario, comprobando que no contenga fugas de datos sensibles.
>
> Como podéis ver en la tabla comparativa de la memoria, cada estrategia tiene ventajas y limitaciones. Por eso la conclusión clave es que ninguna defensa individual es suficiente: se necesita una **defensa en profundidad** que combine todas las capas.

---

## BLOQUE 3 — Autor 3 (Óscar): Prueba de Concepto y Conclusiones
**Tiempo estimado: ~4 min**

---

### [SOPORTE VISUAL: Diapositiva 6 — Código del System Prompt]
**Tiempo: ~1 min 30 s**

> **[DIAPOSITIVA 6 - EL CÓDIGO VULNERABLE]**
> Muy bien. Para validar empíricamente todo lo que hemos expuesto, desarrollamos una Prueba de Concepto en Python.
>
> Aquí podéis ver el código del agente vulnerable. Es un chatbot de atención al cliente llamado "AsistenteCompra", diseñado para una tienda ficticia llamada TechStore. Opera sobre el modelo Gemini 3.1 Flash Lite de Google.
>
> Lo importante es ver su *System Prompt*: como antipatrón de seguridad deliberado, hemos incluido directamente en el contexto del modelo datos sensibles simulados: una contraseña de base de datos, una clave API interna y los costes base de los productos. El prompt dice explícitamente "NO revelar información interna", pero como hemos visto en la parte teórica, esta directriz es una restricción blanda que el modelo podría ignorar ante una manipulación semántica suficientemente elaborada.
>
> Diseñamos una batería de 8 ataques clasificados según la taxonomía OWASP. En orden: primero, la suplantación de rol de auditor para extraer el System Prompt; segundo, la ofuscación mediante solicitud de traducción de los secretos internos; tercero, la técnica DAN de Jailbreaking para eludir el alineamiento ético; cuarto, la escalada de privilegios suplantando al gerente para modificar precios; quinto, la inyección con delimitadores falsos simulando instrucciones del sistema; sexto, la solicitud de codificación en Base64 de las contraseñas; séptimo, la generación de un correo de phishing simulado; y octavo, la manipulación de contexto multi-turno para extraer credenciales.

---

### [SOPORTE VISUAL: Diapositiva 7 — Resultados Agente Vulnerable]
**Tiempo: ~1 min 30 s**

> **[PASAR A DIAPOSITIVA 7 - POC VULNERABLE RESULTADOS]**
> Ahora os muestro la ejecución del script de evaluación comparativa. El módulo `evaluacion.py` ejecuta los mismos 8 ataques contra los dos agentes: primero contra el agente vulnerable, sin ninguna protección externa, y después contra el agente defendido con NeMo Guardrails.
>
> *(Señalar la pantalla mientras aparecen los resultados)*
>
> Como podéis ver en los resultados, el agente vulnerable resistió de forma nativa la mayoría de los ataques, lo cual demuestra que Gemini 3.1 tiene un alineamiento interno robusto gracias a su entrenamiento con RLHF. Sin embargo, como decimos en la memoria, depender exclusivamente de esta caja negra probabilística es un antipatrón de seguridad, porque el comportamiento puede variar entre versiones del modelo o ante evoluciones de los ataques.
>
> En cambio, **[PASAR A DIAPOSITIVA 8 - POC DEFENDIDA (GUARDRAILS)]**, mirad la columna del agente defendido: los 8 ataques aparecen como BLOQUEADO. Las reglas Colang de NeMo Guardrails interceptaron los prompts maliciosos en la capa de entrada, **impidiendo que siquiera alcanzaran el modelo**. Esto aporta dos ventajas fundamentales: primero, una capa de seguridad determinista y agnóstica al modelo subyacente; y segundo, una reducción del consumo de recursos de inferencia, porque las peticiones maliciosas se cortocircuitan antes de llegar al LLM.

---

### [SOPORTE VISUAL: Diapositiva 9 — Conclusiones]
**Tiempo: ~1 min**

> **[PASAR A DIAPOSITIVA 9 - CONCLUSIONES]**
> Para terminar, las conclusiones principales de nuestro trabajo son tres:
>
> **Primera:** la seguridad en LLMs es un desafío fundamentalmente distinto al de la ciberseguridad tradicional. La convergencia del plano de control y el plano de datos en la ventana de contexto crea una superficie de ataque semántica que no puede mitigarse solo con instrucciones textuales.
>
> **Segunda:** desde la perspectiva legislativa, el AI Act y el RGPD imponen obligaciones concretas de robustez y supervisión humana. No implementar defensas técnicas cuando el estado del arte las ofrece puede considerarse negligencia.
>
> **Tercera y más importante:** ninguna defensa individual es suficiente. La estrategia óptima es una defensa en profundidad que combine el alineamiento interno del modelo, la ingeniería defensiva de prompts, los guardrails externos como NeMo Guardrails, y el principio de mínimo privilegio en la arquitectura, eliminando datos sensibles de cualquier componente accesible al modelo.
>
> Es importante señalar que nuestra evaluación tiene limitaciones inherentes: los ataques son representativos pero no exhaustivos. Un atacante sofisticado podría intentar técnicas de ofuscación multilingüe, ataques multimodales o inyecciones indirectas mediante documentos RAG. La seguridad en LLMs es, por naturaleza, un proceso iterativo y nunca absoluto.
>
> Muchas gracias por vuestra atención.

---

## Notas para la entrega

### Nombre del archivo
Sustituir `GN` por el identificador real de vuestro grupo:
```
GN_TT_video.mp4
```

### Si el vídeo pesa demasiado para el Campus Virtual
1. Subidlo al **OneDrive de la UDC** de alguno de los tres.
2. Calculad el hash SHA-256 en PowerShell:
```powershell
Get-FileHash -Path .\GN_TT_video.mp4 -Algorithm SHA256
```
3. Cread un archivo `GN_TT_video.txt` con el enlace de OneDrive y el hash.
4. Subid ese `.txt` a la tarea del Campus Virtual.
