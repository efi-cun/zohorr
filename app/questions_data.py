# Banco Oficial de Preguntas Interactivas - Zoho Recruit Cyber-Arena

ZOHO_RECRUIT_QUESTIONS = [
    {
        "id": "zr-01",
        "order_num": 1,
        "type": "ORDER_SEQUENCE",
        "category": "CANDIDATE PIPELINE",
        "title": "🧩 DESAFÍO DE SECUENCIA: Pipeline de Candidatos",
        "question_text": "Ordena cronológicamente las etapas estándar por las que pasa un candidato en Zoho Recruit desde que postula hasta que ingresa a la empresa:",
        "options": [
            {"id": "opt_A", "text": "Asociado a Vacante (Screening / Preselección)"},
            {"id": "opt_B", "text": "Entrevista Técnica & Evaluación de Rúbrica"},
            {"id": "opt_C", "text": "Emisión de Carta de Oferta (Offer Letter)"},
            {"id": "opt_D", "text": "Contratado (Hired) & Traspaso a Zoho People"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El pipeline estándar en Zoho Recruit inicia con la preselección (Screening), avanza a Entrevista (Interview), formalización con Carta de Oferta (Offer) y finaliza con la Contratación (Hired) y sincronización a Zoho People.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-02",
        "order_num": 2,
        "type": "CHOICE",
        "category": "ARQUITECTURA DE RECRUIT",
        "title": "⚡ DECISIÓN TÁCTICA: Modelos de Negocio en Zoho Recruit",
        "question_text": "¿Cuál es la principal diferencia entre configurar Zoho Recruit en modo 'Corporate HR' vs 'Staffing Agency'?",
        "options": [
            {"id": "opt_A", "text": "Corporate HR gestiona vacantes internas de una empresa; Staffing Agency gestiona Clientes, Cuentas y Contactos externos."},
            {"id": "opt_B", "text": "Staffing Agency no permite sincronización con portales de empleo como LinkedIn ni Indeed."},
            {"id": "opt_C", "text": "Corporate HR no tiene módulo de candidatos ni de cartas de oferta."},
            {"id": "opt_D", "text": "Ambas configuraciones son idénticas y solo cambia el color del logo."}
        ],
        "correct_answer": "opt_A",
        "explanation": "El modo Staffing Agency añade los módulos de 'Clientes' (Clients) y 'Contactos' para facturar y reclutar a terceros, mientras que Corporate HR se enfoca en 'Departamentos' internos de la propia organización.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "zr-03",
        "order_num": 3,
        "type": "ORDER_SEQUENCE",
        "category": "PUBLICACIÓN DE VACANTES",
        "title": "🧩 DESAFÍO DE SECUENCIA: Lanzamiento de Vacante (Job Opening)",
        "question_text": "Ordena el flujo correcto para aperturar y difundir una nueva vacante de talento en Zoho Recruit:",
        "options": [
            {"id": "opt_A", "text": "Crear requisición de empleo con descripción, habilidades y salario"},
            {"id": "opt_B", "text": "Aprobación interna de la vacante mediante Blueprint o Workflow"},
            {"id": "opt_C", "text": "Publicación multicanal en Career Site, LinkedIn e Indeed"},
            {"id": "opt_D", "text": "Recepción automática y parsing de hojas de vida (Resume Inbox)"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "Primero se formula la vacante, luego se aprueba internamente (presupuesto/perfil), se difunde en bolsas de empleo y el career site, y finalmente el Resume Parser procesa los CVs que van ingresando.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-04",
        "order_num": 4,
        "type": "SCENARIO",
        "category": "GESTIÓN DE TALENTO",
        "title": "🎭 CASO PRÁCTICO: El Dilema del Candidato Estrella",
        "question_text": "Llega un candidato con perfil sobresaliente para un cargo Senior, pero la vacante actual ya fue cerrada ayer. ¿Cuál es la mejor práctica recomendada en Zoho Recruit?",
        "options": [
            {"id": "opt_A", "text": "Asignarlo a un 'Talent Pool' (Bolsa de Talentos) especializado con etiquetas de competencias para futuras vacantes."},
            {"id": "opt_B", "text": "Eliminar su registro para no generar duplicados en la base de datos."},
            {"id": "opt_C", "text": "Cambiar el estado de la vacante cerrada a 'Borrador' sin avisar al equipo."},
            {"id": "opt_D", "text": "Descargar el CV en PDF a una carpeta local del computador y borrarlo de Zoho."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Los 'Talent Pools' permiten categorizar talentos pre-cualificados sin necesidad de vincularlos a una vacante activa, manteniéndolos listos para contacto inmediato cuando surja una necesidad.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "zr-05",
        "order_num": 5,
        "type": "CHOICE",
        "category": "INTELIGENCIA ARTIFICIAL",
        "title": "🤖 TECNOLOGÍA ZIA: AI Candidate Matching",
        "question_text": "¿Cómo calcula Zoho Recruit (Zia) el porcentaje de compatibilidad (Matching Score) de un postulante?",
        "options": [
            {"id": "opt_A", "text": "Compara las habilidades, experiencia laboral y nivel educativo del CV contra los requisitos de la vacante."},
            {"id": "opt_B", "text": "Basándose únicamente en la cercanía geográfica por código postal."},
            {"id": "opt_C", "text": "Por orden de llegada del currículum al correo electrónico."},
            {"id": "opt_D", "text": "Generando un número aleatorio entre 50% y 100%."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Zia AI analiza mediante NLP las palabras clave de destrezas, certificaciones, años de experiencia y educación extraídas del CV frente a la ficha técnica del Job Opening.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "zr-06",
        "order_num": 6,
        "type": "ORDER_SEQUENCE",
        "category": "INTEGRACIÓN & ONBOARDING",
        "title": "🧩 DESAFÍO DE SECUENCIA: De Candidato a Empleado (Onboarding)",
        "question_text": "Ordena los pasos para completar la contratación formal y el traspaso a talento humano en el ecosistema Zoho:",
        "options": [
            {"id": "opt_A", "text": "Generar Carta de Oferta con campos dinámicos (Merge Tags)"},
            {"id": "opt_B", "text": "Firma electrónica vinculante del candidato mediante Zoho Sign"},
            {"id": "opt_C", "text": "Cambiar estado del candidato a 'Hired / Contratado'"},
            {"id": "opt_D", "text": "Ejecutar acción 'Convert to Employee' para crear su ficha en Zoho People"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El proceso formaliza primero la oferta digital, obtiene la firma con validez jurídica a través de Zoho Sign, actualiza el estado a Hired y finalmente sincroniza los datos hacia Zoho People para la bienvenida y nómina.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-07",
        "order_num": 7,
        "type": "SCENARIO",
        "category": "CONTROL DE PROCESOS",
        "title": "🎭 CASO PRÁCTICO: Control de Calidad con Blueprints",
        "question_text": "La gerencia detectó que algunos reclutadores enviaban cartas de oferta sin haber registrado las notas de la entrevista técnica. ¿Cómo solucionas esto de forma definitiva en Zoho Recruit?",
        "options": [
            {"id": "opt_A", "text": "Configurar un Blueprint que haga obligatorio adjuntar la evaluación de entrevista antes de habilitar la transición a 'Oferta'."},
            {"id": "opt_B", "text": "Enviar un correo a todos pidiendo por favor que no lo vuelvan a hacer."},
            {"id": "opt_C", "text": "Bloquear el acceso a Zoho Recruit a los reclutadores los fines de semana."},
            {"id": "opt_D", "text": "Desactivar el módulo de entrevistas de la plataforma."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Los Blueprints en Zoho Recruit fuerzan el cumplimiento de la metodología corporativa: un usuario no puede pasar a la siguiente fase sin completar campos y criterios obligatorios.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "zr-08",
        "order_num": 8,
        "type": "CHOICE",
        "category": "AUTOMATIZACIÓN & DELUGE",
        "title": "⚡ AUTOMATIZACIÓN AVANZADA: Deluge en Zoho Recruit",
        "question_text": "¿Qué función de Deluge te permite consultar información de una vacante directamente desde código?",
        "options": [
            {"id": "opt_A", "text": "zoho.recruit.getRecordById(\"JobOpenings\", vacante_id);"},
            {"id": "opt_B", "text": "database.select(\"vacantes\").where(id);"},
            {"id": "opt_C", "text": "recruit.fetchCandidateByName(\"Juan\");"},
            {"id": "opt_D", "text": "zoho.crm.searchLead();"}
        ],
        "correct_answer": "opt_A",
        "explanation": "El namespace 'zoho.recruit' en Deluge provee funciones nativas de integración como getRecordById, getRecords, updateRecord y searchRecordsByPDC.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "zr-09",
        "order_num": 9,
        "type": "ORDER_SEQUENCE",
        "category": "EVALUACIONES & ENTREVISTAS",
        "title": "🧩 DESAFÍO DE SECUENCIA: Ronda de Evaluación Técnica",
        "question_text": "Ordena el procedimiento para coordinar una evaluación técnica colaborativa con el líder de área:",
        "options": [
            {"id": "opt_A", "text": "Asignar plantilla de evaluación (Assessment Sheet) con criterios técnicos"},
            {"id": "opt_B", "text": "Agendar entrevista sincronizada con el calendario de Zoho Mail/Google"},
            {"id": "opt_C", "text": "El evaluador califica las competencias en la hoja de evaluación en vivo"},
            {"id": "opt_D", "text": "Consolidación automática del promedio de puntuación en el perfil del candidato"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "La estructura de assessments en Zoho Recruit permite estandarizar la evaluación objetiva vinculándola a la agenda de entrevistas y calculando un score consolidado del postulante.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-10",
        "order_num": 10,
        "type": "SPEED_TRIAL",
        "category": "PORTALES & PRIVACIDAD",
        "title": "⚡ PRUEBA RELÁMPAGO: Portales de Candidatos y GDPR",
        "question_text": "¿Pueden los candidatos acceder a un portal web autoservicio de Zoho Recruit para actualizar su CV y ejercer derechos de privacidad sobre sus datos?",
        "options": [
            {"id": "opt_A", "text": "VERDADERO: Zoho Recruit ofrece un Portal de Candidatos dedicado con gestión de consentimiento y actualización de perfil."},
            {"id": "opt_B", "text": "FALSO: Toda modificación requiere obligatoriamente que un reclutador la edite a mano."}
        ],
        "correct_answer": "opt_A",
        "explanation": "¡Correcto! El Candidate Portal y las funciones de cumplimiento GDPR permiten al postulante revisar sus postulaciones, actualizar su hoja de vida y solicitar la revocación o eliminación de sus datos.",
        "time_limit_sec": 15,
        "points_base": 1100
    }
]
