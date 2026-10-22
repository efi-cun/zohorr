# 🚀 Zoho Recruit: Cyber-Talent Arena (CUN 2026)

Plataforma interactiva, tecnológica y futurista en tiempo real estilo **Kahoot Cyberpunk** para capacitaciones y evaluación dinámica de conocimientos sobre **Zoho Recruit**.

Diseñada para proyección en pantalla compartida (Google Meet / Teams / Proyector) con interacción simultánea de participantes desde smartphones o computadores personales, integrando persistencia en vivo con **Supabase** (PostgreSQL).

---

## 🌟 Características Principales

1. **Estética Sci-Fi & Cyberpunk de Alto Impacto:**
   - Interfaz espacial oscura con neones holográficos (Cyan, Magenta, Ámbar, Esmeralda).
   - Efectos de sonido cibernéticos sintetizados nativamente en el navegador (**Web Audio API**) sin necesidad de descargar archivos de audio externos.
   - Animaciones táctiles, radares de jugadores y podio 3D con lluvia de confeti.

2. **Mecánicas de Juego Variadas y Muy Entretenidas:**
   - 🧩 **Modo ORDENAR (Puzzles de Secuencia):** Arrastra o pulsa tarjetas para ordenar cronológicamente las fases del pipeline de contratación, publicación de vacantes y ciclo de onboarding.
   - ⚡ **Ronda Relámpago (Speed Trials):** Decisiones instantáneas con bonificación de velocidad.
   - 🎭 **Casos Prácticos & Dilemas de Reclutador:** Simulación de escenarios reales (Gestión de Talent Pools, Bloqueo de Blueprints, Matching Zia AI).
   - 🔥 **Sistema de Combos y Rachas:** Multiplicador progresivo de puntos al mantener respuestas correctas consecutivas.

3. **Registro de Asistentes & Trazabilidad Total:**
   - Los participantes se conectan escaneando el **Código QR** o ingresando el PIN.
   - Registran sus datos oficiales: **Nombre Completo, Correo Institucional/Personal, Cargo/Área, Nickname de batalla y Avatar Holográfico**.

4. **Integración Directa con Supabase:**
   - Base de datos limpia con 4 tablas relacionales:
     - `recruit_game_sessions`: Sesiones de capacitación y estado.
     - `recruit_participants`: Asistentes registrados, puntaje, aciertos y puesto final.
     - `recruit_questions`: Banco oficial de 10 preguntas y desafíos de Zoho Recruit.
     - `recruit_answers`: Trazabilidad por participante, tiempo de respuesta en milisegundos y puntos.

5. **Reportes y Certificación:**
   - Botón directo para descargar en 1 clic el reporte consolidado de asistentes y calificaciones en formato **CSV compatible con Microsoft Excel**.

---

## 🛠️ Requisitos e Instalación

La aplicación funciona nativamente con **Python 3.12+** sin requerir Node.js ni compiladores adicionales.

### 1. Instalar dependencias
```powershell
python -m pip install -r requirements.txt
```

### 2. Iniciar la Cyber-Arena
```powershell
python run.py
```

Al ejecutarse, el sistema:
1. Verificará y sincronizará las tablas en Supabase.
2. Detectará automáticamente la dirección IP local de tu computador (ej. `192.168.1.15`).
3. Abrirá automáticamente la consola del Host en tu navegador predeterminado.
4. Mostrará en pantalla el **Código QR** y el PIN de sala.

---

## 🌐 URLs de Acceso

- **🖥️ Pantalla del Instructor / Host (Proyector):**
  `http://localhost:8000/host`
- **📱 Pantalla de Jugadores (Móviles / PC):**
  `http://localhost:8000/` (o la IP local detectada para teléfonos en la misma red Wi-Fi).

---

## 🧪 Pruebas Automatizadas

Para validar la lógica de ordenamiento, conexión con Supabase y endpoints de la API:
```powershell
python -m unittest discover tests
```
