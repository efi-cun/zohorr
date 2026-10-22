import os
import socket
import json
import csv
import io
import secrets
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import (
    init_db, 
    get_session_export_rows,
    authenticate_user,
    get_user_by_id,
    get_all_users,
    create_user,
    update_user_status,
    delete_user,
    get_all_topics_from_db,
    get_topic_from_db,
    save_topic,
    delete_topic,
    toggle_topic_visibility,
    get_questions_by_topic,
    save_question,
    delete_question,
    get_sessions_history,
    get_all_participants,
    get_participant_detail_with_answers,
    get_analytics_dashboard_data,
    get_all_participants_export_rows
)
from app.game_manager import game_manager
from app.config import HOST, PORT

# In-memory active auth tokens: token -> user_dict
AUTH_SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Resolves authenticated user from Bearer header or cookie."""
    token = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif "x-auth-token" in request.headers:
        token = request.headers.get("x-auth-token")
    elif "auth_token" in request.cookies:
        token = request.cookies.get("auth_token")

    if token and token in AUTH_SESSIONS:
        return AUTH_SESSIONS[token]
    return None

def require_auth(request: Request, require_admin: bool = False) -> Dict[str, Any]:
    """Helper that raises 401/403 if unauthenticated or lacks permissions."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Sesión no válida o expirada. Por favor inicia sesión.")
    if require_admin and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Permiso denegado. Se requiere rol de Administrador.")
    return user

app = FastAPI(title="Zoho Recruit: Cyber-Talent Arena")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Ensure static dirs exist
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
async def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"Warning: DB startup check: {e}")

