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
REFERRAL_REWARD=10
REFERRAL_BONUS=10
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

## ۵. پرداخت استار (VIP)

**نیازی به تنظیم در BotFather نیست.** برخلاف پرداخت ریالی/ارزی، Stars با currency=`XTR` و `provider_token` خالی مستقیم کار می‌کند.

1. `VIP_STARS_PRICE=50` در `.env` (۵۰ استار)
2. برای غیرفعال کردن: `VIP_STARS_PRICE=0`
3. در ربات: `💎 VIP` → `⭐ خرید VIP با استار`

> اگر در BotFather بخش Payments فقط Stripe/YooKassa و... دیدی، طبیعی است — آن‌ها برای کالای فیزیکی است. Stars جداگانه فعال نمی‌شود.

### برداشت درآمد Stars

Stars دریافتی را از **Fragment** ([fragment.com](https://fragment.com)) به TON تبدیل کن. حداقل ۱۰۰۰ استار و ۲۱ روز انتظار لازم است.

---

## ۶. PostgreSQL (Production)

SQLite برای تست محلی خوب است. روی Railway/Render/VPS واقعی PostgreSQL پایدارتر است.

### Railway

1. در پروژه Railway یک **PostgreSQL** plugin اضافه کن
2. متغیر `DATABASE_URL` را کپی کن — اگر با `postgres://` شروع شد، در `.env` این‌طور بنویس:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/railway
```

> SQLAlchemy به `postgresql+asyncpg://` نیاز دارد (نه `postgres://`).

### VPS (Ubuntu)

```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE USER talko WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE talko OWNER talko;"
```

`.env`:

```env
DATABASE_URL=postgresql+asyncpg://talko:your_password@localhost:5432/talko
```

ربات در اولین اجرا جداول را خودکار می‌سازد.

---

## ۷. سیستم دعوت (Referral)

| متغیر | پیش‌فرض | معنی |
|--------|---------|------|
| `REFERRAL_REWARD` | 10 | سکه برای دعوت‌کننده |
| `REFERRAL_BONUS` | 10 | سکه اضافه برای کاربر جدید |

لینک دعوت: `https://t.me/YourBot?start=ref<telegram_id>`

کاربر از **👤 پروفایل → 🎁 دعوت دوستان** لینک خودش را می‌بیند.

---

## ۸. دستورات ادمین

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

## ۹. عیب‌یابی

| مشکل | راه‌حل |
|------|--------|
| `BOT_TOKEN is not set` | `.env` را چک کن |
| ربات جواب نمی‌دهد | `systemctl status talko` یا لاگ Railway |
| VIP استار کار نمی‌کند | `VIP_STARS_PRICE>0` باشد؛ نیازی به BotFather Payments نیست |
| دیتابیس خالی شد | از PostgreSQL + backup استفاده کن |
| Conflict polling | فقط یک instance ربات اجرا شود |

---

## ۱۰. امنیت

- `.env` را **هرگز** commit نکن (در `.gitignore` است)
- `ADMIN_IDS` را فقط با آیدی خودت پر کن
- توکن لو رفت → در BotFather **Revoke** کن

---

## ۱۱. آپدیت ربات

```bash
cd /opt/talko
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart talko
```

---

ساخته شده برای **TALKO** — چت ناشناس تلگرام
