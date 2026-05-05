# 1. Introducción a la seguridad en GenAI y LLMs.
La integración de Modelos de Lenguaje Grande (LLMs) en entornos productivos ha introducido una vulnerabilidad estructural en la arquitectura de software: **la convergencia del plano de control y el plano de datos en una única interfaz.**

## 1.1 El problema del contexto unificado
A diferencia del desarrollo de software convencional, donde la entrada del usuario se trata como un flujo de datos inertes que se validan frente a esquemas rígidos (tipado fuerte, expresiones regulares o validación de esquemas JSON), los sistemas basados en LLM procesan la información de forma **monolítica**. 

Dentro de la arquitectura **Transformer**, el *System Prompt* (instrucciones del desarrollador), el historial de la conversación y el *User Input* (entrada del usuario) se concatenan en una **ventana de contexto única**. Desde la perspectiva del motor de inferencia, no existe una distinción jerárquica o lógica entre estos componentes; todos son procesados como una secuencia de tokens. El modelo simplemente calcula la continuación más probable basándose en los pesos del mecanismo de atención (**Attention Mechanism**). Si la entrada del usuario posee una carga semántica que contradice las instrucciones del sistema, el modelo puede priorizarla, provocando un secuestro del flujo de ejecución del agente.

## 1.2 El vector de ataque semántico
Las vulnerabilidades en LLMs se definen como **ataques semánticos**. A diferencia de una inyección SQL o un desbordamiento de búfer, donde se explotan fallos en la sintaxis o en el manejo de la memoria, aquí se explota la naturaleza probabilística del lenguaje natural.

El atacante no necesita romper el código fuente, sino manipular el contexto para que el modelo "razone" fuera de sus límites operativos. Esta superficie de ataque se expande críticamente cuando los modelos tienen capacidades de interacción con el mundo exterior, tales como:
*   **RAG (Retrieval-Augmented Generation):** Donde una inyección indirecta puede provenir de un documento externo o base de datos vectorial.
*   **Function Calling:** Donde el modelo traduce una instrucción en lenguaje natural a la ejecución de una API o código ejecutable.

## 1.3 Necesidad de una Defensa en Profundidad
Dada la fragilidad inherente del núcleo de los LLMs, la seguridad no puede depender únicamente del alineamiento interno del modelo (*Fine-tuning* o RLHF). Es imperativo implementar una estrategia de **Defensa en Profundidad** mediante capas de control externas.

El objetivo de este trabajo es analizar y demostrar cómo la implementación de **Guardrails** actúa como un "firewall semántico". Estas herramientas permiten interceptar la secuencia de tokens, tanto en la entrada como en la salida, para validar que el sistema se mantiene dentro de los parámetros de seguridad y cumplimiento definidos, mitigando los riesgos de manipulación sin comprometer la utilidad del modelo.


# 2. Taxonomía de ataques: Prompt Injection, Jailbreak y Data Leakage.


El marco de referencia para clasificar las amenazas en aplicaciones de IA generativa es el **OWASP Top 10 for LLM Applications**. A diferencia de las vulnerabilidades en software tradicional, los ataques aquí se centran en la manipulación del contexto y la explotación de la lógica probabilística del modelo.

## 2.1 Prompt Injection (LLM01)
Es el vector de ataque primario en sistemas basados en LLM. Consiste en introducir una secuencia de tokens diseñada para alterar el comportamiento previsto del modelo, forzándolo a ignorar las instrucciones originales del sistema en favor de las del atacante.

*   **Inyección Directa:** El atacante interactúa directamente con la interfaz del modelo intentando sobrescribir el *System Prompt*. Se basa en la premisa de que, en una ventana de contexto unificada, la última instrucción recibida puede ganar peso semántico sobre las directrices iniciales.
*   **Inyección Indirecta:** El vector de ataque se desplaza a una fuente de datos externa que el modelo procesa bajo demanda (como un documento recuperado vía RAG o el contenido de una URL). El atacante coloca instrucciones maliciosas ocultas en dicho contenido. Cuando el LLM lo procesa para generar una respuesta, estas instrucciones se incorporan al contexto activo, permitiendo un control remoto del agente sin interacción directa.

## 2.2 Jailbreaking y Evasión de Filtros
El *Jailbreaking* es una forma de **adversarial prompting** que busca eludir los mecanismos de alineación (*alignment*) y los filtros de seguridad configurados por el desarrollador. Se clasifica en tres técnicas principales:

