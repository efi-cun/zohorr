import os
import socket
import json
import csv
import io
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from app.database import init_db, get_session_export_rows
from app.game_manager import game_manager
from app.config import HOST, PORT

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
async def network_ip_endpoint():
    public_url = os.getenv("PUBLIC_WEB_URL")
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
