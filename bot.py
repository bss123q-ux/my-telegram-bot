import os
import threading
from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- 1. إعداد خادم الويب (لمنع البوت من النوم في Render) ---
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. قراءة التوكن بأمان من الإعدادات ---
TOKEN = os.environ.get("TOKEN")

# --- 3. دالة إنشاء الأزرار ---
def get_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💚 تجميع نقاط", callback_data="collect", style="success"),
            InlineKeyboardButton("🐉 رصيد حسابك: 0 كوكيز", callback_data="balance", style="danger")
        ],
        [
            InlineKeyboardButton("🔔 معلوماتي", callback_data="info", style="danger"),
            InlineKeyboardButton("💸 تحويل نقاط", callback_data="transfer", style="success")
        ],
        [
            InlineKeyboardButton("🎁 استبدال النقاط مقابل هدية", callback_data="redeem", style="primary")
        ],
        [
            InlineKeyboardButton("🏵️ شروط الاستخدام", callback_data="terms", style="danger"),
            InlineKeyboardButton("📝 تعليمات", callback_data="instructions", style="danger")
        ],
        [
            # ضع رابط قناتك هنا بدل الرابط التجريبي
            InlineKeyboardButton("🤖 قنوات البوت", url="https://t.me/telegram", style="primary"),
            InlineKeyboardButton("🔹 تسليم الطلبات", callback_data="submit", style="primary")
        ],
        [
            InlineKeyboardButton("🟢 طلبات مكتملة", callback_data="completed", style="danger")
        ],
        [
            # ضع رابط الشحن هنا بدل الرابط التجريبي
            InlineKeyboardButton("💳 شحن تلقائي", url="https://t.me/telegram", style="success")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- 4. أمر البدء /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "أهلاً بك في متجرنا\n\n"
        "🆔 ايديك: `{}`\n"
        "🍪 عدد كوكيز: [ 0 ]".format(update.effective_user.id)
    )
    await update.message.reply_text(text, reply_markup=get_keyboard(), parse_mode="Markdown")

# --- 5. معالجة ضغطات الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # إجباري لمنع الزر من الدوران

    if query.data == "collect":
        await query.edit_message_text("✅ تم تجميع النقاط بنجاح! (هنا تضيف كود زيادة النقاط)")
    elif query.data == "balance":
        await query.edit_message_text("💰 رصيدك الحالي: 0 كوكيز")
    elif query.data == "info":
        await query.edit_message_text("👤 معلوماتك:\nالاسم: {}\nالايدي: {}".format(query.from_user.first_name, query.from_user.id))
    elif query.data == "transfer":
        await query.edit_message_text("💸 لتحويل النقاط، أرسل الأمر /transfer")
    elif query.data == "redeem":
        await query.edit_message_text("🎁 اختر الهدية التي تريد استبدالها (هنا تضيف قائمة الهدايا)")
    elif query.data == "terms":
        await query.edit_message_text("🏵️ شروط الاستخدام:\n1. ممنوع الغش\n2. ممنوع التخريب")
    elif query.data == "instructions":
        await query.edit_message_text("📝 التعليمات:\nاضغط على 'تجميع نقاط' لجمع النقاط يومياً.")
    elif query.data == "submit":
        await query.edit_message_text("🔹 لتسليم طلبك، اكتب طلبك هنا وسيتم مراجعته.")
    elif query.data == "completed":
        await query.edit_message_text("🟢 لا توجد طلبات مكتملة حالياً.")

# --- 6. التشغيل الرئيسي ---
if __name__ == "__main__":
    # تشغيل Flask في الخلفية لمنع النوم
    threading.Thread(target=run_flask, daemon=True).start()
    
    # تشغيل بوت التيليجرام
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    
    print("البوت شغال الآن...")
    telegram_app.run_polling()