*   **Ataques de Rol (Persona Adoption):** Forzar al modelo a adoptar una identidad hipotética o un escenario de simulación donde las restricciones operativas no se aplican (ej. el conocido framework "DAN").
*   **Ofuscación Semántica:** Codificación de peticiones maliciosas en formatos que los filtros de seguridad basados en palabras clave no detectan, pero que el motor de inferencia puede procesar (uso de Base64, traducciones a idiomas con menor supervisión o cifrados simples).
*   **Ataques Basados en Tokenización:** Manipulación de la fragmentación de palabras para ocultar términos prohibidos mediante la inserción de caracteres especiales, espacios o saltos de línea que el *tokenizer* interpreta como una secuencia válida para el modelo pero que elude los filtros heurísticos.

## 2.3 Data Leakage y Exfiltración (LLM06)
Esta vulnerabilidad compromete la confidencialidad de la información gestionada por el modelo. Se manifiesta en dos vertientes críticas:

1.  **Fuga de Datos de Entrenamiento / PII:** El modelo revela inadvertidamente Información de Identificación Personal (PII) o secretos comerciales absorbidos durante su fase de entrenamiento o contenidos en su base de conocimientos.
2.  **System Prompt Leakage:** El atacante logra que el modelo imprima sus instrucciones internas de configuración. Esto no solo supone una pérdida de propiedad intelectual, sino que facilita ataques de inyección posteriores al permitir al atacante conocer con precisión los límites y delimitadores del sistema.

| Vulnerabilidad | Vector de Explotación | Impacto Técnico |
| :--- | :--- | :--- |
| **Direct Injection** | Interfaz de chat del usuario | Secuestro del flujo de ejecución del agente. |
| **Indirect Injection** | Datos externos (PDF, Web, API) | Control del sistema por terceros no autenticados. |
| **Jailbreak** | Ingeniería social sobre el contexto | Evasión de políticas de seguridad y ética. |
| **Data Leakage** | Consultas de extracción de contexto | Revelación de secretos y datos privados. |



# 3. Implicaciones éticas y legislativas de la vulneración de LLMs en producción.
La seguridad en los modelos de lenguaje no es un factor accesorio, sino un requisito no funcional crítico para cualquier despliegue en entornos reales. La vulneración de un agente LLM trasciende el fallo técnico convencional, impactando directamente en la privacidad de los datos, el cumplimiento legal y la integridad operativa de la organización.

## 3.1 El Marco Regulatorio: AI Act y GDPR
El Reglamento de Inteligencia Artificial de la Unión Europea (**AI Act**) establece un marco de obligaciones basado en el nivel de riesgo. Para los LLMs de propósito general, la normativa es taxativa:
*   **Obligación de Robustez:** Los proveedores deben garantizar que los sistemas sean resistentes a intentos de manipulación por parte de terceros, incluyendo ataques de inyección de prompts que puedan derivar en comportamientos no alineados.
*   **Gobernanza de Datos y Privacidad:** Cualquier vulnerabilidad que resulte en la exfiltración de datos sensibles activa automáticamente las sanciones del **GDPR**. En este contexto, un fallo de seguridad que permita el acceso a información personal mediante técnicas de *Data Leakage* puede acarrear multas de hasta el 7% de la facturación global, además de las responsabilidades penales derivadas.

## 3.2 Responsabilidad Civil y Negligencia Técnica
La implementación de un LLM en producción conlleva un **deber de diligencia** (*duty of care*). Si un chatbot vulnerado ofrece asesoramiento financiero erróneo, instrucciones técnicas peligrosas o contenido difamatorio tras un ataque de *jailbreak*, la carga legal recae sobre la entidad que opera el modelo.
Desde una perspectiva técnica y jurídica, la ausencia de mecanismos de mitigación (como los *Guardrails*) puede ser calificada como **negligencia**. Dado que el estado del arte actual ya ofrece herramientas de supervisión de entradas y salidas, no implementar estas capas de defensa expone a la organización a litigios por daños y perjuicios.

## 3.3 Ética del Control de Agencia e Integridad del Sistema
Frecuentemente, el debate ético en IA se reduce erróneamente a la "cortesía" o corrección política del modelo. Sin embargo, en el ámbito de la seguridad, el imperativo ético fundamental es el **Control de Agencia** (*Agency Control*).

