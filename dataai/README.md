# 3.SEATECH DataAI Frontend

Frontend estático independiente para `data.3seatech.com`.

## Cloudflare Pages

- Repositorio: `3seatech-cyber/3seatech-web`
- Rama: `main`
- Root directory: `dataai`
- Framework preset: None
- Build command: `exit 0` (o vacío)
- Build output directory: `.`
- Custom domain: `data.3seatech.com`

## Backend

El frontend usa `https://api-data.3seatech.com`, publicado mediante Cloudflare Tunnel hacia `http://localhost:8000`.

El login visual ya está implementado, pero la autenticación real requiere que el backend implemente `POST /api/auth/login`. No se almacenan credenciales en este frontend.

El dashboard de demostración muestra estado online/offline y mantiene disponible la interfaz aunque el servidor analítico esté desconectado.
