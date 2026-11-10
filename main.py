import os
import logging
import threading
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

# Inisialisasi Client Free Fire (Default Region ID)
# Lo bisa ganti "ID" jadi "SG", "MY", "BR", dll sesuai region akun FF lo
ff_client = FreeFireClient(server="ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hai! Bot FF siap. Kirim /cek [UID] buat ngecek akun.')

async def cek_akun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Kirim UID-nya ya. Contoh: /cek 123456789')
        return
    
    uid = context.args[0]
    msg = await update.message.reply_text(f'⏳ Sedang mencari data UID {uid}...')
    
    try:
        # Narik data dari API Free Fire
        data = ff_client.get_complete_player_data(uid)
        
        # Ambil info dasar dari data yang didapat
        basic_info = data.get('basicInfo', {})
        nickname = basic_info.get('nickname', 'Unknown')
        level = basic_info.get('level', 'Unknown')
        region = basic_info.get('region', 'ID')
        
        # Bikin teks balasan
        reply_text = (
            f"🎮 *INFO AKUN FREE FIRE*\n\n"
            f"👤 Nickname: *{nickname}*\n"
            f"🏅 Level: *{level}*\n"
            f"🌍 Region: *{region}*\n"
            f"🆔 UID: `{uid}`\n\n"
            f"_(Data Rank & Wishlist akan ditambahkan nanti)_"
        )
        
        await msg.edit_text(reply_text, parse_mode='Markdown')
        
    except Exception as e:
        await msg.edit_text(f"❌ Gagal mengambil data.\nPastikan UID benar atau API sedang down.\n\nError: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cek", cek_akun))
    print("Bot berjalan...")
    app.run_polling()
