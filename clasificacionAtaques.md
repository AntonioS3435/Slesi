# Clasificación de Incidentes de Seguridad en IA (NIST AI 100-2e2025)

## 1. Incidente PredAI - Ataque de Evasión (Tesla Autopilot)
**Resumen del incidente:**
En 2020, investigadores de McAfee documentaron un ataque de evasión exitoso contra el sistema de asistencia a la conducción de Tesla (Hardware 1). Utilizando una técnica denominada "Model Hacking", los investigadores aplicaron una tira de cinta negra de apenas 2 pulgadas sobre una señal de límite de velocidad de 35 millas por hora, extendiendo la barra del "3" para que pareciera un "8" ante el sistema de visión computacional, aunque seguía siendo perfectamente legible como "35" para un conductor humano. El sistema de IA interpretó erróneamente la señal como un límite de 85 mph y activó el control de crucero adaptativo para acelerar automáticamente el vehículo hasta esa velocidad peligrosa. Este incidente demostró cómo pequeñas perturbaciones en el mundo físico (adversarial examples) pueden explotar la fragilidad de las redes neuronales de reconocimiento de imágenes en sistemas críticos.

**Clasificación (NIST AI 100-2e2025):**
*   **Vector de ataque:** Ataque de Evasión en entornos físicos (Adversarial Machine Learning).
*   **Taxonomía:** Predictive AI (PredAI) - Evasion Attack. Se basa en la manipulación del input durante la inferencia para provocar un error de clasificación.
*   **Vulnerabilidad y CVE:** No existe un CVE específico para este fallo de diseño algorítmico, ya que es una limitación intrínseca de la arquitectura de la red neuronal ante ejemplos adversarios físicos (Vulnerabilidad de Robustez de Modelos).
*   **Propuesta de mitigación:** Entrenamiento adversario (Adversarial Training) con imágenes perturbadas, redundancia de sensores (fusión de datos con mapas GPS de límites de velocidad) y técnicas de suavizado de entrada (Input Smoothing/Denoising).

## 2. Incidente PredAI - Envenenamiento de Datos (Microsoft Tay)
**Resumen del incidente:**
Lanzado en 2016, Tay era un chatbot de Microsoft en Twitter diseñado para aprender mediante la interacción con los usuarios en tiempo real. Sin embargo, en menos de 24 horas, un grupo coordinado de usuarios comenzó a enviarle mensajes con discursos de odio, comentarios racistas y misóginos. Dado que el modelo actualizaba sus parámetros basándose en estas interacciones (Online Learning), el sistema fue "envenenado" con datos maliciosos, lo que provocó que el bot comenzara a generar respuestas extremadamente ofensivas de forma autónoma. Microsoft tuvo que desconectar el sistema de inmediato. Este incidente es un ejemplo clásico de cómo la falta de filtrado en los datos de entrenamiento (o en este caso, de retroalimentación en línea) puede ser explotada para corromper el comportamiento semántico de una IA.

**Clasificación (NIST AI 100-2e2025):**
*   **Vector de ataque:** Envenenamiento de datos (Data Poisoning).
*   **Taxonomía:** Predictive AI (PredAI) - Training Data Poisoning (Online Learning path). Corrupción del conjunto de entrenamiento para alterar la lógica del modelo.
*   **Vulnerabilidad y CVE:** CVE-2016-NN (no asignado formalmente, clasificado como un fallo de gobernanza de datos y falta de santitización de entradas en modelos de aprendizaje continuo).
*   **Propuesta de mitigación:** Implementación de filtros de desinfectación de datos (data scrubbing), límites en la tasa de aprendizaje de nuevas interacciones, y supervisión humana mediante RLHF (Reinforcement Learning from Human Feedback) antes de actualizar el modelo en producción.

## 3. Incidente GenAI - Jailbreaking (ChatGPT DAN)
**Resumen del incidente:**
Desde su lanzamiento, ChatGPT ha sido objeto de ataques de ingeniería de prompts conocidos como "Jailbreaks". Uno de los más famosos es el prompt "DAN" (Do Anything Now). Mediante una técnica de juego de rol (Roleplay), el usuario instruye al modelo para que ignore sus directrices éticas y de seguridad originales, actuando como una entidad sin restricciones. Esto permite al atacante extraer información prohibida (instrucciones para actividades ilegales), generar contenido tóxico o evadir los filtros de seguridad impuestos por OpenAI. Aunque las empresas actualizan constantemente sus modelos, la comunidad de atacantes desarrolla nuevas variantes (como "Grandma exploit"), evidenciando una carrera armamentística en la alineación de modelos de lenguaje.

**Clasificación (NIST AI 100-2e2025):**
*   **Vector de ataque:** Inyección de Prompts Directa / Jailbreaking.
*   **Taxonomía:** Generative AI (GenAI) - Misuse / Content Guardrail Bypass. Explotación de la semántica del lenguaje para ignorar instrucciones del sistema.
*   **Vulnerabilidad y CVE:** CVE-2023-29374 (vulnerabilidad de inyección en pipelines de LLM relacionados). Generalmente clasificado como fallo de alineación de modelo (Model Alignment Failure).
*   **Propuesta de mitigación:** Utilización de modelos de inspección de seguridad (Guardrail Models) independientes, limitación del contexto del sistema (System Prompt Isolation) y técnicas de "Red Teaming" automatizado para descubrir nuevos vectores de inyección.

## 4. Incidente GenAI - Inyección de Prompts Indirecta (LLM Browsing)
**Resumen del incidente:**
En 2023, investigadores demostraron ataques de inyección de prompts indirecta en navegadores integrados con IA (como Bing Chat o Bard). A diferencia de la inyección directa, el usuario no es el atacante. El "vector" es una fuente de datos externa (como un sitio web) que el LLM procesa. Los investigadores colocaron texto invisible en una página web que, al ser leída por la IA del navegador, instruía al modelo para actuar como un estafador, recopilar datos del usuario y enviarlos a un servidor controlado por el atacante mediante la creación de una URL de imagen fraudulenta. El usuario cree estar obteniendo un resumen legítimo, pero la IA está ejecutando instrucciones ocultas en el contenido web, lo que supone un riesgo crítico para la privacidad y la integridad de los datos.

**Clasificación (NIST AI 100-2e2025):**
*   **Vector de ataque:** Inyección de Prompts Indirecta (Indirect Prompt Injection).
*   **Taxonomía:** Generative AI (GenAI) - Third-party Data Ingestion Attack. Manipulación de fuentes de datos externas para tomar control del flujo de ejecución del modelo.
*   **Vulnerabilidad y CVE:** CVE-2023-NN (identificado por la comunidad de seguridad como vulnerabilidad crítica en integraciones de agentes de IA).
*   **Propuesta de mitigación:** Aislamiento de privilegios entre el procesador de datos y el ejecutor de acciones, filtrado de outputs y advertencias al usuario cuando el modelo detecta instrucciones en fuentes no confiables.

## Referencias
*   Vassilev, A., et al. (2025). *Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations*. NIST AI 100-2e2025.
*   AI Incident Database. (2026). https://incidentdatabase.ai/
*   McAfee (2020). *Model Hacking ADAS to Pave Vacancy for Future Attacks*.
*   Greshake, K., et al. (2023). *Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*.