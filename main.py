import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Mengambil token dari Environment Variable (Render), BUKAN ditulis langsung di sini
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hai! Bot FF siap. Kirim /cek [UID] buat ngetes.')

async def cek_akun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Kirim UID-nya ya. Contoh: /cek 123456789')
        return
    
    uid = context.args[0]
    await update.message.reply_text(f'Mencari data UID {uid}... (Fitur API menyusul)')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cek", cek_akun))
    print("Bot berjalan...")
    app.run_polling()
