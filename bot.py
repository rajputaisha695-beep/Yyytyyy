import asyncio
import json
import os
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"
CHANNEL_ID = -1003550209252
ADMIN_ID = 8961906024
# -------------------------

# Schedule file
SCHEDULE_FILE = "schedule.json"

# ---------- SCHEDULE FUNCTIONS ----------
def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return {"posts": [], "daily_count": 1, "post_time": "07:00", "custom_message": "📌 Join our channel for more updates!"}

def save_schedule(data):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ---------- AUTO-APPROVE ----------
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.chat_join_request.from_user
        chat = update.chat_join_request.chat
        
        await context.bot.approve_chat_join_request(
            chat_id=chat.id, 
            user_id=user.id
        )
        
        print(f"✅ {user.first_name} (ID: {user.id}) approved!")
        
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text="🎉 Welcome to our channel!\n\nStay tuned for amazing content! 😊"
            )
        except:
            pass
        
    except Exception as e:
        print(f"❌ Auto-approve error: {e}")

# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    await update.message.reply_text(
        "🤖 *Auto-Post Bot*\n\n"
        "📌 *Commands:*\n"
        "/addpost <text or video link> - Post add karo\n"
        "/settime <HH:MM AM/PM> - Post time set karo\n"
        "/setcount <number> - Daily post count\n"
        "/setmessage <message> - Post ke baad ka message\n"
        "/listposts - Saare posts dekho\n"
        "/removepost <index> - Post remove karo\n"
        "/stats - Aaj ki stats\n"
        "/help - Help\n\n"
        "*Examples:*\n"
        "/addpost Hello everyone!\n"
        "/addpost https://1024terabox.com/s/abc123\n"
        "/settime 07:00 AM\n"
        "/settime 09:30 PM",
        parse_mode="Markdown"
    )

async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /addpost <your post content or video link>")
        return
    
    post_text = " ".join(context.args)
    schedule = load_schedule()
    schedule["posts"].append(post_text)
    save_schedule(schedule)
    
    await update.message.reply_text(f"✅ Post added!\n\n📝 {post_text}\n\n📊 Total posts: {len(schedule['posts'])}")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /settime 07:00 AM or /settime 09:30 PM")
        return
    
    time_str = " ".join(context.args).upper()
    
    # Convert 12-hour to 24-hour format
    try:
        if "AM" in time_str or "PM" in time_str:
            # Parse 12-hour format
            time_parts = time_str.replace("AM", "").replace("PM", "").strip().split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            if "PM" in time_str and hour != 12:
                hour += 12
            elif "AM" in time_str and hour == 12:
                hour = 0
            
            # Validate
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                schedule = load_schedule()
                schedule["post_time"] = f"{hour:02d}:{minute:02d}"
                save_schedule(schedule)
                await update.message.reply_text(f"✅ Post time set to {time_str} daily!")
                return
            else:
                await update.message.reply_text("❌ Invalid time! Use HH:MM AM/PM (e.g., 07:00 AM)")
                return
        else:
            # Try 24-hour format
            datetime.strptime(time_str, "%H:%M")
            schedule = load_schedule()
            schedule["post_time"] = time_str
            save_schedule(schedule)
            await update.message.reply_text(f"✅ Post time set to {time_str} daily!")
            return
    except:
        await update.message.reply_text("❌ Invalid time! Use HH:MM AM/PM (e.g., 07:00 AM or 09:30 PM)")

async def setcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        # Check if it's a video/link
        if post.startswith("http"):
            message += f"{i}. 📹 [Video Link]({post})\n\n"
        else:
            message += f"{i}. {post[:100]}{'...' if len(post) > 100 else ''}\n\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def removepost(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    schedule = load_schedule()
    today = datetime.now().strftime("%d-%m-%Y")
    
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": today, "posted": 0}
    
    stats_data = context.bot.daily_stats
    message = f"📊 *Daily Stats - {today}*\n\n"
    message += f"📝 Posts Today: {stats_data['posted']}\n"
    message += f"📋 Total Posts in Queue: {len(schedule['posts'])}\n"
    message += f"⏰ Post Time: {schedule['post_time']}\n"
    message += f"📦 Daily Count: {schedule['daily_count']}\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ---------- AUTO-POST ----------
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    schedule = load_schedule()
    posts = schedule["posts"]
    daily_count = schedule["daily_count"]
    custom_msg = schedule["custom_message"]
    
    if not posts:
        print("📭 No posts in queue!")
        return
    
    count = min(daily_count, len(posts))
    posted_today = 0
    
    for i in range(count):
        if i >= len(posts):
            break
        
        post_content = posts[i]
        
        try:
            # Check if it's a video link
            if post_content.startswith("http") and ("youtube.com" in post_content or "terabox.com" in post_content or "youtu.be" in post_content):
                # Send as text with link (video link)
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"🎬 *Video Link:*\n\n{post_content}",
                    parse_mode="Markdown"
                )
                print(f"📹 Video link posted: {post_content[:50]}...")
            else:
                # Send as normal text
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=post_content
                )
                print(f"📤 Posted: {post_content[:50]}...")
            
            posted_today += 1
            
            # Custom message after each post
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=custom_msg
            )
            
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Post error: {e}")
    
    if posted_today > 0:
        schedule["posts"] = schedule["posts"][posted_today:]
        save_schedule(schedule)
        print(f"✅ {posted_today} posts posted! {len(schedule['posts'])} remaining")
        
        if not hasattr(context.bot, 'daily_stats'):
            context.bot.daily_stats = {"today": datetime.now().strftime("%d-%m-%Y"), "posted": 0}
        context.bot.daily_stats["posted"] += posted_today
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📊 *Daily Post Report*\n\n"
                 f"✅ {posted_today} posts posted today!\n"
                 f"📝 Remaining posts: {len(schedule['posts'])}\n"
                 f"📅 Date: {datetime.now().strftime('%d-%m-%Y')}",
            parse_mode="Markdown"
        )

# ---------- DAILY REPORT ----------
async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    schedule = load_schedule()
    
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": datetime.now().strftime("%d-%m-%Y"), "posted": 0}
    
    stats_data = context.bot.daily_stats
    
    report = f"📊 *Daily Report - {datetime.now().strftime('%d-%m-%Y')}*\n\n"
    report += f"📝 Posts Today: {stats_data['posted']}\n"
    report += f"📋 Posts in Queue: {len(schedule['posts'])}\n"
    report += f"⏰ Next Post Time: {schedule['post_time']}\n"
    report += f"📦 Daily Count: {schedule['daily_count']}\n"
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode="Markdown")
    
    context.bot.daily_stats["posted"] = 0
    context.bot.daily_stats["today"] = datetime.now().strftime("%d-%m-%Y")

# ---------- CHECK TIME ----------
async def check_time(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M")
    schedule = load_schedule()
    if now == schedule["post_time"]:
        await auto_post(context)

# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Auto-Approve
    app.add_handler(ChatJoinRequestHandler(auto_approve))
    
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
    
    # JobQueue
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(check_time, interval=60, first=10)
        job_queue.run_daily(daily_report, time=time(23, 59, 0))
        print("✅ JobQueue initialized!")
    else:
        print("⚠️ JobQueue not available!")
    
    print("=" * 50)
    print("🤖 Auto-Approval + Auto-Post Bot is running!")
    print(f"📢 Channel ID: {CHANNEL_ID}")
    print(f"👤 Admin ID: {ADMIN_ID}")
    print("✅ Auto-approve: ON")
    print("📋 Commands: /addpost, /settime, /setcount, /setmessage, /listposts, /removepost, /stats")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()
