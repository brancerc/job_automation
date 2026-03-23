# 🚀 IMPLEMENTACIÓN PASO A PASO - GitHub Actions

## PASO 1️⃣: Crear Telegram Bot (5 min)

### 1.1 Crear el bot en Telegram

```
1. Abre Telegram
2. Busca: @BotFather
3. Envía: /newbot
4. Responde las preguntas:
   - ¿Nombre del bot? → bcercJobAlerts
   - ¿Username del bot? → bcerc_job_alerts_bot (DEBE SER ÚNICO)
5. ✅ Te dará un TOKEN (cópialo, lo necesitarás):  8776167013:AAFiQqCB5ysW9s9ipnLBbh3Ncd1VuT6xVjw
```

### 1.2 Obtener tu Chat ID

```
1. Busca en Telegram: @userinfobot
2. Envía: /start
3. Te mostrará tu Chat ID (un número como 987654321)
4. Cópialo  5463123453
```

### 1.3 Iniciar tu bot

```
1. Busca tu bot: bcercJobAlerts
2. Envía: /start
3. ✅ Bot inicializado
```

---

## PASO 2️⃣: Crear Repositorio en GitHub (3 min)

### Opción A: Usar repo existente (Si tienes una cuenta)

```bash
# 1. Ir a https://github.com/new
# 2. Llenar:
#    - Repository name: job_automation
#    - Description: Automated job alerts for internships in CDMX
#    - Public ✅
#    - README: Sin marcar (ya tenemos)
# 3. Crear repositorio
```

### Opción B: Si ya tienes git configurado localmente

```bash
# Navegar a la carpeta del proyecto
cd /ruta/a/job_automation

# Configurar git (primera vez)
git config --global user.email "tu_email@gmail.com"
git config --global user.name "Tu Nombre"

# Agregar todos los archivos
git add .

# Hacer commit inicial
git commit -m "🚀 Configuración inicial: Job automation con GitHub Actions"

# Conectar con tu repositorio en GitHub
git remote add origin https://github.com/TU_USERNAME/job_automation.git

# Cambiar rama a main (si está en master)
git branch -M main

# Pushear código
git push -u origin main
```

---

## PASO 3️⃣: Agregar Secrets en GitHub (3 min)

### Cómo agregar los secrets

```
1. Ir a tu repositorio en GitHub:
   https://github.com/TU_USERNAME/job_automation

2. Clic en: Settings (pestaña)
   ↓
3. Clic en: Secrets and variables → Actions
   (En la izquierda, bajo "Security")
   ↓
4. Clic en: "New repository secret" (botón verde)
   ↓
5. PRIMER SECRET:
   Name: TELEGRAM_BOT_TOKEN
   Value: [Pega el TOKEN de BotFather]
   Clic: "Add secret"
   ↓
6. SEGUNDO SECRET:
   Name: TELEGRAM_CHAT_ID
   Value: [Pega tu Chat ID de @userinfobot]
   Clic: "Add secret"
```

### Verificación

```
Deberías ver dos secrets listados:
✅ TELEGRAM_BOT_TOKEN
✅ TELEGRAM_CHAT_ID

(Los valores no se muestran, solo *** para seguridad)
```

---

## PASO 4️⃣: Habilitar GitHub Actions (1 min)

```
1. En tu repositorio, ve a: Actions (pestaña)
   ↓
2. Si ves mensaje "Workflows are disabled":
   - Clic en: "I understand my workflows, go ahead and enable them"
   ↓
3. Clic en: "🚀 Job Scraper Alert" (en la izquierda)
   ↓
4. ✅ Actions habilitadas!
```

---

## PASO 5️⃣: Probar Manualmente (Opcional, 30 seg)

```
1. Ve a: Actions → "🚀 Job Scraper Alert"
   ↓
2. Clic en: "Run workflow"
   ↓
3. Botón: "Run workflow" (confirmar)
   ↓
4. Espera a que se complete (~30 segundos)
   ↓
5. ✅ Deberías recibir un mensaje en Telegram con vacantes!
```

---

## PASO 6️⃣: Configurar Ejecución Automática (1 min - OPCIONAL)

El bot ya está configurado para ejecutarse **cada 4 horas automáticamente**.

Si quieres cambiar la frecuencia:

```
1. En tu repo, abre: .github/workflows/job_alert.yml
   ↓
2. Busca esta sección:
   on:
     schedule:
       - cron: '0 */4 * * *'

3. Cambia el número:
   */4  = Cada 4 horas (default)
   */2  = Cada 2 horas
   */1  = Cada 1 hora
   */6  = Cada 6 horas

4. Clic en Commit changes (abajo)
```