def get_local_ip():
    """Detects local LAN IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/host", response_class=HTMLResponse)
async def serve_host():
    host_file = STATIC_DIR / "host.html"
    return HTMLResponse(content=host_file.read_text(encoding="utf-8"))

@app.get("/play", response_class=HTMLResponse)
async def serve_play():
    player_file = STATIC_DIR / "player.html"
    return HTMLResponse(content=player_file.read_text(encoding="utf-8"))

@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    login_file = STATIC_DIR / "login.html"
    if not login_file.exists():
        return HTMLResponse("<h2>Login view loading...</h2>")
    return HTMLResponse(content=login_file.read_text(encoding="utf-8"))

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin():
    admin_file = STATIC_DIR / "admin.html"
    if not admin_file.exists():
        return HTMLResponse("<h2>Admin Dashboard loading...</h2>")
    return HTMLResponse(content=admin_file.read_text(encoding="utf-8"))

@app.get("/dashboard")
async def redirect_dashboard():
    return RedirectResponse(url="/admin")

# --- API Endpoints ---

class RegisterRequest(BaseModel):
    room_code: str
    full_name: str
    email: str
    role_or_area: str
    nickname: str
    avatar: str = "cyber_scout"

@app.post("/api/register")
async def register_player_endpoint(req: RegisterRequest):
    room_code = req.room_code.upper().strip()
    if not room_code:
        raise HTTPException(status_code=400, detail="El código de sala es requerido.")
    if not req.full_name or not req.email or not req.nickname:
        raise HTTPException(status_code=400, detail="Por favor completa todos los campos obligatorios.")

    player = await game_manager.register_player(
        room_code=room_code,
        full_name=req.full_name.strip(),
        email=req.email.strip(),
        role_or_area=req.role_or_area.strip(),
        nickname=req.nickname.strip(),
        avatar=req.avatar
    )
    return {
        "success": True,
        "player_id": player["id"],
        "room_code": room_code,
        "player": player
    }

@app.get("/api/network-ip")
async def network_ip_endpoint(request: Request):
    public_url = os.getenv("PUBLIC_WEB_URL") or os.getenv("RENDER_EXTERNAL_URL")
    
    # Auto-detect public host from request headers if accessed through reverse proxy (e.g. Render / Cloudflare)
    if not public_url:
        forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host")
        if forwarded_host and ("onrender.com" in forwarded_host or "trycloudflare.com" in forwarded_host):
            forwarded_proto = request.headers.get("x-forwarded-proto", "https")
            public_url = f"{forwarded_proto}://{forwarded_host}"

    # Default Render domain fallback if running on Render environment (default port 10000 or RENDER flag)
    if not public_url and (os.getenv("RENDER") or PORT == 10000 or os.getenv("PORT") == "10000"):
        public_url = "https://zoho-recruit-arena.onrender.com"

    if public_url:
        return {
            "ip": "Web Public",
            "port": PORT,
            "join_url": public_url.rstrip("/") + "/",
            "is_public_tunnel": True
        }

    local_ip = get_local_ip()
    return {
        "ip": local_ip,
        "port": PORT,
        "join_url": f"http://{local_ip}:{PORT}/",
        "is_public_tunnel": False
    }

class TopicChangeRequest(BaseModel):
    topic_id: str

@app.get("/api/topics")
async def get_topics_endpoint():
    """Returns available training topics and metadata (only visible/active topics for Host)."""
    from app.questions_data import get_all_topics
    return get_all_topics(include_hidden=False)

@app.post("/api/room/{room_code}/topic")
async def change_room_topic_endpoint(room_code: str, req: TopicChangeRequest):
    """Changes the active topic for a game room."""
    success = await game_manager.change_topic(room_code.upper().strip(), req.topic_id)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo cambiar el tema (la partida puede haber iniciado ya).")
    return {"success": True, "room_code": room_code, "topic_id": req.topic_id}

@app.get("/api/session/{room_code}/export")
async def export_session_results(room_code: str):
    """Exports session participants and scores to CSV."""
    rows = get_session_export_rows(room_code.upper().strip())
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron datos para esta sala.")

    output = io.StringIO()
    # Write BOM for Excel UTF-8 compatibility
    output.write('\ufeff')
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=Zoho_Recruit_CyberArena_{room_code}.csv"
    return response

# ==============================================================================
# AUTHENTICATION & DASHBOARD API ENDPOINTS
# ==============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
async def login_endpoint(req: LoginRequest):
    """Logs in an administrator or facilitator."""
    res = authenticate_user(req.username, req.password)
    if not res:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")
    if "error" in res:
        raise HTTPException(status_code=403, detail=res["error"])

    token = secrets.token_hex(24)
    AUTH_SESSIONS[token] = res

    response = Response(
        content=json.dumps({"success": True, "token": token, "user": res}),
        media_type="application/json"
    )
    # Set cookie for direct browser navigation to /admin
    response.set_cookie(key="auth_token", value=token, httponly=False, max_age=86400, samesite="lax")
    return response

@app.get("/api/auth/me")
async def get_me_endpoint(request: Request):
    """Returns profile of currently logged-in user."""
    user = require_auth(request)
    return {"authenticated": True, "user": user}

@app.post("/api/auth/logout")
async def logout_endpoint(request: Request):
    """Destroys current auth session."""
    user = get_current_user(request)
    auth_header = request.headers.get("authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif "auth_token" in request.cookies:
        token = request.cookies.get("auth_token")

    if token and token in AUTH_SESSIONS:
        del AUTH_SESSIONS[token]

    response = Response(content=json.dumps({"success": True}), media_type="application/json")
    response.delete_cookie("auth_token")
    return response

# --- Dashboard & Stats ---

@app.get("/api/admin/stats")
async def get_admin_stats(request: Request):
    """Returns overview metrics for dashboard."""
    require_auth(request)
    from app.questions_data import get_all_topics
    all_t = get_all_topics()
    all_u = get_all_users()
    sessions = get_sessions_history()
    
    total_q = sum(t.get("question_count", 0) for t in all_t)
    total_participants = sum(s.get("total_participants", 0) for s in sessions)

    return {
        "active_rooms_count": len([r for r in game_manager.rooms.values() if r.status != "FINISHED"]),
        "total_topics": len(all_t),
        "total_questions": total_q,
        "total_users": len(all_u),
        "total_sessions": len(sessions),
        "total_participants": total_participants
    }

# --- Users Management (Admin Only) ---

class CreateUserPayload(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str = "facilitator"

class UpdateStatusPayload(BaseModel):
    is_active: bool

@app.get("/api/admin/users")
async def list_users_endpoint(request: Request):
    require_auth(request, require_admin=True)
    return get_all_users()

@app.post("/api/admin/users")
async def create_user_endpoint(payload: CreateUserPayload, request: Request):
    require_auth(request, require_admin=True)
    try:
        new_u = create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role=payload.role
        )
        return {"success": True, "user": new_u}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando usuario: {str(e)}")

@app.put("/api/admin/users/{user_id}/status")
async def update_user_status_endpoint(user_id: str, payload: UpdateStatusPayload, request: Request):
    require_auth(request, require_admin=True)
    update_user_status(user_id, payload.is_active)
    return {"success": True, "user_id": user_id, "is_active": payload.is_active}

@app.delete("/api/admin/users/{user_id}")
async def delete_user_endpoint(user_id: str, request: Request):
    user = require_auth(request, require_admin=True)
    if user.get("id") == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta mientras estás conectado.")
    try:
        delete_user(user_id)
        return {"success": True, "deleted_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Topics / Capacitaciones CRUD ---

class SaveTopicPayload(BaseModel):
    id: str
    name: str
    badge: str
    description: str = ""
    default_pin: str = "CUN2026"

class TopicVisibilityPayload(BaseModel):
    is_active: bool

@app.get("/api/admin/topics")
async def list_admin_topics(request: Request):
    require_auth(request)
    return get_all_topics_from_db(include_hidden=True)

@app.get("/api/admin/topics/{topic_id}")
async def get_topic_detail(topic_id: str, request: Request):
    require_auth(request)
    t = get_topic_from_db(topic_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tema no encontrado.")
    return t

@app.post("/api/admin/topics")
async def save_topic_endpoint(payload: SaveTopicPayload, request: Request):
    user = require_auth(request)
    t = save_topic(
        topic_id=payload.id,
        name=payload.name,
        badge=payload.badge,
        description=payload.description,
        default_pin=payload.default_pin,
        created_by=user.get("username", "admin")
    )
    return {"success": True, "topic": t}

@app.put("/api/admin/topics/{topic_id}/visibility")
async def toggle_topic_visibility_endpoint(topic_id: str, payload: TopicVisibilityPayload, request: Request):
    require_auth(request)
    new_status = toggle_topic_visibility(topic_id, payload.is_active)
    return {"success": True, "topic_id": topic_id, "is_active": new_status}

@app.delete("/api/admin/topics/{topic_id}")
async def delete_topic_endpoint(topic_id: str, request: Request):
    require_auth(request)
    delete_topic(topic_id)
    return {"success": True, "deleted_id": topic_id}

# --- Questions CRUD ---

class SaveQuestionPayload(BaseModel):
    id: Optional[str] = None
    topic_id: str
    order_num: int = 1
    type: str = "CHOICE"
    category: str = "GENERAL"
    title: str
    question_text: str
    options: list
    correct_answer: Any = None
    correct_order: Optional[list] = None
    explanation: str = ""
    time_limit_sec: int = 25
    points_base: int = 1000

@app.get("/api/admin/topics/{topic_id}/questions")
async def list_topic_questions(topic_id: str, request: Request):
    require_auth(request)
    return get_questions_by_topic(topic_id)

@app.post("/api/admin/questions")
async def save_question_endpoint(payload: SaveQuestionPayload, request: Request):
    require_auth(request)
    saved = save_question(payload.dict())
    return {"success": True, "question": saved}

@app.delete("/api/admin/questions/{question_id}")
async def delete_question_endpoint(question_id: str, request: Request):
    require_auth(request)
    delete_question(question_id)
    return {"success": True, "deleted_id": question_id}

# --- Sessions & History ---

@app.get("/api/admin/sessions")
async def list_sessions_endpoint(request: Request):
    require_auth(request)
    return get_sessions_history()

# --- Participants & Evaluated People ---

@app.get("/api/admin/participants")
async def list_participants_endpoint(
    request: Request,
    search: Optional[str] = Query(None),
    topic: Optional[str] = Query(None)
):
    """Returns list of evaluated participants with optional search and topic filtering."""
    require_auth(request)
    return get_all_participants(topic_filter=topic, search=search)

@app.get("/api/admin/participants/{participant_id}")
async def get_participant_detail_endpoint(participant_id: str, request: Request):
    """Returns detailed answers and metrics for an individual participant."""
    require_auth(request)
    detail = get_participant_detail_with_answers(participant_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Participante no encontrado.")
    return detail

@app.get("/api/admin/participants/export/csv")
async def export_all_participants_csv(request: Request):
    """Exports all evaluated participants to CSV with UTF-8 BOM for Excel."""
    require_auth(request)
    rows = get_all_participants_export_rows()
    if not rows:
        raise HTTPException(status_code=404, detail="No hay participantes registrados para exportar.")

    output = io.StringIO()
    output.write('\ufeff')  # BOM for Excel
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=Evaluados_CyberArena_CUN_Consolidado.csv"
    return response

# --- Advanced Analytics ---

@app.get("/api/admin/analytics")
async def get_analytics_endpoint(request: Request):
    """Returns comprehensive analytics metrics, topic breakdown, leaderboard and question stats."""
    require_auth(request)
    return get_analytics_dashboard_data()

# --- Real-Time WebSocket Hub ---

@app.websocket("/ws/{room_code}/{client_type}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_code: str, 
    client_type: str, 
    client_id: str = Query(None)
):
    await websocket.accept()
    room_code = room_code.upper().strip()
    await game_manager.attach_ws(room_code, client_type, client_id, websocket)

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
            except Exception:
                continue

            action = msg.get("action")

            if client_type == "host":
                if action == "START_GAME":
                    await game_manager.start_game(room_code)
                elif action == "CHANGE_TOPIC":
                    await game_manager.change_topic(room_code, msg.get("topic_id"))
                elif action == "NEXT_QUESTION":
                    await game_manager.next_question(room_code)
                elif action == "REVEAL_RESULTS":
                    await game_manager.reveal_results(room_code)
                elif action == "SHOW_LEADERBOARD":
                    await game_manager.show_leaderboard(room_code)
            
            elif client_type == "player":
                if action == "SUBMIT_ANSWER":
                    answer_payload = msg.get("answer")
                    await game_manager.submit_answer(room_code, client_id, answer_payload)

    except WebSocketDisconnect:
        await game_manager.detach_ws(room_code, client_type, client_id)
    except Exception as e:
        print(f"WS error: {e}")
        await game_manager.detach_ws(room_code, client_type, client_id)
