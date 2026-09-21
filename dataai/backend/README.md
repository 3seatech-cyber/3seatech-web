# 3SeaTech DataAI backend

Backend local para `api-data.3seatech.com` mediante Cloudflare Tunnel.

## Primera configuración (Windows)

1. Abra CMD en esta carpeta y ejecute `INICIAR_DATAAI.bat` una vez para crear `.venv`.
2. Genere un hash: `.venv\Scripts\python crear_password.py`.
3. Copie **solo el hash generado** y configure:
   - `setx DATAAI_ADMIN_USER "su_usuario"`
   - `setx DATAAI_ADMIN_PASSWORD_HASH "$2b$..."`
4. Cierre y vuelva a abrir CMD para cargar las variables.
5. Ejecute `INICIAR_DATAAI.bat` como administrador si necesita iniciar el servicio cloudflared.

No suba contraseñas ni hashes reales al repositorio. El frontend permite visualizarse aunque este backend esté apagado.

## Endpoints iniciales

- `GET /health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`

Siguiente fase: usuarios/roles persistentes, SQLite, uploads, WebSocket, Knowledge/RAG y forecast.
