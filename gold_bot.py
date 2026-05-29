import requests
import time
from datetime import datetime

# ==============================
# إعدادات البوت
# ==============================
TELEGRAM_TOKEN = "8968151497:AAG9Anu3L_wCu_G1_o03FBx6RtoTv6cEuuI"
CHAT_ID = "8219194461"

# ==============================
# أسعار المراقبة بالدرهم للغرام
# ==============================
BUY_ALERT_PRICE  = 525.0   # اشترِ إذا نزل لهذا السعر
SELL_ALERT_PRICE = 555.0   # بِع إذا صعد لهذا السعر
CHECK_INTERVAL   = 60      # كل 60 ثانية

# ==============================
# متغيرات داخلية
# ==============================
last_price = None
buy_alert_sent  = False
sell_alert_sent = False
silver_buy_sent  = False
silver_sell_sent = False
# أسعار الفضة بالدرهم للغرام
SILVER_BUY_PRICE  = 8.90
SILVER_SELL_PRICE = 9.30

def get_gold_price_aed():
    """جلب سعر الذهب بالدرهم للغرام"""
    try:
        # جلب سعر الذهب بالدولار للأوقية
        r = requests.get("https://api.metals.live/v1/spot/gold", timeout=10)
        data = r.json()
        usd_per_oz = float(data[0]["price"])
        # تحويل لدرهم/غرام: 1 أوقية = 31.1035 غرام، 1 دولار = 3.6725 درهم
        aed_per_gram = (usd_per_oz / 31.1035) * 3.6725
        return round(aed_per_gram, 2)
    except:
        pass
    try:
        r = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/GC=F",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        data = r.json()
        usd_per_oz = float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
        aed_per_gram = (usd_per_oz / 31.1035) * 3.6725
        return round(aed_per_gram, 2)
    except:
        return None

return None

def get_silver_price_aed():
    try:
        r = requests.get("https://api.metals.live/v1/spot/silver", timeout=10)
        data = r.json()
        usd_per_oz = float(data[0]["price"])
        aed_per_gram = (usd_per_oz / 31.1035) * 3.6725
        return round(aed_per_gram, 2)
    except:
        return None
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        print(f"✅ تم الإرسال")
    except Exception as e:
        print(f"❌ فشل الإرسال: {e}")


def check_and_alert(price):
    global buy_alert_sent, sell_alert_sent
    now = datetime.now().strftime("%H:%M:%S")

    if price <= BUY_ALERT_PRICE and not buy_alert_sent:
        msg = (
            f"🟢 <b>تنبيه شراء الذهب!</b>\n\n"
            f"💰 السعر الحالي: <b>{price} درهم/غرام</b>\n"
            f"🎯 هدف الشراء: <b>{BUY_ALERT_PRICE} درهم/غرام</b>\n"
            f"⏰ الوقت: {now}\n\n"
            f"👉 افتح OGold الآن واشترِ!"
        )
        send_telegram(msg)
        buy_alert_sent = True

    elif price >= SELL_ALERT_PRICE and not sell_alert_sent:
        msg = (
            f"🔴 <b>تنبيه بيع الذهب!</b>\n\n"
            f"💰 السعر الحالي: <b>{price} درهم/غرام</b>\n"
            f"🎯 هدف البيع: <b>{SELL_ALERT_PRICE} درهم/غرام</b>\n"
            f"⏰ الوقت: {now}\n\n"
            f"👉 افتح OGold الآن وبِع!"
        )
        send_telegram(msg)
        sell_alert_sent = True

    if BUY_ALERT_PRICE < price < SELL_ALERT_PRICE:
        buy_alert_sent  = False
        sell_alert_sent = False


def main():
    print("🏅 OGold Bot - مراقب سعر الذهب بالدرهم")
    print(f"📈 سعر الشراء: {BUY_ALERT_PRICE} درهم/غرام")
    print(f"📉 سعر البيع: {SELL_ALERT_PRICE} درهم/غرام")

    send_telegram(
        f"🤖 <b>OGold Bot بدأ يعمل!</b>\n\n"
        f"📈 سعر الشراء: <b>{BUY_ALERT_PRICE} درهم/غرام</b>\n"
        f"📉 سعر البيع: <b>{SELL_ALERT_PRICE} درهم/غرام</b>\n"
        f"⏱ يراقب كل {CHECK_INTERVAL} ثانية\n\n"
        f"✅ سأُنبهك فور وصول السعر لهدفك"
    )

    while True:
        price = get_gold_price_aed()
        now = datetime.now().strftime("%H:%M:%S")

        if price:
            print(f"[{now}] سعر الذهب: {price} درهم/غرام")
            check_and_alert(price)
            silver = get_silver_price_aed()
        if silver:
            print(f"[{now}] سعر الفضة: {silver} درهم/غرام")
            check_silver_alert(silver)
        else:
            print(f"[{now}] ⚠️ فشل جلب السعر...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
