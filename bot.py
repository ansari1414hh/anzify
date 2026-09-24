import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import requests
import base64

# Configurations
TELEGRAM_BOT_TOKEN = '8853127212:AAE3scQjdAMg3olGvSyQ3gC5LgdvOjCWrZ0'
GITHUB_TOKEN = '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'
OWNER = 'ansari1414hh'
REPO = 'anzify'
PATH = 'songs.json'

async def handle_song_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song_name = update.message.text
    await update.message.reply_text(f"Searching YouTube for '{song_name}'...")

    try:
        # Use yt-dlp to extract direct audio stream and metadata without external APIs
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': False,
            'default_search': 'ytsearch1'
        }

        audio_url = ""
        image = ""
        title = song_name

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song_name}", download=False)
            if 'entries' in info and info['entries']:
                video_info = info['entries'][0]
                title = video_info.get('title', song_name)
                audio_url = video_info.get('url', '')
                image = video_info.get('thumbnail', '')

        if not audio_url:
            await update.message.reply_text("Could not find a valid audio link for this song.")
            return

        await update.message.reply_text(f"Found: {title}. Updating GitHub...")

        # Update GitHub songs.json
        github_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"
        headers = {'Authorization': f'Bearer {GITHUB_TOKEN}'}
        
        get_res = requests.get(github_url, headers=headers)
        if get_res.status_code == 200:
            file_data = get_res.json()
            sha = file_data['sha']
            
            file_content_decoded = base64.b64decode(file_data['content']).decode('utf-8')
            try:
                current_content = json.loads(file_content_decoded)
            except:
                current_content = []
            
            # Append new song entry with the real direct audio stream link
            current_content.append({
                'title': title,
                'id': audio_url,
                'img': image
            })

            updated_content_base64 = base64.b64encode(json.dumps(current_content, indent=4).encode()).decode()
            put_payload = {
                'message': f'Add {title} via yt-dlp Bot',
                'content': updated_content_base64,
                'sha': sha
            }
            
            put_res = requests.put(github_url, headers=headers, json=put_payload)
            if put_res.status_code in [200, 201]:
                await update.message.reply_text(f"Success! '{title}' added to Anzify and ready to play.")
            else:
                await update.message.reply_text("Failed to update GitHub repository.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_song_name))
    print("Bot is running with yt-dlp integration...")
    app.run_polling()

if __name__ == '__main__':
    main()