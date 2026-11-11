import os
import logging
import threading
import requests
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
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hai! Kirim /cek [UID] buat ngecek akun FF lo.\nContoh: /cek 14554842325')

async def cek_akun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Kirim UID-nya ya. Contoh: /cek 14554842325')
        return
    
    uid = context.args[0]
    msg = await update.message.reply_text(f'⏳ Sedang mencari data UID {uid}...')
    
    try:
        # API Gratis dari BIELVENDAs (Region ID)
        url = f"https://free-ff-api-src-5plp.onrender.com/api/v1/account?region=ID&uid={uid}"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Cek apakah data basicInfo ada
            if "basicInfo" in data:
                basic_info = data["basicInfo"]
                nama = basic_info.get("nickname", "Unknown")
                level = basic_info.get("level", "N/A")
                rank = basic_info.get("rank", "N/A")
                region = basic_info.get("region", "ID")
                
                reply_text = (
                    f"🎮 *INFO AKUN FREE FIRE*\n\n"
                    f"👤 Nickname: *{nama}*\n"
                    f"🏅 Level: *{level}*\n"
                    f"🏆 Rank: *{rank}*\n"
                    f"🌍 Region: *{region}*\n"
                    f"🆔 UID: `{uid}`\n"
                )
                await msg.edit_text(reply_text, parse_mode='Markdown')
            else:
                await msg.edit_text(f"❌ UID `{uid}` tidak ditemukan atau data tidak lengkap.")
        else:
            await msg.edit_text(f"❌ Gagal mengambil data. Server API error (Status: {response.status_code}).")
            
    except Exception as e:
        await msg.edit_text(f"❌ Gagal mengambil data. Error: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cek", cek_akun))
    print("Bot berjalan...")
    app.run_polling()
