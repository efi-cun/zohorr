# ==============================================================================
# Catálogo Multitemático de Capacitaciones Interactivas - Cyber-Talent Arena
# ==============================================================================

# --- TEMA 1: ZOHO RECRUIT ---
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

# --- TEMA 2: SEGURIDAD Y SALUD EN EL TRABAJO (SST) ---
SST_CUN_QUESTIONS = [
    {
        "id": "sst-01",
        "order_num": 1,
        "type": "ORDER_SEQUENCE",
        "category": "PLAN DE EMERGENCIAS",
        "title": "🧩 DESAFÍO DE SECUENCIA: Protocolo de Evacuación Segura",
        "question_text": "Ordena cronológicamente los pasos que debes seguir cuando suena la alarma general de evacuación en la sede:",
        "options": [
            {"id": "opt_A", "text": "Suspender labores inmediatamente y asegurar objetos de valor personales"},
            {"id": "opt_B", "text": "Desplazarse en fila por la derecha siguiendo las señales verdes de salida"},
            {"id": "opt_C", "text": "Bajar por las escaleras sin correr y sin usar ascensores bajo ninguna circunstancia"},
            {"id": "opt_D", "text": "Llegar al Punto de Encuentro asignado y reportarse ante el brigadista"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "Ante la alarma se suspenden labores, se sigue la ruta de evacuación por la derecha, se usan exclusivamente escaleras y se permanece en el punto de encuentro hasta el censo del brigadista.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "sst-02",
        "order_num": 2,
        "type": "CHOICE",
        "category": "ERGONOMÍA Y BIENESTAR",
        "title": "⚡ SALUD LABORAL: Frecuencia de Pausas Activas",
        "question_text": "¿Cuál es la recomendación ergonómica de pausas activas durante jornadas de oficina y trabajo en pantallas?",
        "options": [
            {"id": "opt_A", "text": "Realizar pausas de 5 a 10 minutos cada 2 horas de postura continua, con estiramiento y descanso visual."},
            {"id": "opt_B", "text": "Realizar una sola pausa de 1 minuto al final del día laboral."},
            {"id": "opt_C", "text": "No levantarse nunca de la silla para mantener la concentración sin interrupciones."},
            {"id": "opt_D", "text": "Hacer pausas activas únicamente los viernes antes de salir a descansar."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Las pausas activas cada 2 horas previenen trastornos musculoesqueléticos, fatiga visual y mejoran la circulación sanguínea y oxigenación cerebral.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "sst-03",
        "order_num": 3,
        "type": "ORDER_SEQUENCE",
        "category": "GESTIÓN DE ACCIDENTES",
        "title": "🧩 DESAFÍO DE SECUENCIA: Ruta ante un Accidente de Trabajo (AT)",
        "question_text": "Ordena el flujo de atención institucional ante la ocurrencia de un Accidente de Trabajo:",
        "options": [
            {"id": "opt_A", "text": "Prestar primeros auxilios inmediatos por parte de la brigada de emergencias"},
            {"id": "opt_B", "text": "Reportar el suceso al jefe inmediato y al área de Seguridad y Salud en el Trabajo"},
            {"id": "opt_C", "text": "Traslado del trabajador al centro médico asistencial de la red ARL"},
            {"id": "opt_D", "text": "Radicación formal del informe FURAT ante la ARL dentro de las 48 horas"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "Se estabiliza a la persona con primeros auxilios, se notifica a SST, se atiende en la red de la aseguradora de riesgos y se radica el reporte legal (FURAT) en los tiempos de ley.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "sst-04",
        "order_num": 4,
        "type": "SCENARIO",
        "category": "CULTURA DE PREVENCIÓN",
        "title": "🎭 CASO PRÁCTICO: Detección de Condición Insegura",
        "question_text": "Observas que en el pasillo principal hay un cable de alta tensión suelto y el piso tiene agua derramada sin señalizar. ¿Cómo debes actuar?",
        "options": [
            {"id": "opt_A", "text": "Señalizar preventivamente la zona y reportar de inmediato a Mantenimiento y SST mediante la tarjeta de condición insegura."},
            {"id": "opt_B", "text": "Pasar con cuidado saltando el charco sin avisarle a nadie."},
            {"id": "opt_C", "text": "Secar el agua con hojas de papel reciclado y dejar el cable como está."},
            {"id": "opt_D", "text": "Tomar una foto para redes sociales personales sin realizar ningún reporte interno."}
        ],
        "correct_answer": "opt_A",
        "explanation": "El autocuidado y la prevención activa exigen señalizar el peligro para proteger a los demás colaboradores y reportar de inmediato a SST para su corrección técnica inmediata.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "sst-05",
        "order_num": 5,
        "type": "CHOICE",
        "category": "COMITÉS PARITARIOS",
        "title": "⚖️ MARCO LEGAL: ¿Qué es el COPASST y cuál es su misión?",
        "question_text": "¿Cuál es la función principal del Comité Paritario de Seguridad y Salud en el Trabajo (COPASST)?",
        "options": [
            {"id": "opt_A", "text": "Vigilar el cumplimiento de las normas de SST, proponer mejoras en ambientes de trabajo e investigar incidentes laborales."},
            {"id": "opt_B", "text": "Gestionar las solicitudes de préstamos de dinero y nómina de los colaboradores."},
            {"id": "opt_C", "text": "Organizar las fiestas navideñas y eventos recreativos de fin de año."},
            {"id": "opt_D", "text": "Aplicar memorandos y sanciones disciplinarias a los trabajadores."}
        ],
        "correct_answer": "opt_A",
        "explanation": "El COPASST es un organismo paritario (representantes de empresa y trabajadores) encargado de fomentar hábitos seguros, proponer medidas preventivas y participar en la investigación de accidentes.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "sst-06",
        "order_num": 6,
        "type": "ORDER_SEQUENCE",
        "category": "HIGIENE POSTURAL",
        "title": "🧩 DESAFÍO DE SECUENCIA: Levantamiento Manual de Cargas",
        "question_text": "Ordena la técnica biomecánica correcta para levantar un paquete pesado desde el suelo:",
        "options": [
            {"id": "opt_A", "text": "Aproximarse a la carga y separar los pies al ancho de los hombros"},
            {"id": "opt_B", "text": "Flexionar las rodillas manteniendo la espalda recta en todo momento"},
            {"id": "opt_C", "text": "Agarrar firmemente la carga manteniéndola pegada al cuerpo"},
            {"id": "opt_D", "text": "Levantarse haciendo la fuerza con los músculos de las piernas sin doblar la columna"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "La fuerza debe realizarse con las piernas y glúteos, nunca arqueando la espalda, manteniendo la carga lo más pegada al eje central del cuerpo.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "sst-07",
        "order_num": 7,
        "type": "SCENARIO",
        "category": "CONVIVENCIA LABORAL",
        "title": "🎭 CASO PRÁCTICO: Comité de Convivencia Laboral (CCL)",
        "question_text": "Un colaborador experimenta conductas reiteradas de hostigamiento o trato descalificador injustificado por parte de un colega. ¿Cuál es el canal institucional de atención?",
        "options": [
            {"id": "opt_A", "text": "Presentar la queja formal y confidencial ante el Comité de Convivencia Laboral (CCL) para mediación concertada."},
            {"id": "opt_B", "text": "Responder con agresiones verbales en reuniones públicas de equipo."},
            {"id": "opt_C", "text": "Publicar comentarios indirectos en redes sociales personales."},
            {"id": "opt_D", "text": "Ignorar la situación y dejar que el conflicto crezca."}
        ],
        "correct_answer": "opt_A",
        "explanation": "El Comité de Convivencia Laboral tiene como función legal prevenir el acoso laboral, brindar un espacio neutral de mediación y generar compromisos para un ambiente laboral sano y respetuoso.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "sst-08",
        "order_num": 8,
        "type": "CHOICE",
        "category": "CONTROL DE INCENDIOS",
        "title": "🔥 BRIGADAS: Extintor para Equipos Electrónicos",
        "question_text": "¿Qué tipo de extintor debe utilizarse para controlar un fuego incipiente en servidores, tableros o computadores?",
        "options": [
            {"id": "opt_A", "text": "Extintor de Solkaflam / Dióxido de Carbono (CO2) o agente limpio, que no conduce electricidad ni deja residuos destructivos."},
            {"id": "opt_B", "text": "Extintor de agua presurizada corriente."},
            {"id": "opt_C", "text": "Baldes de agua tomados del baño más cercano."},
            {"id": "opt_D", "text": "Soplar fuertemente hacia las llamas."}
        ],
        "correct_answer": "opt_A",
        "explanation": "Los extintores de CO2 o agentes limpios (Solkaflam/Halotrón) son no conductores eléctricos y no dañan los circuitos de cómputo ni dejan polvos corrosivos.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "sst-09",
        "order_num": 9,
        "type": "ORDER_SEQUENCE",
        "category": "INSPECCIÓN DE PUESTO",
        "title": "🧩 DESAFÍO DE SECUENCIA: Ajuste Ergonómico de la Estación de Trabajo",
        "question_text": "Ordena los ajustes ergonómicos al sentarte en tu puesto de trabajo:",
        "options": [
            {"id": "opt_A", "text": "Graduar la altura de la silla hasta que los pies queden apoyados planos en el suelo o apoyapiés"},
            {"id": "opt_B", "text": "Ajustar el espaldar para dar soporte firme a la curva lumbar"},
            {"id": "opt_C", "text": "Posicionar el monitor a la distancia de un brazo y con el borde superior a la altura de los ojos"},
            {"id": "opt_D", "text": "Ubicar teclado y mouse al mismo nivel permitiendo que los antebrazos reposen a 90 grados"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El ajuste parte de los pies y la pelvis, continúa con el soporte lumbar, sigue con la altura visual de la pantalla y culmina con la alineación neutra de muñecas y codos a 90°.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "sst-10",
        "order_num": 10,
        "type": "SPEED_TRIAL",
        "category": "OBLIGACIONES LEGALES",
        "title": "⚡ PRUEBA RELÁMPAGO: Participación en Simulacros",
        "question_text": "¿Es obligación de todos los colaboradores y contratistas participar con total seriedad en los simulacros de evacuación programados?",
        "options": [
            {"id": "opt_A", "text": "VERDADERO: Es un deber legal de autocuidado y preparación para preservar la vida ante emergencias reales."},
            {"id": "opt_B", "text": "FALSO: Los simulacros son opcionales y solo obligan a los brigadistas uniformados."}
        ],
        "correct_answer": "opt_A",
        "explanation": "¡Correcto! Todo trabajador tiene el deber legal y ético de conocer las rutas de escape y participar en los simulacros para responder con calma y eficacia ante una contingencia real.",
        "time_limit_sec": 15,
        "points_base": 1100
    }
]

# --- TEMA 3: INDUCCIÓN & CULTURA INSTITUCIONAL CUN ---
ONBOARDING_CUN_QUESTIONS = [
    {
        "id": "onb-01",
        "order_num": 1,
        "type": "ORDER_SEQUENCE",
        "category": "RUTA DE INTEGRACIÓN",
        "title": "🧩 DESAFÍO DE SECUENCIA: Ruta de Bienvenida para Nuevos Talentos",
        "question_text": "Ordena cronológicamente las fases de la experiencia de inducción de un nuevo colaborador en la CUN:",
        "options": [
            {"id": "opt_A", "text": "Formalización contractual, entrega de credenciales y bienvenida oficial"},
            {"id": "opt_B", "text": "Inducción corporativa: historia, valores, modelo pedagógico y cultura CUN"},
            {"id": "opt_C", "text": "Inducción al puesto de trabajo, procesos del área y entrega de herramientas"},
            {"id": "opt_D", "text": "Seguimiento al periodo de prueba y concertación de metas del rol"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "La ruta inicia con la vinculación y credenciales, continúa con la inmersión cultural institucional, avanza al entrenamiento específico en el puesto y culmina en la concertación de metas de desempeño.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "onb-02",
        "order_num": 2,
        "type": "CHOICE",
        "category": "IDENTIDAD CUN",
        "title": "⚡ CULTURA Y ADN: Pilares Institucionales",
        "question_text": "¿Qué rasgos caracterizan la propuesta de valor y el modelo educativo de la CUN?",
        "options": [
            {"id": "opt_A", "text": "Educación disruptiva, innovación pedagógica, tecnología aplicada y formación accesible por ciclos propedéuticos."},
            {"id": "opt_B", "text": "Metodología memorística tradicional sin plataformas digitales."},
            {"id": "opt_C", "text": "Educación exclusivamente teórica sin conexión con el mundo laboral."},
            {"id": "opt_D", "text": "Clases presenciales rígidas sin posibilidad de interacción virtual."}
        ],
        "correct_answer": "opt_A",
        "explanation": "La CUN se distingue por su enfoque innovador, alegre, flexible y con trayectoria propedéutica, permitiendo a los estudiantes escalar títulos progresivamente.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "onb-03",
        "order_num": 3,
        "type": "ORDER_SEQUENCE",
        "category": "CICLOS PROPEDÉUTICOS",
        "title": "🧩 DESAFÍO DE SECUENCIA: Cadena de Titulación Propedéutica",
        "question_text": "Ordena la escalera formativa por ciclos propedéuticos que brinda la institución a sus estudiantes:",
        "options": [
            {"id": "opt_A", "text": "Ciclo Técnico Profesional (Desarrollo operativo y habilidades prácticas)"},
            {"id": "opt_B", "text": "Ciclo Tecnológico (Gestión táctica, coordinación y análisis)"},
            {"id": "opt_C", "text": "Ciclo Profesional Universitario (Estrategia, diseño y toma de decisiones)"},
            {"id": "opt_D", "text": "Posgrados y Especializaciones (Alta especialización y profundización)"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El modelo propedéutico permite graduarse primero como Técnico Profesional, continuar a Tecnólogo, culminar como Profesional y avanzar a Posgrados.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "onb-04",
        "order_num": 4,
        "type": "SCENARIO",
        "category": "EXPERIENCIA ESTUDIANTIL",
        "title": "🎭 CASO PRÁCTICO: La Filosofía de Servicio 'Gente CUN'",
        "question_text": "Un estudiante de primer semestre se encuentra desorientado en el pasillo buscando su aula virtual. Aunque tú no eres docente, ¿cómo actúas?",
        "options": [
            {"id": "opt_A", "text": "Te detienes, lo saludas con amabilidad, escuchas su consulta y lo orientas con empatía hacia la plataforma o canal de soporte correcto."},
            {"id": "opt_B", "text": "Le respondes que estás ocupado y que busque en un cartel de la pared."},
            {"id": "opt_C", "text": "Le dices que ese trámite no le corresponde a tu área y te marchas."},
            {"id": "opt_D", "text": "Lo ignoras por completo asumiendo que alguien más le responderá."}
        ],
        "correct_answer": "opt_A",
        "explanation": "El ADN de la CUN se basa en la calidez, la empatía y la orientación al estudiante: todos los colaboradores somos embajadores de servicio y facilitadores del éxito académico.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "onb-05",
        "order_num": 5,
        "type": "CHOICE",
        "category": "HERRAMIENTAS INSTITUCIONALES",
        "title": "💻 ECOSISTEMA DIGITAL: Canales de Gestión",
        "question_text": "¿Cuál es la herramienta corporativa principal para gestionar requerimientos internos de tecnología y servicios administrativos?",
        "options": [
            {"id": "opt_A", "text": "La Mesa de Ayuda y portales institucionales de autogestión de solicitudes."},
            {"id": "opt_B", "text": "Grupos informales de mensajería instantánea sin número de radicado."},
            {"id": "opt_C", "text": "Notas de papel adhesivo dejadas en la puerta de la oficina."},
            {"id": "opt_D", "text": "Llamadas personales fuera de los horarios de servicio."}
        ],
        "correct_answer": "opt_A",
        "explanation": "La Mesa de Ayuda permite radicar tickets formales con trazabilidad, tiempos de respuesta (SLA) y seguimiento puntual para resolver necesidades tecnológicas y administrativas.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "onb-06",
        "order_num": 6,
        "type": "ORDER_SEQUENCE",
        "category": "AUTOSERVICIO LABORAL",
        "title": "🧩 DESAFÍO DE SECUENCIA: Solicitud de Vacaciones o Permisos",
        "question_text": "Ordena el procedimiento de solicitud de permisos o vacaciones en el portal de talento:",
        "options": [
            {"id": "opt_A", "text": "Acceder al portal de autoservicio de colaboradores con usuario institucional"},
            {"id": "opt_B", "text": "Seleccionar la fecha de inicio y fin en el módulo de solicitudes"},
            {"id": "opt_C", "text": "Notificación y aprobación automática por parte del líder de área"},
            {"id": "opt_D", "text": "Confirmación del sistema y registro en la programación de nómina"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El proceso se realiza de forma digital en el portal: radicación de fechas, validación del jefe inmediato y confirmación directa con nómina.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "onb-07",
        "order_num": 7,
        "type": "SCENARIO",
        "category": "INNOVACIÓN Y MEJORA",
        "title": "🎭 CASO PRÁCTICO: Espíritu Emprendedor en el Trabajo",
        "question_text": "Detectas que una tarea repetitiva semanal en tu equipo se puede optimizar automatizando una plantilla compartida. ¿Qué deberías hacer?",
        "options": [
            {"id": "opt_A", "text": "Diseñar la propuesta de mejora, validarla con tu equipo y proponer su adopción ágil para ahorrar tiempo."},
            {"id": "opt_B", "text": "Seguir haciendo el proceso manual lento para no cambiar la rutina tradicional."},
            {"id": "opt_C", "text": "Guardarte la idea para que nadie más la aproveche."},
            {"id": "opt_D", "text": "Quejarte informalmente de la cantidad de trabajo sin proponer alternativas."}
        ],
        "correct_answer": "opt_A",
        "explanation": "La CUN promueve la intra-emprendimiento y la cultura 'Hazlo Fácil': cualquier miembro del equipo está invitado a proponer ideas que optimicen procesos y ahorren tiempo valioso.",
        "time_limit_sec": 25,
        "points_base": 1000
    },
    {
        "id": "onb-08",
        "order_num": 8,
        "type": "CHOICE",
        "category": "ÉTICA Y CIBERSEGURIDAD",
        "title": "🔒 SEGURIDAD DE LA INFORMACIÓN: Uso de Credenciales Institucionales",
        "question_text": "¿Cuál es la política correcta respecto a las contraseñas y cuentas corporativas institucionales?",
        "options": [
            {"id": "opt_A", "text": "Son de uso personal, intransferible y confidencial, con autenticación segura y bloqueo al ausentarse del equipo."},
            {"id": "opt_B", "text": "Anotar la contraseña en un papel pegado al monitor de la oficina."},
            {"id": "opt_C", "text": "Compartir la contraseña con amigos y compañeros de trabajo para agilizar tareas."},
            {"id": "opt_D", "text": "Utilizar la misma contraseña sencilla para todas las plataformas sin cambiarla nunca."}
        ],
        "correct_answer": "opt_A",
        "explanation": "La confidencialidad y el resguardo de la información institucional y de los datos de nuestros estudiantes (Habeas Data) es una responsabilidad estricta de cada colaborador.",
        "time_limit_sec": 20,
        "points_base": 1000
    },
    {
        "id": "onb-09",
        "order_num": 9,
        "type": "ORDER_SEQUENCE",
        "category": "DESARROLLO DE TALENTO",
        "title": "🧩 DESAFÍO DE SECUENCIA: Ciclo de Gestión del Desempeño",
        "question_text": "Ordena el ciclo de evaluación y crecimiento profesional del colaborador:",
        "options": [
            {"id": "opt_A", "text": "Acuerdo de objetivos de desempeño y competencias clave al inicio del ciclo"},
            {"id": "opt_B", "text": "Sesiones periódicas de seguimiento y retroalimentación constructiva (Feedback 1 a 1)"},
            {"id": "opt_C", "text": "Evaluación formal de cumplimiento de metas y autoevaluación"},
            {"id": "opt_D", "text": "Construcción del plan individual de desarrollo y formación en la Universidad Corporativa"}
        ],
        "correct_order": ["opt_A", "opt_B", "opt_C", "opt_D"],
        "explanation": "El ciclo parte del alineamiento de expectativas, continúa con el acompañamiento permanente del líder, culmina en el balance formal de resultados y proyecta el plan de aprendizaje.",
        "time_limit_sec": 30,
        "points_base": 1200
    },
    {
        "id": "onb-10",
        "order_num": 10,
        "type": "SPEED_TRIAL",
        "category": "BENEFICIOS Y BIENESTAR",
        "title": "⚡ PRUEBA RELÁMPAGO: Programas de Bienestar y Formación",
        "question_text": "¿Ofrece la institución convenios, programas de bienestar integral y oportunidades de descuento educativo para colaboradores y sus familias?",
        "options": [
            {"id": "opt_A", "text": "VERDADERO: Existen planes de formación continua, convenios de bienestar, salud y auxilios educativos."},
            {"id": "opt_B", "text": "FALSO: La institución no contempla beneficios de bienestar ni crecimiento para colaboradores."}
        ],
        "correct_answer": "opt_A",
        "explanation": "¡Totalmente verdadero! Bienestar y Gestión Humana gestionan alianzas, becas corporativas, actividades culturales y deportivas para el bienestar integral de la comunidad laboral.",
        "time_limit_sec": 15,
        "points_base": 1100
    }
]

# --- CATÁLOGO CENTRALIZADO DE TEMAS ---
TRAINING_TOPICS = {
    "zoho_recruit": {
        "id": "zoho_recruit",
        "name": "Zoho Recruit: Cyber-Talent Arena",
        "badge": "ZOHO RECRUIT",
        "description": "Capacitación práctica en el ciclo completo de selección, vacantes, resume parsing y contratación.",
        "default_pin": "ZR2026",
        "questions": ZOHO_RECRUIT_QUESTIONS
    },
    "sst_cun": {
        "id": "sst_cun",
        "name": "Seguridad y Salud en el Trabajo (SST)",
        "badge": "SST CORPORATIVO",
        "description": "Protocolos de emergencia, ergonomía, prevención de riesgos, COPASST y brigadas.",
        "default_pin": "SST2026",
        "questions": SST_CUN_QUESTIONS
    },
    "onboarding_cun": {
        "id": "onboarding_cun",
        "name": "Inducción & Cultura Institucional CUN",
        "badge": "CULTURA & ADN",
        "description": "Identidad, ciclos propedéuticos, herramientas de autogestión y excelencia en servicio.",
        "default_pin": "CUN2026",
        "questions": ONBOARDING_CUN_QUESTIONS
    }
}

def get_topic(topic_id: str = "zoho_recruit"):
    """Returns topic data from database if available, otherwise falls back to memory."""
    topic_id = (topic_id or "zoho_recruit").lower().strip()
    try:
        from app.database import get_topic_from_db
        db_topic = get_topic_from_db(topic_id)
        if db_topic and db_topic.get("questions"):
            return db_topic
    except Exception:
        pass
    return TRAINING_TOPICS.get(topic_id, TRAINING_TOPICS["zoho_recruit"])

def get_all_topics():
    """Returns summaries of all available topics from DB or in-memory catalog."""
    try:
        from app.database import get_all_topics_from_db
        db_topics = get_all_topics_from_db()
        if db_topics and len(db_topics) > 0:
            return db_topics
    except Exception:
        pass

    topics_list = []
    for tid, tdata in TRAINING_TOPICS.items():
        topics_list.append({
            "id": tdata["id"],
            "name": tdata["name"],
            "badge": tdata["badge"],
            "description": tdata["description"],
            "default_pin": tdata["default_pin"],
            "question_count": len(tdata["questions"])
        })
    return topics_list

def get_all_questions():
    """Returns flat list of questions from all topics for database syncing."""
    all_q = []
    for tdata in TRAINING_TOPICS.values():
        all_q.extend(tdata["questions"])
    return all_q
