# 🚀 Harpans Deployment Guide

## Pre-deployment Checklist

### Lokalt (INNAN upload):
- [ ] Kör `python security_check.py`
- [ ] Generera ny SECRET_KEY
- [ ] Kontrollera .gitignore innehåller .env och db.sqlite3
- [ ] Test att allt fungerar lokalt: `python manage.py runserver`
- [ ] Bygg Tailwind: `npm run build`
- [ ] Commit till git (om applicable)

### På Linode:
- [ ] Ubuntu 22.04 LTS installerad
- [ ] 2GB RAM (minimum 1GB)
- [ ] Firewall konfigurerad (UFW)
- [ ] PostgreSQL installerad
- [ ] Database & user skapad
- [ ] Nginx installerad

## Deployment Steps

1. **Upload filer** (via scp eller git)
2. **Skapa .env** från .env.production.template
3. **Install Python dependencies**: `pip install -r requirements.txt`
4. **Install Node dependencies**: `npm install`
5. **Build Tailwind**: `npm run build`
6. **Collect static**: `python manage.py collectstatic --noinput`
7. **Migrate database**: `python manage.py migrate`
8. **Create superuser**: `python manage.py createsuperuser`
9. **Setup Gunicorn** service
10. **Setup Nginx** config
11. **Test**: Besök http://DIN_IP

## Post-deployment

- [ ] Testa alla sidor fungerar
- [ ] Testa admin-panel: http://IP/admin
- [ ] Testa kontaktformulär
- [ ] Logga in och lägg till innehåll
- [ ] Setup backup-rutin
- [ ] Dokumentera admin-lösenord säkert

## För framtiden

När domän är klar:
1. Peka DNS A-record till Linode IP
2. Uppdatera ALLOWED_HOSTS i .env
3. Setup SSL med Let's Encrypt: `sudo certbot --nginx -d harpans.se -d www.harpans.se`
4. Aktivera SSL-settings i production.py

## Troubleshooting

**500 Error:**
```bash
sudo journalctl -u gunicorn -n 50
sudo tail -f /var/log/nginx/error.log
```

**Static files 404:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

**Database connection error:**
- Kontrollera DB_PASSWORD i .env
- Test: `sudo -u postgres psql -d harpans_db -U harpans_user`
