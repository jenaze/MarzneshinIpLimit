# راهنمای سریع رفع مشکل DNS / Quick DNS Fix Guide

## 🚨 مشکل شما / Your Problem

```
ERROR - An unexpected error occurred: [Errno -3] Temporary failure in name resolution
```

این خطا به دلیل عدم دسترسی به سرورهای تلگرام است (احتمالاً به دلیل فیلتر بودن).

This error is due to inability to access Telegram servers (likely due to filtering).

---

## ⚡ راه حل سریع / Quick Solution

### گام 1: ویرایش فایل config.json

```bash
nano /opt/marzneshiniplimit/config.json
```

### گام 2: اضافه کردن پروکسی

یکی از این موارد را اضافه کنید (بعد از `"BOT_TOKEN"`):

Add one of these (after `"BOT_TOKEN"`):

```json
"PROXY_URL": "http://your-proxy-ip:port",
```

یا برای SOCKS5:

Or for SOCKS5:

```json
"PROXY_URL": "socks5://your-proxy-ip:port",
```

مثال کامل:

Complete example:

```json
{
    "GENERAL_LIMIT":1,
    "BOT_TOKEN": "your_actual_bot_token_here",
    "PROXY_URL": "socks5://127.0.0.1:1080",
    "ADMINS":[112234455],
    ...
}
```

### گام 3: راه‌اندازی مجدد

```bash
cd /opt/marzneshiniplimit
docker-compose down
docker-compose up -d
```

### گام 4: بررسی لاگ

```bash
docker-compose logs -f
```

باید پیام زیر را ببینید:

You should see:

```
Telegram bot started successfully!
```

---

## 🔧 اگر پروکسی ندارید / If You Don't Have Proxy

### روش 1: استفاده از شکن موجود روی سرور

اگر روی سرورتان شکن (مثلاً Xray) نصب است:

If you have a VPN (like Xray) on your server:

```json
"PROXY_URL": "socks5://127.0.0.1:1080",
```

(پورت بسته به تنظیمات شکن شما متفاوت است)

(Port depends on your VPN settings)

### روش 2: تغییر DNS سیستم

```bash
# تغییر موقت DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf

# راه‌اندازی مجدد Docker
cd /opt/marzneshiniplimit
docker-compose restart
```

### روش 3: نصب یک پروکسی ساده

```bash
# نصب Dante SOCKS proxy
sudo apt-get update
sudo apt-get install dante-server -y

# پیکربندی (نیاز به تنظیمات بیشتر دارد)
```

---

## ✅ تأیید رفع مشکل / Verify Fix

پس از هر تغییر، این دستورات را اجرا کنید:

After each change, run these commands:

```bash
# 1. بررسی وضعیت کانتینر / Check container status
docker ps

# 2. بررسی لاگ‌ها / Check logs
docker-compose logs --tail=50

# 3. اگر خطا ادامه دارد / If error continues
docker-compose logs | grep -i error
```

---

## 📝 توجه / Note

اگر `BOT_TOKEN` شما هنوز `"BotToken"` است، باید توکن واقعی ربات تلگرام خود را از [@BotFather](https://t.me/BotFather) دریافت کرده و جایگزین کنید.

If your `BOT_TOKEN` is still `"BotToken"`, you need to get your actual bot token from [@BotFather](https://t.me/BotFather) and replace it.

---

## 🆘 کمک بیشتر / More Help

برای راهنمای کامل، فایل `TROUBLESHOOTING.md` را مطالعه کنید.

For complete guide, read `TROUBLESHOOTING.md` file.

