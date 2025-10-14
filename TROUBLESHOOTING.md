# راهنمای عیب‌یابی / Troubleshooting Guide

## خطای DNS Resolution (Temporary failure in name resolution)

### علت مشکل / Problem Cause

این خطا زمانی رخ می‌دهد که ربات تلگرام نمی‌تواند نام دامنه‌ها را به آی‌پی تبدیل کند. این مشکل معمولاً در کشورهایی که تلگرام فیلتر شده یا زمانی که DNS به درستی پیکربندی نشده، رخ می‌دهد.

This error occurs when the Telegram bot cannot resolve domain names to IP addresses. This is common in countries where Telegram is blocked or when DNS is not properly configured.

---

## راه حل‌ها / Solutions

### راه حل 1: استفاده از پروکسی / Solution 1: Use Proxy

اگر تلگرام در کشور شما فیلتر است، باید از پروکسی استفاده کنید:

If Telegram is blocked in your country, you need to use a proxy:

1. فایل `/opt/marzneshiniplimit/config.json` را ویرایش کنید:
   Edit the file `/opt/marzneshiniplimit/config.json`:

```bash
nano /opt/marzneshiniplimit/config.json
```

2. فیلد `PROXY_URL` را اضافه یا به‌روزرسانی کنید:
   Add or update the `PROXY_URL` field:

```json
{
    "PROXY_URL": "http://your-proxy-server:port",
    ...
}
```

یا برای پروکسی SOCKS5:
Or for SOCKS5 proxy:

```json
{
    "PROXY_URL": "socks5://your-proxy-server:port",
    ...
}
```

3. کانتینر را مجدداً راه‌اندازی کنید:
   Restart the container:

```bash
cd /opt/marzneshiniplimit
docker-compose down
docker-compose up -d
```

---

### راه حل 2: بررسی DNS سیستم / Solution 2: Check System DNS

1. بررسی DNS فعلی:
   Check current DNS:

```bash
cat /etc/resolv.conf
```

2. تست دسترسی به سرورهای تلگرام:
   Test access to Telegram servers:

```bash
nslookup api.telegram.org
ping api.telegram.org
```

3. اگر DNS کار نمی‌کند، از DNS عمومی استفاده کنید:
   If DNS doesn't work, use public DNS:

```bash
# موقت / Temporary
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
echo "nameserver 4.2.2.4" | sudo tee -a /etc/resolv.conf

# دائم / Permanent (Ubuntu/Debian)
sudo nano /etc/systemd/resolved.conf
# اضافه کنید / Add:
# DNS=8.8.8.8 1.1.1.1 4.2.2.4
# FallbackDNS=8.8.4.4

sudo systemctl restart systemd-resolved
```

---

### راه حل 3: استفاده از Bridge Network Mode / Solution 3: Use Bridge Network Mode

اگر `host` network mode مشکل دارد، می‌توانید به bridge تغییر دهید:

If `host` network mode has issues, you can switch to bridge:

1. فایل `docker-compose.yml` را ویرایش کنید:
   Edit `docker-compose.yml`:

```yaml
services:
  marzneshin_ip_limit:
    image: ghcr.io/jenaze/marzneshiniplimit:latest
    restart: always
    environment:
      PORT: 6284
    # network_mode: host را حذف کنید و ports اضافه کنید
    # Remove network_mode: host and add ports
    ports:
      - "6284:6284"
    dns:
      - 8.8.8.8
      - 8.8.4.4
      - 1.1.1.1
    volumes:
      - /opt/marzneshiniplimit/config.json:/marzneshiniplimitcode/config.json
      - /opt/marzneshiniplimit/logs:/marzneshiniplimitcode/logs
    healthcheck:
      test: ["CMD", "python", "/marzneshiniplimitcode/health_check.py"]
      interval: 30s
      timeout: 10s
      retries: 3
```

2. مجدداً راه‌اندازی کنید:
   Restart:

```bash
docker-compose down
docker-compose up -d
```

---

### راه حل 4: بررسی لاگ‌ها / Solution 4: Check Logs

برای دیدن لاگ‌های دقیق‌تر:
To see detailed logs:

```bash
docker-compose logs -f marzneshin_ip_limit
```

یا:
Or:

```bash
docker logs -f marzneshin_ip_limit-marzneshin_ip_limit-1
```

---

### راه حل 5: استفاده از VPN روی سرور / Solution 5: Use VPN on Server

اگر هیچ‌کدام از راه‌حل‌های بالا کار نکرد، می‌توانید یک VPN روی سرور نصب کنید:

If none of the above solutions work, you can install a VPN on the server:

1. نصب Outline VPN یا WireGuard
   Install Outline VPN or WireGuard

2. اتصال به VPN
   Connect to VPN

3. سپس Docker را مجدداً راه‌اندازی کنید
   Then restart Docker

---

## بررسی وضعیت / Status Check

پس از اعمال هر راه‌حل، وضعیت را بررسی کنید:

After applying any solution, check the status:

```bash
# بررسی لاگ‌ها / Check logs
docker-compose logs -f

# بررسی وضعیت کانتینر / Check container status
docker ps

# بررسی health / Check health
docker inspect marzneshin_ip_limit-marzneshin_ip_limit-1 | grep -A 10 Health
```

اگر پیام "Telegram bot started successfully!" را دیدید، مشکل حل شده است!

If you see "Telegram bot started successfully!", the problem is solved!

---

## پشتیبانی / Support

در صورت ادامه مشکل:

If the problem persists:

1. لاگ کامل را ذخیره کنید: `docker-compose logs > logs.txt`
   Save complete logs: `docker-compose logs > logs.txt`

2. فایل `config.json` خود را بررسی کنید (بدون افشای اطلاعات حساس)
   Check your `config.json` (without revealing sensitive information)

3. با توسعه‌دهنده تماس بگیرید
   Contact the developer

---

## تغییرات اخیر / Recent Changes

فایل‌های زیر به‌روزرسانی شده‌اند تا مشکل DNS و پروکسی را حل کنند:

The following files have been updated to fix DNS and proxy issues:

- ✅ `telegram_bot/bot.py` - افزودن پشتیبانی پروکسی و timeout
- ✅ `run_telegram.py` - بهبود error handling و retry logic
- ✅ `docker-compose.yml` - افزودن DNS servers
- ✅ `config.json` - افزودن فیلد PROXY_URL
- ✅ `config.json.example` - به‌روزرسانی مثال
- ✅ `README.md` - افزودن بخش Troubleshooting

