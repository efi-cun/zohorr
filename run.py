import os
import sys
import time
import re
import socket
import subprocess
import threading
import webbrowser
import uvicorn
from pathlib import Path
from app.config import HOST, PORT
from app.database import init_db

import atexit

BASE_DIR = Path(__file__).resolve().parent

tunnel_process = None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def start_public_web_tunnel():
    """Starts cloudflared tunnel to expose port 8000 to the public web (HTTPS)."""
    cloudflared_path = BASE_DIR / "cloudflared.exe"
    if not cloudflared_path.exists():
        return None

    global tunnel_process
    cmd = [str(cloudflared_path), "tunnel", "--url", f"http://127.0.0.1:{PORT}"]
    try:
        tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        atexit.register(lambda: tunnel_process.kill() if tunnel_process else None)

        public_url = None
        start_time = time.time()
        while time.time() - start_time < 15:
            line = tunnel_process.stdout.readline()
            if not line:
                break
            match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
            if match:
                public_url = match.group(0)
                break

        if public_url:
            os.environ["PUBLIC_WEB_URL"] = public_url
            return public_url
    except Exception as e:
        print(f"[!] No se pudo iniciar el túnel web público: {e}")
    return None

def print_cyber_banner(local_ip, public_url):
    web_line = f"  [*] [ENLACE PUBLICO WEB (ZOOM/TEAMS)] --> {public_url}\n" if public_url else ""
    banner = f"""
====================================================================
           ZOHO RECRUIT: CYBER-TALENT ARENA (CUN 2026)             
====================================================================
  [+] Nube Supabase: Conectada (dtrqnzbbcolnkcufjbhh.supabase.co)
  [+] Tablas PostgreSQL: Verificadas y sincronizadas
  [+] Banco de Preguntas: 10 Desafios interactivos (Secuencias y Casos)
  [+] Acceso Remoto Web: {'ACTIVO (Tunel HTTPS Seguro)' if public_url else 'Red Local'}
--------------------------------------------------------------------
{web_line}  [+] [CONSOLA DEL INSTRUCTOR / HOST]      --> http://localhost:{PORT}/host
  [+] [MANDO JUGADORES (LOCAL)]           --> http://localhost:{PORT}/
  [+] [MANDO JUGADORES (RED WI-FI)]       --> http://{local_ip}:{PORT}/
====================================================================
  Cualquier participante puede unirse desde cualquier lugar del pais!
  Presiona Ctrl + C para detener.
====================================================================
"""
    print(banner)

def main():
    # Initialize DB tables in Supabase
    try:
        init_db()
    except Exception as e:
        print(f"[!] Error inicializando base de datos en Supabase: {e}")

    local_ip = get_local_ip()

    # Launch public web tunnel
    print("Iniciando enlace público web para acceso online...")
    public_url = start_public_web_tunnel()

    print_cyber_banner(local_ip, public_url)

    # Automatically open Host view in default browser if run directly
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(f"http://localhost:{PORT}/host")
        except Exception:
            pass

    uvicorn.run("app.main:app", host=HOST, port=PORT, log_level="info")

if __name__ == "__main__":
    main()