[Ayuda con cron times](https://crontab.guru/)

---

## PASO 7️⃣: Personalizar Filtros (5 min - OPCIONAL)

Si quieres cambiar qué vacantes ves:

### Editar palabras clave

```
1. Abre en GitHub: config.py
   ↓
2. Busca: FILTER_KEYWORDS = [ ... ]
   ↓
3. Agrega o elimina palabras (examples):
   'your_keyword',
   'another_keyword',
   ↓
4. Clic: Commit changes
```

### Editar empresas

```
En el mismo archivo, busca:
COMPANY_WHITELIST = [
    'Cisco',
    'Ericsson',
    'Dahua',
    ...
]

Agrega las que te interesen
```

### Editar ubicaciones

```
FILTER_LOCATIONS = [
    'cdmx',
    'mexico city',
    'miguel hidalgo',
    ...
]
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

```
☐ TELEGRAM:
  ☐ Crear bot con @BotFather
  ☐ Copiar TOKEN
  ☐ Obtener Chat ID de @userinfobot
  ☐ Enviar /start al bot

☐ GITHUB:
  ☐ Crear repositorio (job_automation)
  ☐ Pushear código
  ☐ Agregar TELEGRAM_BOT_TOKEN secret
  ☐ Agregar TELEGRAM_CHAT_ID secret
  ☐ Habilitar GitHub Actions

☐ PRUEBA:
  ☐ Ejecutar manualmente desde Actions
  ☐ Recibir primer mensaje en Telegram
  ☐ Verificar formato del mensaje

☐ OPCIONAL:
  ☐ Personalizar filtros en config.py
  ☐ Cambiar frecuencia en job_alert.yml
```

---

## 📱 QUÉ ESPERAR

### Primer mensaje (cuando se ejecute):

```
🚀 NUEVA VACANTE ENCONTRADA

📌 Cisco - Network Support Engineering Intern
🏢 Location: Mexico City, CDMX
💼 Type: Internship (6 months)
📅 Posted: 2024-03-19

Source: Cisco Careers

🔗 APPLY NOW
```

### Recurrencia:

- ✅ Automáticamente cada 4 horas
- ✅ Solo vacantes nuevas (sin duplicados)
- ✅ Filtradas por tus criterios
- ✅ Links directos para aplicar

---

## 🆘 TROUBLESHOOTING

### No recibo mensajes

**1. Verificar secrets:**

```
GitHub → Settings → Secrets and variables → Actions
- ¿TELEGRAM_BOT_TOKEN está ahí?
- ¿TELEGRAM_CHAT_ID está ahí?
```

**2. Verificar Actions está habilitado:**

```
Actions → ¿Ves "🚀 Job Scraper Alert"?
```

**3. Verificar logs:**

```
Actions → Latest run → Clic en job → Ver logs
```

**4. Verificar bot en Telegram:**

```
Busca tu bot y envía: /start
```

### GitHub Actions muestra error

```
1. Ve a: Actions → "🚀 Job Scraper Alert" → Latest run
2. Clic en: scrape-and-notify
3. Lee el error rojo
4. Errores comunes:
   - TELEGRAM_BOT_TOKEN incorrecto → revisar secret
   - TELEGRAM_CHAT_ID incorrecto → revisar secret
   - No hay conexión → revisar network GitHub
```

### No encuentra vacantes

```
Los filtros pueden ser muy restrictivos.

Edita config.py y:
1. Agrega más keywords
2. Expande locations
3. Desactiva exclude_keywords (comentar líneas)

Push → Próxima ejecución encontrará más!
```

---

## 🎯 RESUMEN RÁPIDO

```
⏱️ TIEMPO TOTAL: ~15 minutos

1. Telegram bot + token (5 min)
2. GitHub repo (3 min)
3. Agregar secrets (3 min)
4. Habilitar Actions (1 min)
5. Probar (3 min)

✅ LISTO! Tu bot está vivo!
```

---

## 📊 DESPUÉS DE IMPLEMENTAR

- ✅ Recibirás alertas cada 4 horas automáticamente
- ✅ Ningún servidor que mantener
- ✅ Completamente GRATIS
- ✅ Base de datos que crece con tiempo
- ✅ Histórico de todas las vacantes vistas

---

## 🚀 SIGUIENTE PASO

Una vez implementado:

1. **Espera a primer run** (máximo 4 horas)
2. **Revisa mensajes Telegram**
3. **Aplica a vacantes interesantes**
4. **Personaliza filtros según necesidad**

¡Mucho éxito en tu búsqueda de empleo! 💪
