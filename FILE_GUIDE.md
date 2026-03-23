# 📁 Guía de Archivos del Proyecto

## Estructura del Proyecto

```
job_automation/
│
├── 📄 README.md                         ⭐ Documentación completa
├── 📄 QUICKSTART.md                     ⭐ Setup en 5 minutos
├── 📄 IMPLEMENTACION_GITHUB.md          ⭐ Pasos paso a paso
├── 📄 ARCHITECTURE.md                   Arquitectura técnica (avanzado)
├── 📄 FILE_GUIDE.md                     Este archivo
│
├── 🐍 CÓDIGO PRINCIPAL (Python)
│   ├── main.py                          Orquestador principal
│   ├── job_scraper.py                   Lógica de scraping + BD
│   ├── telegram_bot.py                  Notificaciones Telegram
│   └── config.py                        Configuración personalizable
│
├── 📦 CONFIGURACIÓN
│   ├── requirements.txt                 Dependencias Python
│   ├── .gitignore                       Archivos ignorados
│   └── setup.py                         Script de configuración
│
├── ⚙️ GITHUB ACTIONS
│   └── .github/workflows/
│       └── job_alert.yml                Workflow automático
│
└── 📚 GIT
    └── .git/                            Repositorio Git
```

---

## 🎯 COMIENZA AQUÍ

1. **Leer:** QUICKSTART.md (5 min)
2. **Seguir:** IMPLEMENTACION_GITHUB.md (paso a paso)
3. **Referenciar:** ARCHITECTURE.md (si necesitas entender internals)

---

## 📄 Archivos de Documentación

### QUICKSTART.md
- **Para:** Gente con prisa
- **Tiempo:** 5 minutos
- **Contenido:** Pasos esenciales solamente
- **Cuándo leer:** Primero

### IMPLEMENTACION_GITHUB.md
- **Para:** Implementación en GitHub
- **Tiempo:** 15 minutos total
- **Contenido:** Paso a paso detallado con ejemplos
- **Cuándo leer:** Segundo

### ARCHITECTURE.md
- **Para:** Entender cómo funciona
- **Tiempo:** 20 minutos
- **Contenido:** Diagramas, flujos, componentes
- **Cuándo leer:** Después de que funcione

### README.md
- **Para:** Referencia completa
- **Tiempo:** 30 minutos
- **Contenido:** Todo (features, troubleshooting, etc)
- **Cuándo leer:** Cuando necesites referencia

---

## 🐍 Archivos Python

### main.py
```
Propósito: Orquestador principal
Qué hace:
  1. Crea JobAggregator
  2. Llama scrape_all()
  3. Crea JobTelegramNotifier
  4. Envía notificaciones
  5. Marca jobs como notificados

Ejecutado por: GitHub Actions (cada 4 horas)
Requiere: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID env vars
Líneas: ~50
Complejidad: ⭐ (muy simple)
```

### job_scraper.py
```
Propósito: Core del sistema
Componentes:

1. JobDatabase class
   - Maneja SQLite (jobs.db)
   - Métodos: add_job(), job_exists(), get_new_jobs()
   - Deduplicación por URL hash

2. CiscoScraper class
   - Scraping de Cisco Careers API
   - Busca internships en Mexico

3. LinkedInScraper class
   - Scraping de LinkedIn (básico)
   - Requiere Selenium para completo

4. OCCMexicoScraper class
   - Scraping de OCC.com.mx
   - Necesita mejoras en parsing

5. JobAggregator class
   - Coordina todos los scrapers
   - Filtra por keywords + locations
   - Deduplicación
   - Retorna jobs nuevos

Ejecutado por: main.py
Base de datos: jobs.db (SQLite, auto-creado)
Líneas: ~300
Complejidad: ⭐⭐⭐ (mayor parte de lógica)
```

### telegram_bot.py
```
Propósito: Enviar notificaciones a Telegram
Clase: JobTelegramNotifier

Métodos principales:
- format_job_message(job) → HTML formateado
- send_notification(job) → Envía un job
- send_summary(jobs) → Envía resumen
- send_notifications_batch(jobs) → Todo junto

Requiere: python-telegram-bot library
Secretos: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
Líneas: ~150
Complejidad: ⭐⭐ (async/await básico)
```

### config.py
```
Propósito: Centralizar configuración
Secciones:

- FILTER_KEYWORDS: ['intern', 'network', 'cisco', ...]
- FILTER_LOCATIONS: ['cdmx', 'mexico city', ...]
- EXCLUDE_KEYWORDS: ['senior', 'management', ...]
- COMPANY_WHITELIST: ['Cisco', 'Ericsson', ...]
- ENABLED_SCRAPERS: {cisco: True, linkedin: False, ...}
- TELEGRAM_SETTINGS: {...}
- DATABASE: {...}

Propósito: Editar esto SIN tocar código
Líneas: ~80
Complejidad: ⭐ (solo diccionarios)
```

---

## 📦 Archivos de Configuración

### requirements.txt
```
Contenido: Dependencias Python

- requests==2.31.0
  → Para HTTP requests (scraping)

- beautifulsoup4==4.12.2
  → Para parsing HTML

- python-telegram-bot==20.3
  → Para Telegram Bot API

- lxml==4.9.3
  → Parser de HTML/XML

Uso:
  pip install -r requirements.txt

Cuándo actualizar:
  Si agregas nuevas librerías
```

### .gitignore
```
Propósito: No subir ciertos archivos
Archivos ignorados:

- __pycache__/ (compilados Python)
- *.pyc (bytecode)
- .env (secretos locales)
- *.log (logs)
- venv/, env/ (virtual envs)

Archivos SÍ subidos:
- jobs.db (queremos historial)
- code *.py (el código)
- *.md (documentación)
```

