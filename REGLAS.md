# REGLAS - App-Soporte

> **Instrucción para IA:** Cuando el usuario diga "leer reglas", lee este archivo para recuperar contexto del proyecto.

---

## 📋 DESCRIPCIÓN DEL PROYECTO

**PcGraf-Soporte** es una aplicación web para gestión de visitas técnicas.

- **Ubicación fuentes:** `c:\pcgraf\fuentes\app-soporte\`
- **Repositorio:** github.com/jmorales-dsg/app-soporte
- **Deploy:** Railway (automático al hacer push)
- **Versión actual:** 1.6.6

---

## 🔴 REGLAS IMPORTANTES

### ⛔ REGLA #1 - SIEMPRE PREGUNTAR ANTES DE ACTUAR
**No hacer nada sin preguntar primero.** Proponer "¿Quieres que haga X?" y esperar autorización explícita con "SI".

### ⛔ REGLA #2 - AUTORIZACIÓN SOLO CON "SI"
Solo proceder cuando el usuario diga **"SI"** (explícito). Cualquier otra respuesta significa comunicación, **NO es autorización**.

---

## ⚠️ LIMITACIONES CRÍTICAS - FLET WEB

### ❌ FLET FUE UN ERROR DE ELECCIÓN

Flet es un framework joven con **muchas limitaciones para web**:

| Limitación | Descripción |
|------------|-------------|
| **Android NO funciona** | Se queda en "working..." - Problema de WebSocket con navegadores Android |
| **No tiene set_clipboard** | No puede copiar al portapapeles |
| **No tiene run_javascript** | No puede ejecutar JS en el cliente |
| **No tiene launch_url_async** | No puede descargar archivos |
| **Versiones incompatibles** | Cada versión rompe sintaxis anterior |

### ✅ Funciona en:
- iOS (Safari)
- Windows (Chrome, Edge)

### ❌ NO funciona en:
- Android (Chrome, Firefox, cualquier navegador)

---

## 📜 REGLA PARA FUTUROS PROYECTOS WEB

**NO usar Flet para aplicaciones web.**

Usar tecnologías probadas:
- **Flask/FastAPI + HTML/CSS/JS puro** - Funciona en cualquier navegador
- **Django + templates** - Para apps más complejas

Estas tecnologías funcionan en iOS, Android, Windows, cualquier navegador sin problemas.

---

## 🏗️ ARQUITECTURA ACTUAL

```
app-soporte/
├── main.py          # Aplicación Flet principal
├── database.py      # PostgreSQL (Railway) / SQLite (local)
├── correo.py        # Envío de correos (SMTP bloqueado en Railway)
└── requirements.txt # flet>=0.21.0, psycopg2-binary
```

---

## 🗄️ BASE DE DATOS

- **Producción:** PostgreSQL en Railway (variable DATABASE_URL)
- **Local:** SQLite (soporte.db)

### Tablas:
- `soportistas` - Técnicos de soporte
- `clientes` - Clientes con soportista asignado
- `visitas` - Registro de visitas técnicas
- `tareas` - Tareas/pendientes independientes
- `configuracion` - Configuración SMTP

---

## 📝 LOG DE CAMBIOS

### Enero 2026
- **[10-Ene]** Investigación problema Android - NO tiene solución con Flet
- **[10-Ene]** Documentada limitación de Flet como error de elección
- **[10-Ene]** Revertido a v1.6.6 que funciona en iOS/Windows

### Versiones anteriores
- v1.6.6 - Pantalla completa para reporte con TextField
- v1.6.5 - Eliminado botón enviar correo (SMTP bloqueado)
- v1.6.0+ - Intentos fallidos de copiar al portapapeles

---

## 🔜 RECOMENDACIÓN FUTURA

Si se necesita soporte Android, **rehacer la app con Flask + HTML/CSS/JS puro**.

Estimación: 2-3 días de trabajo para migrar funcionalidad actual.

---

*Última actualización: 10-Enero-2026*

