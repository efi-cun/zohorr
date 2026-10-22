# Banco Oficial de Preguntas Interactivas - Zoho Recruit Cyber-Arena
# 100% Enfocado en la Operación y Funcionamiento Práctico de Zoho Recruit

ZOHO_RECRUIT_QUESTIONS = [
    {
        "id": "zr-01",
        "order_num": 1,
        "type": "ORDER_SEQUENCE",
        "category": "FLUJO DEL CANDIDATO",
        "title": "🧩 DESAFÍO DE SECUENCIA: Pipeline de Candidatos en Zoho Recruit",
        "question_text": "Ordena cronológicamente las etapas por las que avanza un postulante en Zoho Recruit desde que aplica hasta su ingreso a la organización:",
        "options": [
            {"id": "opt_A", "text": "Asociado a Vacante (Screening / Preselección)"},
            {"id": "opt_B", "text": "Entrevista Técnica & Evaluación de Rúbrica"},
            {"id": "opt_C", "text": "Emisión y Aprobación de Carta de Oferta (Offer Letter)"},
            {"id": "opt_D", "text": "Contratado (Hired) & Traspaso a Zoho People"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El pipeline estándar en Zoho Recruit inicia con la preselección (Screening), avanza a Entrevista (Interview) con rúbrica, formalización con Carta de Oferta (Offer Letter) y finaliza con la Contratación (Hired) y sincronización a Zoho People.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-02",
        "order_num": 2,
        "type": "CHOICE",
        "category": "DIFUSIÓN DE VACANTES",
        "title": "⚡ OPERACIÓN DE RECLUTAMIENTO: Difusión Multicanal de Ofertas",
        "question_text": "Cuando un reclutador crea una vacante ('Job Opening') en Zoho Recruit y desea difundirla masivamente, ¿cómo opera la plataforma?",
        "options": [
            {"id": "opt_A", "text": "Permite publicarla simultáneamente en LinkedIn, Indeed, el sitio web de empleo (Career Site) y redes con un solo clic."},
            {"id": "opt_B", "text": "Exige entrar manualmente portal por portal y copiar/pegar la descripción cada vez."},
            {"id": "opt_C", "text": "Solo permite enviar correos individuales a candidatos previamente registrados en la base de datos."},
            {"id": "opt_D", "text": "Requiere exportar la vacante en PDF y subirla a servidores externos por protocolo FTP."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Zoho Recruit integra la publicación multicanal: desde la sección 'Job Boards' de la vacante, se difunde en bolsas de empleo aliadas y en el Career Site corporativo en un solo paso centralizado.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "zr-03",
        "order_num": 3,
        "type": "ORDER_SEQUENCE",
        "category": "GESTIÓN DE VACANTES",
        "title": "🧩 DESAFÍO DE SECUENCIA: Ciclo de Vida de una Vacante (Job Opening)",
        "question_text": "Ordena el flujo operativo para aperturar, difundir y comenzar a recibir postulantes en Zoho Recruit:",
        "options": [
            {"id": "opt_A", "text": "Creación de la requisición con descripción del cargo, competencias y presupuesto"},
            {"id": "opt_B", "text": "Aprobación interna de la vacante mediante flujo de validación"},
            {"id": "opt_C", "text": "Publicación multicanal en Career Site y bolsas de empleo"},
            {"id": "opt_D", "text": "Recepción automática y extracción de CVs en el Resume Inbox"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El ciclo operativo inicia con el levantamiento del perfil del cargo, su aprobación interna (presupuesto y perfil), la publicación multicanal y la posterior captura y lectura automática de CVs.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-04",
        "order_num": 4,
        "type": "SCENARIO",
        "category": "BOLSA DE TALENTOS",
        "title": "🎭 CASO PRÁCTICO: Gestión de Candidatos en 'Talent Pools'",
        "question_text": "Un candidato tiene un perfil brillante durante la evaluación, pero la vacante actual ya completó sus cupos. En el funcionamiento de Zoho Recruit, ¿cuál es la mejor práctica recomendada?",
        "options": [
            {"id": "opt_A", "text": "Asignarlo a un 'Talent Pool' (Bolsa de Talentos) con etiquetas de competencias para futuras convocatorias sin perder su trazabilidad."},
            {"id": "opt_B", "text": "Eliminar su ficha de la plataforma para no generar registros duplicados."},
            {"id": "opt_C", "text": "Modificar el estado de la vacante cerrada a 'Borrador' sin notificar al equipo."},
            {"id": "opt_D", "text": "Descargar el CV a una carpeta local del computador y borrarlo del sistema."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Los 'Talent Pools' permiten categorizar talentos pre-cualificados por especialidad o área, teniéndolos disponibles para asociarlos a futuras vacantes con un solo clic.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "zr-05",
        "order_num": 5,
        "type": "CHOICE",
        "category": "PROCESAMIENTO DE CVS",
        "title": "📄 OPERACIÓN EFICIENTE: Resume Parser (Extractor de CVs)",
        "question_text": "¿Qué hace automáticamente el 'Resume Parser' cuando se sube o llega una hoja de vida en PDF o Word a Zoho Recruit?",
        "options": [
            {"id": "opt_A", "text": "Lee el documento y extrae automáticamente datos de contacto, experiencia, formación y habilidades, creando la ficha sin digitación manual."},
            {"id": "opt_B", "text": "Convierte la hoja de vida en imagen estática sin permitir edición ni búsqueda de palabras clave."},
            {"id": "opt_C", "text": "Envía automáticamente una oferta de contratación formal sin validación del reclutador."},
            {"id": "opt_D", "text": "Bloquea al candidato en la base de datos hasta que confirme por llamada telefónica."}
        ],
        "correct_answer": "opt_A",
        "explanation": "El Resume Parser de Zoho Recruit procesa de inmediato los documentos adjuntos (PDF, DOCX) y puebla los campos clave del módulo de Candidatos, ahorrando tiempo operativo de digitación.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "zr-06",
        "order_num": 6,
        "type": "ORDER_SEQUENCE",
        "category": "CONTRATACIÓN Y TRASPASO",
        "title": "🧩 DESAFÍO DE SECUENCIA: Formalización de Contratación (Onboarding)",
        "question_text": "Ordena los pasos en Zoho Recruit para cerrar con éxito la vinculación y traspasar el candidato a Recursos Humanos / Nómina:",
        "options": [
            {"id": "opt_A", "text": "Generar la Carta de Oferta (Offer Letter) usando plantillas con campos combinados"},
            {"id": "opt_B", "text": "Enviar a firma electrónica digital con validez jurídica mediante Zoho Sign"},
            {"id": "opt_C", "text": "Actualizar el estado del candidato a 'Contratado' (Hired) en la vacante"},
            {"id": "opt_D", "text": "Ejecutar la acción 'Convert to Employee' para crear su ficha en Zoho People"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "Se genera la oferta digital formal, se obtiene la firma electrónica con Zoho Sign, se actualiza el estado a Hired y se convierte en empleado sincronizando sus datos hacia Zoho People.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-07",
        "order_num": 7,
        "type": "SCENARIO",
        "category": "BLUEPRINTS Y PROCESOS",
        "title": "🎭 CASO PRÁCTICO: Estandarización de Procesos con Blueprints",
        "question_text": "La coordinación de selección exige que ningún reclutador pueda emitir una Carta de Oferta sin antes registrar las notas de la entrevista y validar referencias. ¿Cómo se garantiza esto en Zoho Recruit?",
        "options": [
            {"id": "opt_A", "text": "Configurando un 'Blueprint' que bloquee el cambio de etapa y haga obligatorios los campos de entrevista y referencias antes de habilitar 'Oferta'."},
            {"id": "opt_B", "text": "Enviando un correo recordatorio diario a los reclutadores para pedirles que no se salten pasos."},
            {"id": "opt_C", "text": "Bloqueando el acceso a Zoho Recruit a los reclutadores después del mediodía."},
            {"id": "opt_D", "text": "Desactivando permanentemente el módulo de cartas de oferta."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Los Blueprints en Zoho Recruit fuerzan el cumplimiento de la metodología corporativa: un usuario no puede transicionar a la siguiente fase sin completar campos y criterios obligatorios.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "zr-08",
        "order_num": 8,
        "type": "CHOICE",
        "category": "PRE-SELECCIÓN Y FILTROS",
        "title": "🎯 FILTRO INTELIGENTE: Preguntas Pre-screening en Vacantes",
        "question_text": "¿Cuál es la función operativa principal de configurar 'Pre-screening Questions' (Preguntas de Preselección) en el formulario de una vacante?",
        "options": [
            {"id": "opt_A", "text": "Puntuar y filtrar automáticamente a los postulantes según requisitos indispensables (ej. nivel de idioma, aspiración salarial o disponibilidad)."},
            {"id": "opt_B", "text": "Generar automáticamente la nómina mensual del candidato antes de ser evaluado."},
            {"id": "opt_C", "text": "Publicar la vacante en las redes sociales personales del postulante."},
            {"id": "opt_D", "text": "Desactivar la recepción de postulaciones para cerrar la oferta inmediatamente."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Las preguntas de preselección (Pre-screening) permiten calificar y descartar automáticamente a candidatos que no cumplen los requisitos indispensables, optimizando el tiempo del equipo de selección.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "zr-09",
        "order_num": 9,
        "type": "ORDER_SEQUENCE",
        "category": "EVALUACIONES Y ENTREVISTAS",
        "title": "🧩 DESAFÍO DE SECUENCIA: Coordinación y Calificación de Entrevistas",
        "question_text": "Ordena el procedimiento operativo para llevar a cabo una entrevista técnica con hoja de evaluación en Zoho Recruit:",
        "options": [
            {"id": "opt_A", "text": "Asignar la plantilla de evaluación técnica (Assessment Sheet) a la vacante"},
            {"id": "opt_B", "text": "Agendar la entrevista sincronizada con el calendario de Google / Outlook / Zoho"},
            {"id": "opt_C", "text": "El entrevistador califica las competencias en vivo en la hoja de evaluación"},
            {"id": "opt_D", "text": "Consolidación automática del promedio de puntuación en el perfil del candidato"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "La estructura de Assessments en Zoho Recruit permite estandarizar la evaluación objetiva vinculándola a la agenda de entrevistas y calculando una calificación consolidada del postulante.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "zr-10",
        "order_num": 10,
        "type": "SPEED_TRIAL",
        "category": "PORTAL DE CANDIDATOS",
        "title": "⚡ PRUEBA RELÁMPAGO: Autoservicio en el Candidate Portal",
        "question_text": "¿Permite Zoho Recruit que los postulantes consulten el estado de su proceso en vivo y actualicen sus documentos a través de un portal de autoservicio web?",
        "options": [
            {"id": "opt_A", "text": "VERDADERO: Cuenta con un Portal de Candidatos dedicado donde el postulante hace seguimiento a sus vacantes y carga soportes."},
            {"id": "opt_B", "text": "FALSO: Los postulantes no tienen acceso web y todo debe actualizarse llamando directamente al reclutador."}
        ],
        "correct_answer": "opt_A",
        "explanation": "¡Correcto! El Candidate Portal de Zoho Recruit ofrece autogestión para los postulantes: pueden consultar el estado de sus postulaciones, adjuntar documentación y actualizar sus datos en cualquier momento.",
        "time_limit_sec": 15,
        "points_base": 1100
    }
]
