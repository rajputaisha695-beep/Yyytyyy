import asyncio
import json
import os
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"
CHANNEL_ID = -1003550209252
ADMIN_ID = 8961906024  # 🔥 APNI ADMIN ID DALO (Apni Telegram User ID)

# Schedule file (bina database ke JSON me store)
SCHEDULE_FILE = "schedule.json"

# ---------- SCHEDULE FUNCTIONS ----------
def load_schedule():
    """Schedule load karo"""
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return {"posts": [], "daily_count": 1, "post_time": "07:00", "custom_message": "📌 Join our channel for more updates!"}

def save_schedule(data):
    """Schedule save karo"""
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot start command"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    await update.message.reply_text(
        "🤖 *Auto-Post Bot*\n\n"
        "📌 *Commands:*\n"
        "/addpost <post> - Naya post add karo\n"
        "/settime <HH:MM> - Post time set karo (24hr format)\n"
        "/setcount <number> - Daily post count set karo\n"
        "/setmessage <message> - Post ke baad ka custom message\n"
        "/listposts - Saare posts dekho\n"
        "/removepost <index> - Post remove karo\n"
        "/stats - Aaj ki stats dekho\n"
        "/help - Yeh message\n\n"
        "*Example:*\n"
        "/addpost Hello everyone! Welcome to our channel!",
        parse_mode="Markdown"
    )

async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Naya post add karo"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /addpost <your post content>")
        return
    
    post_text = " ".join(context.args)
    schedule = load_schedule()
    schedule["posts"].append(post_text)
    save_schedule(schedule)
    
    await update.message.reply_text(f"✅ Post added!\n\n📝 {post_text}\n\n📊 Total posts: {len(schedule['posts'])}")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Post time set karo"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /settime 07:00")
        return
    
    time_str = context.args[0]
    try:
        datetime.strptime(time_str, "%H:%M")
        schedule = load_schedule()
        schedule["post_time"] = time_str
        save_schedule(schedule)
        await update.message.reply_text(f"✅ Post time set to {time_str} daily!")
    except:
        await update.message.reply_text("❌ Invalid time! Use HH:MM format (e.g., 07:00)")

async def setcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Daily post count set karo"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /setcount 10")
        return
    
    try:
        count = int(context.args[0])
        if count < 1:
            await update.message.reply_text("❌ Count must be at least 1!")
            return
        
        schedule = load_schedule()
        schedule["daily_count"] = count
        save_schedule(schedule)
        await update.message.reply_text(f"✅ Daily post count set to {count}")
    except:
        await update.message.reply_text("❌ Invalid number! Use /setcount 10")

async def setmessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom message set karo (post ke baad aayega)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /setmessage <your message>")
        return
    
    msg = " ".join(context.args)
    schedule = load_schedule()
    schedule["custom_message"] = msg
    save_schedule(schedule)
    await update.message.reply_text(f"✅ Custom message set!\n\n📌 {msg}")

