# ⚡ QUICK START - 5 Minutes Setup

## 1️⃣ Create Telegram Bot (2 minutes)

**In Telegram:**
- Search: `@BotFather`
- Send: `/newbot`
- Name your bot: `BrandoJobAlerts`
- Username: `brando_job_alerts_bot` (must be unique)
- **COPY THE TOKEN** (looks like: `123456:ABC...`)

**Get Chat ID:**
- Search: `@userinfobot`
- Send: `/start`
- **COPY YOUR CHAT ID** (a number)

---

## 2️⃣ Create GitHub Repository (1 minute)

```bash
# Clone this repo or create new one
git clone https://github.com/YOUR_USERNAME/job_automation.git
cd job_automation

# (Or init new repo with these files)
```

---

## 3️⃣ Add GitHub Secrets (1 minute)

**GitHub → Repo → Settings → Secrets and variables → Actions**

Create two secrets:

| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | Paste your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Paste your chat ID number |

---

## 4️⃣ Push & Enable (1 minute)

```bash
git add .
git commit -m "Setup job automation"
git push origin main
```

**GitHub → Actions tab → Enable workflows**

---

## ✅ DONE! 🎉

The bot will now:
- ✅ Run automatically every 4 hours
- ✅ Send you Telegram alerts for matching jobs
- ✅ Avoid duplicate notifications
- ✅ Cost $0 (completely free)

---

## 📱 What You'll Receive

```
🚀 NUEVA VACANTE ENCONTRADA

📌 Cisco - Network Support Engineering Intern
🏢 Location: Mexico City, CDMX
💼 Type: Internship
🔗 APPLY NOW → [clickable link]
```

Every job that matches your filters!

---

## 🔧 Customize (Optional)

**Edit `config.py` to:**
- Add/remove job keywords
- Change locations
- Whitelist specific companies
- Adjust notification frequency

**Edit `.github/workflows/job_alert.yml` to:**
- Change run schedule (currently every 4 hours)
- Enable different scrapers

---

## 🆘 Troubleshooting

**Not getting alerts?**
1. Check GitHub Actions logs (Actions tab → latest run)
2. Verify Telegram secrets are correct
3. Ensure bot has received `/start` command

**Errors in workflow?**
- Read the GitHub Actions logs for details
- Test locally: `python main.py`

**Want to test manually?**
```bash
pip install -r requirements.txt
python main.py
```

---

## 📚 Full Documentation

See `README.md` for complete setup guide with:
- Detailed Telegram setup
- Custom filtering
- Troubleshooting
- Monitoring
- Contributing

---

## 🎯 You're All Set!

Your automated job alert system is now live. 

**Next:** Apply to the jobs you receive! 💪

Good luck! 🚀
