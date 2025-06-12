
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7645213770:AAFz5kM6Uh-6tfGPmRGewdCJbcv7GwuQeGM"
ADMIN_ID = 6440597747
API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9..."

logging.basicConfig(level=logging.INFO)

BASE_URL = "https://5sim.net/v1/user"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا البوت مخصص للاستخدام الخاص فقط.")
        return

    keyboard = [
        [InlineKeyboardButton("📞 رقم جزائري", callback_data='algeria')],
        [InlineKeyboardButton("🌍 دولة أخرى", callback_data='other')]
    ]
    await update.message.reply_text("👋 اختر الدولة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    country = query.data

    if country == "other":
        await query.edit_message_text("🌍 الدعم الحالي فقط للجزائر. سيتم التوسعة لاحقًا.")
        return

    try:
        response = requests.get(
            "https://5sim.net/v1/user/buy/activation/any/al/jdmarket",
            headers=HEADERS
        )
        data = response.json()

        phone = data["phone"]
        sms_id = data["id"]
        await query.edit_message_text(f"📱 الرقم: `{phone}`\n⌛️ انتظر استلام الكود...", parse_mode="Markdown")

        for _ in range(30):
            sms_check = requests.get(f"{BASE_URL}/check/{sms_id}", headers=HEADERS).json()
            if sms_check.get("sms"):
                code = sms_check["sms"][0]["code"]
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ الكود المستلم: `{code}`", parse_mode="Markdown")
                break
            await asyncio.sleep(5)
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text="⚠️ لم يتم استلام الكود بعد 30 ثانية.")

    except Exception as e:
        await query.edit_message_text(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    import asyncio
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(telegram.ext.CallbackQueryHandler(button_handler))
    app.run_polling()