async def listposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saare posts dikhao"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    schedule = load_schedule()
    posts = schedule["posts"]
    
    if not posts:
        await update.message.reply_text("📭 No posts added yet! Use /addpost")
        return
    
    message = "📋 *All Posts:*\n\n"
    for i, post in enumerate(posts, 1):
        message += f"{i}. {post[:100]}{'...' if len(post) > 100 else ''}\n\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def removepost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Post remove karo"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /removepost <index>")
        return
    
    try:
        index = int(context.args[0]) - 1
        schedule = load_schedule()
        if 0 <= index < len(schedule["posts"]):
            removed = schedule["posts"].pop(index)
            save_schedule(schedule)
            await update.message.reply_text(f"✅ Removed post:\n\n{removed}")
        else:
            await update.message.reply_text("❌ Invalid index! Use /listposts to see indices")
    except:
        await update.message.reply_text("❌ Invalid number!")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Daily stats dikhao"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    schedule = load_schedule()
    today = datetime.now().strftime("%d-%m-%Y")
    
    # Track stats in memory (simple)
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": today, "posted": 0}
    
    stats = context.bot.daily_stats
    message = f"📊 *Daily Stats - {today}*\n\n"
    message += f"📝 Posts Today: {stats['posted']}\n"
    message += f"📋 Total Posts in Queue: {len(schedule['posts'])}\n"
    message += f"⏰ Post Time: {schedule['post_time']}\n"
    message += f"📦 Daily Count: {schedule['daily_count']}\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ---------- AUTO-POST SCHEDULER ----------
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    """Auto post karne wala function"""
    schedule = load_schedule()
    posts = schedule["posts"]
    daily_count = schedule["daily_count"]
    custom_msg = schedule["custom_message"]
    
    if not posts:
        print("📭 No posts in queue!")
        return
    
    # Kitne posts post karne hain?
    count = min(daily_count, len(posts))
    posted_today = 0
    
    for i in range(count):
        if i >= len(posts):
            break
        
        post_content = posts[i]
        
        # Post send karo
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=post_content
            )
            print(f"📤 Posted: {post_content[:50]}...")
            posted_today += 1
            
            # Custom message send karo (har post ke baad)
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=custom_msg
            )
            
            # Thoda wait karo (spam se bachne ke liye)
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Post error: {e}")
    
    # Remove posted posts from queue (post ho gaye toh hatao)
    if posted_today > 0:
        schedule["posts"] = schedule["posts"][posted_today:]
        save_schedule(schedule)
        print(f"✅ {posted_today} posts posted! {len(schedule['posts'])} remaining")
        
        # Stats update
        if not hasattr(context.bot, 'daily_stats'):
            context.bot.daily_stats = {"today": datetime.now().strftime("%d-%m-%Y"), "posted": 0}
        context.bot.daily_stats["posted"] += posted_today
        
        # Send report to admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📊 *Daily Post Report*\n\n"
                 f"✅ {posted_today} posts posted today!\n"
                 f"📝 Remaining posts: {len(schedule['posts'])}\n"
                 f"📅 Date: {datetime.now().strftime('%d-%m-%Y')}",
            parse_mode="Markdown"
        )

# ---------- DAILY STATS REPORT ----------
async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    """Rozana stats report bheje"""
    schedule = load_schedule()
    
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": datetime.now().strftime("%d-%m-%Y"), "posted": 0}
    
    stats = context.bot.daily_stats
    
    report = f"📊 *Daily Report - {datetime.now().strftime('%d-%m-%Y')}*\n\n"
    report += f"📝 Posts Today: {stats['posted']}\n"
    report += f"📋 Posts in Queue: {len(schedule['posts'])}\n"
    report += f"⏰ Next Post Time: {schedule['post_time']}\n"
    report += f"📦 Daily Count: {schedule['daily_count']}\n"
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode="Markdown")
    
    # Reset daily stats
    context.bot.daily_stats["posted"] = 0
    context.bot.daily_stats["today"] = datetime.now().strftime("%d-%m-%Y")

# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addpost", addpost))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("setcount", setcount))
    app.add_handler(CommandHandler("setmessage", setmessage))
    app.add_handler(CommandHandler("listposts", listposts))
    app.add_handler(CommandHandler("removepost", removepost))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    # Daily post scheduler
    job_queue = app.job_queue
    
    # Har minute check karo ki time aaya ya nahi
    async def check_time(context):
        now = datetime.now().strftime("%H:%M")
        schedule = load_schedule()
        if now == schedule["post_time"]:
            await auto_post(context)
    
    job_queue.run_repeating(check_time, interval=60, first=10)  # Har 1 minute check
    
    # Daily report at 23:59
    async def schedule_report(context):
        await daily_report(context)
    
    job_queue.run_daily(schedule_report, time=time(23, 59, 0))
    
    print("=" * 50)
    print("🤖 Auto-Post Bot is running!")
    print("📋 Commands: /addpost, /settime, /setcount, /setmessage, /listposts, /removepost, /stats")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()