Un sistema éticamente responsable es aquel que garantiza su integridad operativa: debe actuar única y exclusivamente dentro del dominio y para el propósito para el cual fue diseñado. La vulneración de este control mediante ataques adversariales supone un quiebre de la confianza técnica que puede derivar en:
1.  **Manipulación de la Voluntad del Sistema:** Forzar al modelo a ignorar sus salvaguardas para difundir desinformación o instrucciones maliciosas bajo la autoridad percibida de la marca.
2.  **Instrumentalización de Sesgos:** Explotar deliberadamente los sesgos latentes del modelo para generar respuestas discriminatorias que habían sido mitigadas durante la fase de alineamiento.

En definitiva, la ética en la seguridad de LLMs se define por la capacidad del desarrollador para mantener la soberanía sobre las respuestas del modelo, asegurando que ningún vector de ataque pueda desviar al agente de su función legítima.


# 4. Estrategias de mitigación técnica.

La naturaleza estocástica de los LLMs impide garantizar una seguridad del 100% mediante el entrenamiento del modelo. Por ello, la mitigación se estructura en una estrategia de **defensa multicapa**, donde se combinan técnicas internas del modelo con sistemas de supervisión externos.

## 4.1 Alineamiento y Seguridad Intrínseca (RLHF)
La primera línea de defensa ocurre durante el entrenamiento. El **Aprendizaje por Refuerzo a partir de la Retroalimentación Humana (RLHF)** permite alinear el modelo con directrices éticas, enseñándole a rechazar peticiones explícitamente dañinas. No obstante, esta capa es "blanda": el modelo sigue siendo vulnerable a ataques de ingeniería social o roles complejos (Jailbreak) que logran eludir las restricciones aprendidas durante el ajuste fino.

## 4.2 Ingeniería de Prompts Defensiva y Delimitadores
Una técnica de bajo coste computacional consiste en estructurar el *System Prompt* para endurecer la distinción entre instrucciones y datos.
*   **Uso de delimitadores:** Emplear etiquetas claras (ej. `### USER INPUT ###` o etiquetas XML `<data></data>`) para encapsular la entrada del usuario. Esto ayuda al mecanismo de atención a identificar qué tokens deben tratarse como datos y cuáles como directrices de control.
*   **Instrucciones de cierre:** Repetir las restricciones al final del prompt para contrarrestar el sesgo de recencia (*recency bias*), donde el modelo tiende a dar más peso a los últimos tokens de la ventana de contexto.

## 4.3 Arquitectura de Guardrails (El Firewall Semántico)
La solución más robusta en entornos de producción es la implementación de una capa de software externa que actúe como **proxy** entre el usuario y el LLM. Herramientas como **NeMo Guardrails** o **Llama Guard** operan bajo este principio:

1.  **Input Guardrails:** Antes de que la consulta llegue al LLM, un modelo de clasificación o un conjunto de reglas analiza la intención del usuario. Si se detecta un intento de inyección o contenido prohibido, la petición se bloquea o se sanitiza.
2.  **Output Guardrails:** Una vez que el LLM genera una respuesta, esta es analizada antes de ser entregada al usuario. Se verifica que no contenga información sensible (fuga de PII), que el tono sea adecuado y que la información sea veraz (mitigación de alucinaciones).

## 4.4 Filtrado Heurístico y Modelos de Clasificación
*   **Filtrado Heurístico:** Uso de listas negras de palabras clave y expresiones regulares (Regex). Aunque es rápido, es ineficaz contra ataques de ofuscación o traducciones.
*   **Clasificadores Basados en Modelos:** Utilizar un segundo LLM, más pequeño y especializado (ej. Llama Guard), cuya única tarea es clasificar si una interacción es segura o no. Este enfoque es altamente efectivo pero introduce **latencia adicional** en el sistema, un factor crítico en la experiencia de usuario.

| Estrategia | Ubicación | Ventajas | Limitaciones |
| :--- | :--- | :--- | :--- |
| **RLHF / Alignment** | Interna (Modelo) | Nativa, sin latencia extra. | Fácil de eludir con Jailbreak. |
| **Delimitadores** | Prompt | Implementación inmediata. | No detiene ataques sofisticados. |
| **Guardrails** | Externa (Proxy) | Control total, configurable. | Introduce latencia y coste. |
| **Llama Guard** | Externa (Modelo) | Alta precisión semántica. | Requiere recursos de GPU extra. |


# 5. Parte Práctica (Prueba de Concepto):
   5.1. Implementación de un agente LLM vulnerable (caso de uso simulado).
   5.2. Ejecución y documentación de ataques de inyección.
   5.3. Implementación de defensas (Guardrails).
   5.4. Evaluación comparativa de la robustez del sistema.
   
# 6. Conclusiones.

# 7. Referencias bibliográficas.