### setup.py
```
Propósito: Setup interactivo
Flujo:

1. Pide Telegram BOT_TOKEN
2. Pide TELEGRAM_CHAT_ID
3. Guía para GitHub setup
4. Ayuda a personalizar filtros
5. Verifica dependencias instaladas

Uso:
  python setup.py

Cuándo usar:
  Primera vez en setup
```

---

## ⚙️ GitHub Actions

### .github/workflows/job_alert.yml
```
Propósito: Automatizar ejecución en GitHub

Trigger: schedule (cron job)
  - Corre cada 4 horas automáticamente
  - Personalizable

Steps:
  1. actions/checkout@v4
     → Descarga código del repo

  2. actions/setup-python@v4
     → Instala Python 3.11

  3. pip install -r requirements.txt
     → Instala dependencias

  4. python main.py
     → Ejecuta el bot
     Env vars: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

  5. git commit & push jobs.db
     → Guarda estado

Timeout: 15 minutos
Costo: 0 (dentro de 2000 min free/mes)

Cómo modificar:
  - Cambiar frequencia: editar cron
  - Cambiar Python version: editar python-version
  - Agregar steps: copiar/pegar step existente
```

---

## 🔐 Archivos Secretos (NO en GitHub)

```
Estos NO están en el repo (GitHub Secrets):

TELEGRAM_BOT_TOKEN
  → Token de tu bot de Telegram
  → Ubicación: GitHub Settings → Secrets
  → Nunca se muestra en logs

TELEGRAM_CHAT_ID
  → Tu Chat ID de Telegram
  → Ubicación: GitHub Settings → Secrets
  → Nunca se muestra en logs

.env (local)
  → Para testing local
  → Ignorado por .gitignore
  → Contiene secrets para desarrollo
```

---

## 📊 TAMAÑO Y COMPLEJIDAD

| Archivo | Tamaño | Complejidad | Editabilidad |
|---------|--------|-----------|-------------|
| main.py | ~2 KB | ⭐ | Casi no |
| job_scraper.py | ~10 KB | ⭐⭐⭐ | Media |
| telegram_bot.py | ~5 KB | ⭐⭐ | Poca |
| config.py | ~2 KB | ⭐ | SÍ 👈 |
| job_alert.yml | ~1 KB | ⭐⭐ | SÍ 👈 |
| requirements.txt | <1 KB | ⭐ | Si agregas libs |

👈 = Archivos a editar si quieres cambiar comportamiento

---

## 🔄 FLUJO DE DATOS

```
┌─ Cada 4 horas ─────────────────────┐
│                                     │
│  GitHub Actions dispara             │
│         ↓                           │
│  python main.py                     │
│         ↓                           │
│  JobAggregator.scrape_all()        │
│    ├─ CiscoScraper.scrape()        │
│    ├─ LinkedInScraper.scrape()     │
│    └─ OCCMexicoScraper.scrape()    │
│         ↓                           │
│  Filtrado + Deduplicación          │
│    └─ jobs.db (SQLite)             │
│         ↓                           │
│  JobTelegramNotifier               │
│    ├─ send_notification() (cada)   │
│    └─ send_summary() (consolidado) │
│         ↓                           │
│  📱 TELEGRAM → TÚ RECIBES ALERT     │
│         ↓                           │
│  git commit jobs.db                │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎯 CUÁL EDITAR PARA QUÉ

### Quiero cambiar filtros
→ Edita: `config.py`
→ Sección: `FILTER_KEYWORDS`, `FILTER_LOCATIONS`
→ Push a GitHub

### Quiero cambiar frecuencia
→ Edita: `.github/workflows/job_alert.yml`
→ Busca: `cron: '0 */4 * * *'`
→ Push a GitHub

### Quiero agregar nueva fuente
→ Edita: `job_scraper.py`
→ Crea: Nueva clase scraper
→ Registra en: `JobAggregator.__init__`
→ Push a GitHub

### Quiero cambiar formato de mensajes
→ Edita: `telegram_bot.py`
→ Método: `format_job_message()`
→ Push a GitHub

---

## 📚 ARCHIVOS QUE NO EDITAR (generalmente)

```
❌ main.py
   → Orquestación core
   → Cambios aquí pueden romper todo

❌ job_scraper.py (JobAggregator class)
   → Lógica compleja
   → Requiere testing exhaustivo

✅ job_scraper.py (Agregar scraper)
   → Es bien estructurado para esto

❌ telegram_bot.py (core)
   → Async/await complejo

✅ telegram_bot.py (format_job_message)
   → Seguro de editar formato
```

---

## 🚀 DEPLOYMENT WORKFLOW

```
LOCAL:
  Editas archivo
  ↓
GITHUB:
  git commit & push
  ↓
GITHUB ACTIONS:
  Próxima ejecución automática
  ↓
RESULTADO:
  jobs.db actualizado
  Telegram notificado
  ✅ Changes en vivo!
```

---

## 🆘 SI ALGO SALE MAL

### Error en logs de GitHub Actions
→ Ver: Actions → Latest run → scrape-and-notify → logs
→ Buscar: línea roja con "Error"
→ Leer descripción

### No funciona after editar config.py
→ Verificar: Sintaxis Python correcta
→ Verificar: Comillas balanceadas
→ Esperar: Próxima ejecución (hasta 4 hrs)

### Base de datos corrupta
→ Solución: Eliminar `jobs.db`
→ Auto-recreada en próximo run

---

¡Ahora ve a **IMPLEMENTACION_GITHUB.md** para los pasos exactos! 🚀
