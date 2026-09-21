# 3.SEATECH Web

Sitio corporativo de 3.SEATECH. La página principal `3seatech.com` y `www.3seatech.com` permanecen como frontend corporativo estático. DataAI se implementa como una aplicación independiente en el subdominio `data.3seatech.com`.

## Arquitectura DataAI

```text
3seatech.com / www.3seatech.com
        |
        | enlace DataAI (sin modificar el contenido principal)
        v
https://data.3seatech.com
        |
        v
Cloudflare Tunnel: 3seatech-dataai
        |
        v
http://localhost:8000
        |
        v
FastAPI en servidor local
        |
   +----+---------+-----------+
   |              |           |
 SQLite       Knowledge/RAG  Modelos IA
   |                          |
 WebSync                 AE / Forecast
   |
 WebSocket
   |
 Usuarios conectados
```

Cloudflare Tunnel es el canal de producción. El servidor local no necesita exponer públicamente el puerto 8000.

## Página principal

La web corporativa sigue desplegándose desde este repositorio. DataAI no sustituye ni altera las secciones de Inicio, Nosotros, Proyectos, Soluciones, I+D o Contacto.

El único punto de integración previsto es el acceso DataAI, cuyo destino estable es:

```text
https://data.3seatech.com
```

## Subdominio DataAI

Al entrar a `https://data.3seatech.com`, FastAPI debe comprobar la sesión.

```text
data.3seatech.com
       |
       v
¿sesión válida?
   |       |
   no      sí
   |       |
 /login  /dashboard
```

### Entorno de inicio

La primera pantalla será un login independiente con identidad 3.SEATECH DataAI. Después de autenticarse, el usuario accederá al dashboard según su rol.

Roles previstos:

| Rol | Visualización | Carga de datos | Pronóstico | Administración |
| --- | --- | --- | --- | --- |
| Viewer | Sí | No | No | No |
| Editor | Sí | Sí | Sí | No |
| Admin | Sí | Sí | Sí | Sí |

### Dashboard

El entorno autenticado incorporará:

- datos WebSync y estado del servidor;
- visualización en tiempo real;
- histórico, indicadores y mapas;
- carga de CSV, XLSX y JSON, con soporte documental controlado;
- staging y validación antes de consolidar datos;
- Autoencoder y detección de anomalías;
- ejecución y consulta de pronósticos;
- Knowledge/RAG y agente IA;
- auditoría de cargas y resultados.

## Puente bidireccional

### Ida: navegador al servidor local

```text
Usuario
  -> HTTPS data.3seatech.com
  -> Cloudflare Tunnel
  -> FastAPI localhost:8000
  -> validación / staging
  -> SQLite / Knowledge
  -> modelos
```

Cada carga debe registrar usuario, fecha, fuente, batch_id, checksum, filas recibidas, válidas y rechazadas.

### Vuelta: servidor local al navegador

```text
SQLite / modelos / WebSync
  -> FastAPI
  -> WebSocket
  -> Cloudflare Tunnel
  -> usuarios conectados
```

Cloudflare Tunnel soporta WebSockets, por lo que el dashboard podrá recibir cambios sin recargar manualmente la página.

## Rutas previstas

| Ruta | Acceso | Función |
| --- | --- | --- |
| `/` | público | redirección a login o dashboard según sesión |
| `/login` | público | inicio de sesión |
| `/dashboard` | autenticado | DataAI |
| `/health` | técnico | estado mínimo del servicio |
| `/api/data/upload` | Editor/Admin | carga de nueva data |
| `/api/forecast/run` | Editor/Admin | ejecución de pronóstico |
| `/api/websync/status` | autenticado | estado WebSync |
| `/ws/dataai` | autenticado | actualizaciones en tiempo real |
| `/admin` | Admin | usuarios, aprobación y auditoría |

## Cloudflare

Configuración actual prevista:

```text
Tunnel: 3seatech-dataai
Public hostname: data.3seatech.com
Service: http://localhost:8000
```

`cloudflared` debe ejecutarse en la misma máquina que FastAPI. Cloudflare es el acceso estable de producción. ngrok puede conservarse únicamente como canal alternativo de pruebas y diagnóstico.

## Datos y seguridad

Los datos dinámicos no se almacenan en GitHub. GitHub contiene el frontend corporativo y la documentación/artefactos de despliegue; SQLite, archivos cargados, Knowledge y resultados permanecen en el servidor local.

No almacenar en este repositorio tokens de Cloudflare, contraseñas, claves SSH, secretos de sesión, tokens ngrok ni credenciales.

Las cargas realizadas por usuarios deben pasar por validación. Reportes no verificados no deben incorporarse automáticamente como incidentes confirmados ni alimentar modelos de producción sin aprobación.

## Estado de implementación

- [x] Dominio corporativo existente
- [x] Subdominio DataAI definido
- [x] Cloudflare Tunnel creado
- [x] Ruta `data.3seatech.com -> http://localhost:8000` configurada
- [ ] FastAPI DataAI iniciado en puerto 8000
- [ ] Login multiusuario conectado a la base local
- [ ] Roles Viewer / Editor / Admin
- [ ] Upload con staging y validación
- [ ] WebSocket bidireccional
- [ ] Integración WebSync
- [ ] Forecast sobre datos aprobados
- [ ] Auditoría y backups
- [ ] Pruebas externas y endurecimiento de seguridad

## Repositorio

Repositorio principal: `3seatech-cyber/3seatech-web`.

La rama `main` representa la versión destinada al despliegue público.
