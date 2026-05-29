import requests
import time
from datetime import datetime

# ==============================
# إعدادات البوت - لا تغيّرها
# ==============================
TELEGRAM_TOKEN = "8968151497:AAG9Anu3L_wCu_G1_o03FBx6RtoTv6cEuuI"
CHAT_ID = "8219194461"

# ==============================
# إعدادات المراقبة - غيّرها حسب رغبتك
# ==============================

BUY_ALERT_PRICE  = 525.0.    AED/gm
SELL_ALERT_PRICE = 555.0.    AED/gm
CHECK_INTERVAL   = 60       # كم ثانية بين كل مراقبة (60 = دقيقة واحدة)

# ==============================
# متغيرات داخلية
# ==============================
last_price = None
buy_alert_sent  = False
sell_alert_sent = False


def get_gold_price():
    """جلب سعر الذهب الحالي"""
    try:
        # المصدر الأول
        r = requests.get("https://api.metals.live/v1/spot/gold", timeout=10)
        data = r.json()
        return float(data[0]["price"])
    except:
        pass
    try:
        # المصدر الثاني
        r = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/GC=F",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        data = r.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return float(price)
    except:
        return None


def send_telegram(message):
    """إرسال رسالة تيليغرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        print(f"✅ تم إرسال التنبيه: {message[:50]}...")
    except Exception as e:
        print(f"❌ فشل إرسال التنبيه: {e}")


def format_price(price):
    return f"{price:,.2f}"


def check_and_alert(price):
    global buy_alert_sent, sell_alert_sent, last_price
    now = datetime.now().strftime("%H:%M:%S")

    # تنبيه الشراء
    if price <= BUY_ALERT_PRICE and not buy_alert_sent:
        msg = (
            f"🟢 <b>تنبيه شراء الذهب!</b>\n\n"
            f"💰 السعر الحالي: <b>${format_price(price)}</b>\n"
            f"🎯 هدف الشراء: <b>${format_price(BUY_ALERT_PRICE)}</b>\n"
            f"⏰ الوقت: {now}\n\n"
            f"👉 افتح OGold الآن واشترِ!"
        )
        send_telegram(msg)
        buy_alert_sent = True

    # تنبيه البيع
    elif price >= SELL_ALERT_PRICE and not sell_alert_sent:
        msg = (
            f"🔴 <b>تنبيه بيع الذهب!</b>\n\n"
            f"💰 السعر الحالي: <b>${format_price(price)}</b>\n"
            f"🎯 هدف البيع: <b>${format_price(SELL_ALERT_PRICE)}</b>\n"
            f"⏰ الوقت: {now}\n\n"
            f"👉 افتح OGold الآن وبِع!"
        )
        send_telegram(msg)
        sell_alert_sent = True

    # إعادة تفعيل التنبيهات لو رجع السعر للمنتصف
    if BUY_ALERT_PRICE < price < SELL_ALERT_PRICE:
        buy_alert_sent  = False
        sell_alert_sent = False

    last_price = price


def main():
    print("=" * 40)
    print("🏅 OGold Bot - مراقب سعر الذهب")
    print("=" * 40)
    print(f"📈 سعر الشراء المستهدف : ${format_price(BUY_ALERT_PRICE)}")
    print(f"📉 سعر البيع المستهدف  : ${format_price(SELL_ALERT_PRICE)}")
    print(f"⏱  كل {CHECK_INTERVAL} ثانية")
    print("=" * 40)

    # رسالة بدء
    send_telegram(
        "🤖 <b>OGold Bot بدأ يعمل!</b>\n\n"
        f"📈 سعر الشراء: <b>${format_price(BUY_ALERT_PRICE)}</b>\n"
        f"📉 سعر البيع: <b>${format_price(SELL_ALERT_PRICE)}</b>\n"
        f"⏱ يراقب كل {CHECK_INTERVAL} ثانية\n\n"
        "سأُنبهك فور وصول السعر لهدفك ✅"
    )

    while True:
        price = get_gold_price()
        now = datetime.now().strftime("%H:%M:%S")

        if price:
            print(f"[{now}] سعر الذهب: ${format_price(price)}")
            check_and_alert(price)
        else:
            print(f"[{now}] ⚠️ فشل جلب السعر، سأحاول مجدداً...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
