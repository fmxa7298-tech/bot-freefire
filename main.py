import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- DUMMY SERVER UNTUK RENDER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()
# ---------------------------------

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Ambil token dari Environment Variable
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
    # Jalanin server palsu di background
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # Jalanin Bot Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cek", cek_akun))
    print("Bot berjalan...")
    app.run_polling()
