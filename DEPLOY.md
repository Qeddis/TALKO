# راهنمای Deploy ربات TALKO

این سند مرحله‌به‌مرحله نحوه راه‌اندازی ربات چت ناشناس TALKO روی سرور را توضیح می‌دهد.

---

## پیش‌نیازها

- Python 3.11 یا بالاتر
- توکن ربات از [@BotFather](https://t.me/BotFather)
- آیدی عددی تلگرام خودت (برای ADMIN_IDS)

---

## ۱. تنظیم محلی (تست)

```bash
# کلون پروژه
git clone <repo-url>
cd TALKO

# محیط مجازی
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# کپی تنظیمات
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac
```

فایل `.env` را ویرایش کن:

```env
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=987654321
VIP_COIN_PRICE=100
VIP_STARS_PRICE=50
STARTER_COINS=20
SUPPORT_USERNAME=YourSupportBot
```

اجرا:

```bash
python bot.py
```

---

## ۲. Deploy روی VPS (Ubuntu)

### نصب Python و وابستگی‌ها

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

git clone <repo-url> /opt/talko
cd /opt/talko

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### فایل `.env`

```bash
nano /opt/talko/.env
```

محتوا را مثل بخش بالا پر کن.

### سرویس systemd (اجرای دائمی)

```bash
sudo nano /etc/systemd/system/talko.service
```

```ini
[Unit]
Description=TALKO Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/talko
ExecStart=/opt/talko/venv/bin/python bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable talko
sudo systemctl start talko
sudo systemctl status talko
```

لاگ:

```bash
journalctl -u talko -f
```

---

## ۳. Deploy روی Railway

1. پروژه را به GitHub push کن
2. در [railway.app](https://railway.app) پروژه جدید بساز
3. **Deploy from GitHub** را انتخاب کن
4. در **Variables** این‌ها را اضافه کن:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `VIP_COIN_PRICE`, `VIP_STARS_PRICE`, `STARTER_COINS`
5. Railway از `Procfile` استفاده می‌کند:

```
worker: python bot.py
```

6. Deploy را بزن — ربات باید آنلاین شود

> **نکته:** SQLite روی Railway با restart ممکن است پاک شود. برای production از PostgreSQL استفاده کن (بخش ۶).

---

## ۴. Deploy روی Render

1. در [render.com](https://render.com) **Background Worker** بساز
2. ریپو GitHub را وصل کن
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python bot.py`
5. Environment Variables را مثل `.env` پر کن

---

## ۵. فعال‌سازی پرداخت استار (VIP)

1. در @BotFather → ربات → **Payments** → **Telegram Stars** را فعال کن
2. `VIP_STARS_PRICE=50` در `.env` (50 استار)
3. برای غیرفعال کردن: `VIP_STARS_PRICE=0`

---

## ۶. PostgreSQL (پیشنهادی برای Production)

SQLite برای تست خوب است؛ روی سرور واقعی PostgreSQL پایدارتر است.

`.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/talko
```

در `database/db.py` خط `DATABASE_URL` را از env بخوان:

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{BASE_DIR}/bot.db",
)
```

و به `requirements.txt` اضافه کن:

```
asyncpg
```

---

## ۷. دستورات ادمین

| دستور | کار |
|--------|-----|
| `/admin` | پنل ادمین |
| `/stats` | آمار کاربران |
| `/ban <id>` | مسدود کردن |
| `/unban <id>` | رفع مسدودی |
| `/setvip <id>` | فعال VIP |
| `/coins <id> <amount>` | افزودن سکه |
| `/broadcast <متن>` | پیام همگانی |
| `/deploy` | خلاصه راهنمای deploy |

---

## ۸. عیب‌یابی

| مشکل | راه‌حل |
|------|--------|
| `BOT_TOKEN is not set` | `.env` را چک کن |
| ربات جواب نمی‌دهد | `systemctl status talko` یا لاگ Railway |
| VIP استار کار نمی‌کند | Stars در BotFather فعال باشد |
| دیتابیس خالی شد | از PostgreSQL + backup استفاده کن |
| Conflict polling | فقط یک instance ربات اجرا شود |

---

## ۹. امنیت

- `.env` را **هرگز** commit نکن (در `.gitignore` است)
- `ADMIN_IDS` را فقط با آیدی خودت پر کن
- توکن لو رفت → در BotFather **Revoke** کن

---

## ۱۰. آپدیت ربات

```bash
cd /opt/talko
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart talko
```

---

ساخته شده برای **TALKO** — چت ناشناس تلگرام
