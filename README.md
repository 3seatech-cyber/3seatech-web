# 3.SEATECH Web

Sitio corporativo de 3.SEATECH preparado para despliegue continuo desde GitHub y publicación del portal DataAI mediante un subdominio independiente.

## Arquitectura v23

```text
GitHub: 3seatech-cyber/3seatech-web
              |
              v
        3seatech.com
     Web corporativa principal
              |
         enlace DataAI
              |
              v
   data.3seatech.com/portal
              |
        HTTPS / ngrok
              |
              v
       Servidor local
              |
     FastAPI + WebSync
              |
   +----------+-----------+
   |          |           |
 SQLite   Analítica IA   RAG
   |          |           |
Reportes  Autoencoder  Agente IA
           Forecast
```

### Dominio principal — `3seatech.com`

El frontend corporativo permanece en este repositorio y puede desplegarse continuamente desde la rama `main`. Es un sitio estático y no requiere comando de build.

El menú principal incluye un acceso a:

```text
https://data.3seatech.com/portal
```

### Subdominio DataAI — `data.3seatech.com`

DataAI se ejecuta en el servidor local de 3.SEATECH. El servidor inicia FastAPI, sincroniza la web corporativa mediante WebSync y publica el servicio mediante un túnel HTTPS de ngrok.

Rutas principales:

| Ruta | Función |
| --- | --- |
| `/portal` | Portal público DataAI y registro de reportes |
| `/dataai` | Alias del portal DataAI |
| `/login` | Acceso administrativo |
| `/data-ia` | Dashboard privado |
| `/site-sync` | Copia sincronizada de la web corporativa |
| `/api/public/reports` | API de recepción/consulta pública agregada |
| `/api/public/websync-status` | Estado de sincronización |

### WebSync

El servidor DataAI recupera la versión vigente de `3seatech-web` desde GitHub. De esta manera el sitio sincronizado del servidor puede mantenerse alineado con la web corporativa.

```text
git push
   |
   v
GitHub / main
   |
   +------> despliegue de 3seatech.com
   |
   +------> WebSync del servidor
                |
                v
          /site-sync
```

### Flujo de reportes

Los reportes ingresados en DataAI siguen el flujo:

```text
Usuario
  |
  v
data.3seatech.com/portal
  |
 HTTPS
  v
ngrok
  |
  v
FastAPI local
  |
  v
SQLite
  |
  +--> indicadores agregados
  +--> histórico
  +--> análisis de anomalías
  +--> pronósticos
```

Los reportes públicos son entradas no verificadas. La interfaz pública no debe exponer descripciones sensibles, datos de contacto ni ubicaciones exactas. La validación administrativa debe preceder cualquier uso como dato confirmado.

## Configuración del servidor

El paquete DataAI v23 utiliza un único iniciador en Windows:

```bat
INICIAR_3SEATECH_COMPLETO.bat
```

Este proceso actualiza WebSync, inicia FastAPI, inicia ngrok, detecta la URL pública y actualiza el acceso DataAI.

Para producción, `data.3seatech.com` debe ser un hostname estable. Si se utiliza ngrok, se recomienda un dominio custom/reservado compatible con el plan utilizado; una URL gratuita aleatoria puede cambiar después de reiniciar el túnel.

## Seguridad

No almacene tokens, contraseñas, claves SSH, `NGROK_AUTHTOKEN`, secretos de sesión ni credenciales en este repositorio. Manténgalos en variables de entorno, secretos del proveedor de despliegue o archivos locales excluidos de Git.

Los endpoints administrativos deben permanecer autenticados. Para recepción pública en producción se recomienda añadir rate limiting, CAPTCHA/anti-bot, moderación, copias de seguridad y una política de privacidad.

## Componentes previstos

- **www / raíz:** frontend corporativo.
- **data:** DataAI, WebSync y analítica.
- **shop:** comercio electrónico futuro.
- **apps:** aplicaciones.
- **api:** servicios backend privados cuando sean necesarios.

## Repositorio

Repositorio principal: `3seatech-cyber/3seatech-web`.

La rama `main` representa la versión destinada al despliegue público.
