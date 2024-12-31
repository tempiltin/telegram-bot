import os
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot uchun foydalanuvchi avtorizatsiyasi (oddiy ro'yxat bilan)
AUTHORIZED_USERS = {}

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni boshlash xabari."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Assalomu alaykum, {user.mention_html()}! 👋\n"
        "Instagram va TikTok videolarini yuklash uchun avtorizatsiyadan o'ting.\n"
        "Foydalanish uchun /login buyrug'ini kiriting."
    )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini avtorizatsiyadan o'tkazadi."""
    user = update.effective_user
    user_id = user.id

    if user_id not in AUTHORIZED_USERS:
        AUTHORIZED_USERS[user_id] = user.full_name
        await update.message.reply_text(f"Avtorizatsiya muvaffaqiyatli! Xush kelibsiz, {user.full_name}!")
    else:
        await update.message.reply_text("Siz allaqachon avtorizatsiyadan o'tgansiz.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instagram yoki TikTok videolarini yuklaydi."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Avval avtorizatsiyadan o'ting. /login buyrug'ini kiriting.")
        return

    url = update.message.text.strip()
    if not url.startswith(("https://www.instagram.com", "https://www.tiktok.com")):
        await update.message.reply_text("Faqat Instagram yoki TikTok URL manzillarini kiriting.")
        return

    await update.message.reply_text("Videoni yuklash jarayoni boshlandi... ⏳")

    try:
        video_url = get_video_url(url)  # Video yuklash uchun yordamchi funksiya
        if video_url:
            video_data = requests.get(video_url)
            await update.message.reply_video(video=video_data.content)
        else:
            await update.message.reply_text("Videoni yuklab bo'lmadi. URL manzilni tekshirib qaytadan kiriting.")
    except Exception as e:
        await update.message.reply_text(f"Xato yuz berdi: {e}")

def get_video_url(url):
    """Instagram yoki TikTok videolari uchun yuklash URL-ni olish."""
    if "instagram.com" in url:
        api_url = f"https://igdownloader.io/api/video?url={url}"
    elif "tiktok.com" in url:
        api_url = f"https://tiktokdownloader.io/api/video?url={url}"
    else:
        return None

    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get("download_url")  # Mos keladigan API-da 'download_url' bo'lishi kerak
    return None

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Noma'lum buyruqlar uchun."""
    await update.message.reply_text("Noma'lum buyruq. Foydalanish uchun /start buyrug'ini kiriting.")

def main():
    """Botni ishga tushirish."""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
