import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import numexpr as ne
import sympy as sp

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
    teks = (
        "🧮 *AI Kalkulator Aktif!*\n\n"
        "Kirim soal matematika langsung, atau pakai command.\n"
        "Contoh:\n"
        "`/hitung 2 + 2 * 5`\n"
        "`/hitung (10 ** 3) / 2`\n"
        "`/hitung sqrt(144) + 5`\n\n"
        "Atau lo bisa nanya persamaan pakai /persamaan (misal: `/persamaan x**2 - 4 = 0`)"
    )
    await update.message.reply_text(teks, parse_mode='Markdown')

async def hitung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Kirim angkanya dong. Contoh: `/hitung 5 * 8`', parse_mode='Markdown')
        return
    
    # Gabungin semua argumen jadi satu string
    soal = " ".join(context.args)
    msg = await update.message.reply_text('⏳ Menghitung...')
    
    try:
        # 1. Coba pakai numexpr (khusus matematika dasar & cepat)
        try:
            hasil = ne.evaluate(soal)
            await msg.edit_text(f"✅ *Hasil:*\n`{soal} = {hasil}`", parse_mode='Markdown')
            return
        except Exception:
            pass # Kalau gagal, lanjut ke sympy
            
        # 2. Kalau numexpr gagal, pakai sympy (bisa handle akar, sin, cos, dll)
        hasil_sympy = sp.sympify(soal).evalf()
        await msg.edit_text(f"✅ *Hasil:*\n`{soal} = {hasil_sympy}`", parse_mode='Markdown')
        
    except Exception as e:
        await msg.edit_text(f"❌ Waduh, formatnya salah atau nggak bisa dihitung.\nError: {str(e)}")

async def persamaan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Contoh: `/persamaan x**2 - 4 = 0`', parse_mode='Markdown')
        return

    soal = " ".join(context.args)
    msg = await update.message.reply_text('⏳ Mencari nilai X...')

    try:
        # Parsing persamaan pakai sympy
        if "=" in soal:
            kiri, kanan = soal.split("=")
            persamaan_math = sp.Eq(sp.sympify(kiri), sp.sympify(kanan))
        else:
            persamaan_math = sp.sympify(soal)

        # Cari solusinya
        solusi = sp.solve(persamaan_math)
        await msg.edit_text(f"✅ *Solusi:*\n`{soal}`\n\nX = `{solusi}`", parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f"❌ Gagal menyelesaikan persamaan.\nError: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hitung", hitung))
    app.add_handler(CommandHandler("persamaan", persamaan))
    
    print("Bot Kalkulator berjalan...")
    app.run_polling()
