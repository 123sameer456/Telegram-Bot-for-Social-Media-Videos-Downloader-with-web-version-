
import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from telegram.request import HTTPXRequest

# Set up Telegram Bot Token
BOT_TOKEN = ""

# Create a folder to store downloads
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Function to detect platform from URL
def detect_platform(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "facebook.com" in url or "fb.watch" in url:
        return "facebook"
    elif "instagram.com" in url or "instagr.am" in url:
        return "instagram"
    elif "x.com" in url or "twitter.com" in url:
        return "twitter"
    else:
        return "unknown"

# Function to download video asynchronously
async def download_video(url):
    platform = detect_platform(url)
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'quiet': True,
        'merge_output_format': 'mp4',
    }

    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)
        return filename
    except Exception as e:
        print(f"Download error: {str(e)}")
        return f"Error: {str(e)}"

# Function to handle received messages
async def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    
    await update.message.reply_text("⏳ Downloading your video... Please wait.")

    # Download video
    video_path = await download_video(url)

    if isinstance(video_path, str) and os.path.exists(video_path):
        # Send the video file to user
        try:
            with open(video_path, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file)
            
            os.remove(video_path)  # Clean up after sending
        except Exception as e:
            print(f"Error sending video: {str(e)}")
            await update.message.reply_text(f"⚠️ Error sending video: {str(e)}")
    else:
        await update.message.reply_text("⚠️ Failed to download video. Please check the link.")

# Start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "👋 Welcome to the Media Downloader Bot!\n\n"
        "Send me a link from YouTube, TikTok, Facebook, Instagram, or Twitter, "
        "and I'll download and send you the video."
    )

# Start the bot
def main():
    # Configure connection with higher timeouts and optional proxy
    # Uncomment and modify the proxy line below if you're behind a proxy/firewall
    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=30.0,
        write_timeout=30.0,
        connect_timeout=30.0,
        # proxy="http://your-proxy-url:port"  # Uncomment and set your proxy if needed
    )
    
    # Initialize the application with custom request parameters
    app = Application.builder().token(BOT_TOKEN).request(request).build()

    # Handle messages (URLs sent by users)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add command handlers
    app.add_handler(CommandHandler("start", start))

    # Start polling with a longer polling timeout
    print("🤖 Bot is running...")
    try:
        app.run_polling(poll_interval=3.0, timeout=30)
    except Exception as e:
        print(f"Error in polling: {str(e)}")

if __name__ == '__main__':
    # Import CommandHandler here to avoid circular import issue
    from telegram.ext import CommandHandler
    main()