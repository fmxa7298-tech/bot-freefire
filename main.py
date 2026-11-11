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
        # Pakai API Publik Gratis (Tanpa API Key)
        # API ini dari komunitas Vreden (lumayan stabil buat cek profile FF)
        url = f"https://api.vreden.my.id/api/ff?id={uid}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Cek status response dari API
            if data.get("status") == True or data.get("result"):
                result = data.get("result", {})
                
                # Ekstrak data
                nama = result.get("nickname", "Unknown")
                rank = result.get("rank", "Unranked")
                level = result.get("level", "N/A")
                
                reply_text = (
                    f"🎮 *INFO AKUN FREE FIRE*\n\n"
                    f"👤 Nickname: *{nama}*\n"
                    f"🏅 Level: *{level}*\n"
                    f"🏆 Rank: *{rank}*\n"
                    f"🆔 UID: `{uid}`\n"
                )
                await msg.edit_text(reply_text, parse_mode='Markdown')
            else:
                await msg.edit_text(f"❌ UID `{uid}` tidak ditemukan atau belum pernah login.")
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
