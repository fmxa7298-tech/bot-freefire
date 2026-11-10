import os
import logging
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from freefire_api import FreeFireClient

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
TOKEN = os.environ.get("BOT_TOKEN")

# Inisialisasi client Free Fire (default region ID)
ff_client = FreeFireClient(server="ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hai! Kirim /cek [UID] buat ngecek akun FF lo.\nContoh: /cek 17590000040')

async def cek_akun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Kirim UID-nya ya. Contoh: /cek 17590000040')
        return
    
    uid = context.args[0]
    msg = await update.message.reply_text(f'⏳ Sedang mencari data UID {uid}...')
    
    try:
        # Menggunakan library freefire-api untuk ambil profil
        profile = ff_client.get_player_profile(uid)
        
        # Ekstrak data dari respons library
        basic_info = profile.get('basicInfo', {})
        nickname = basic_info.get('nickname', 'Unknown')
        level = basic_info.get('level', 'N/A')
        rank = basic_info.get('rank', 'N/A')
        region = basic_info.get('region', 'ID')
        
        reply_text = (
            f"🎮 *INFO AKUN FREE FIRE*\n\n"
            f"👤 Nickname: *{nickname}*\n"
            f"🏅 Level: *{level}*\n"
            f"🏆 Rank: *{rank}*\n"
            f"🌍 Region: *{region}*\n"
            f"🆔 UID: `{uid}`\n\n"
            f"_(Data wishlist & senjata favorit menyusul)_"
        )
        await msg.edit_text(reply_text, parse_mode='Markdown')
        
    except Exception as e:
        await msg.edit_text(f"❌ Gagal mengambil data. Pastikan UID benar.\n\nError: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cek", cek_akun))
    print("Bot berjalan...")
    app.run_polling()
