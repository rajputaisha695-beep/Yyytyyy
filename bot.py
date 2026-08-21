import asyncio
import json
import os
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"
CHANNEL_ID = -1003550209252
ADMIN_ID = 8961906024
# -------------------------

SCHEDULE_FILE = "schedule.json"

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
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        print(f"✅ {user.first_name} approved!")
        try:
            await context.bot.send_message(chat_id=user.id, text="🎉 Welcome to our channel!")
        except:
            pass
    except Exception as e:
        print(f"❌ Error: {e}")

# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    await update.message.reply_text(
        "🤖 *Auto-Post Bot*\n\n"
        "📌 *Commands:*\n"
        "/addpost <text> - Text post\n"
        "/addvideo - Video + Caption (DM me video bhejo)\n"
        "/settime <HH:MM AM/PM> - Set time\n"
        "/setcount <number> - Daily count\n"
        "/setmessage <msg> - Custom message\n"
        "/listposts - All posts\n"
        "/removepost <index> - Remove post\n"
        "/stats - Today's stats\n"
        "/help - Help",
        parse_mode="Markdown"
    )

async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /addpost <text>")
        return
    post_text = " ".join(context.args)
    schedule = load_schedule()
    schedule["posts"].append({"type": "text", "content": post_text})
    save_schedule(schedule)
    await update.message.reply_text(f"✅ Text post added!\n📝 {post_text}")

async def addvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    context.user_data['waiting_for_video'] = True
    await update.message.reply_text(
        "🎬 *Video Add Mode ON*\n\n"
        "Ab video bhejo with caption.\n"
        "Cancel: /cancelvideo",
        parse_mode="Markdown"
    )

async def cancelvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    context.user_data['waiting_for_video'] = False
    await update.message.reply_text("❌ Cancelled!")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.user_data.get('waiting_for_video'):
        return
    if update.message.video:
        video = update.message.video
        caption = update.message.caption or "🎬 New Video"
        video_data = {"type": "video", "file_id": video.file_id, "caption": caption}
        schedule = load_schedule()
        schedule["posts"].append(video_data)
        save_schedule(schedule)
        context.user_data['waiting_for_video'] = False
        await update.message.reply_text(f"✅ Video added! Caption: {caption[:50]}...")
    else:
        await update.message.reply_text("❌ Please send a video file!")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /settime 07:00 AM")
        return
    time_str = " ".join(context.args).upper()
    try:
        if "AM" in time_str or "PM" in time_str:
            parts = time_str.replace("AM", "").replace("PM", "").strip().split(":")
            hour = int(parts[0]); minute = int(parts[1])
            if "PM" in time_str and hour != 12: hour += 12
            elif "AM" in time_str and hour == 12: hour = 0
            schedule = load_schedule()
            schedule["post_time"] = f"{hour:02d}:{minute:02d}"
            save_schedule(schedule)
            await update.message.reply_text(f"✅ Time set to {time_str}")
        else:
            datetime.strptime(time_str, "%H:%M")
            schedule = load_schedule()
            schedule["post_time"] = time_str
            save_schedule(schedule)
            await update.message.reply_text(f"✅ Time set to {time_str}")
    except:
        await update.message.reply_text("❌ Invalid format! Use HH:MM AM/PM")

async def setcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /setcount 10")
        return
    try:
        count = int(context.args[0])
        schedule = load_schedule()
        schedule["daily_count"] = count
        save_schedule(schedule)
        await update.message.reply_text(f"✅ Daily count set to {count}")
    except:
        await update.message.reply_text("❌ Invalid number!")

async def setmessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /setmessage <msg>")
        return
    msg = " ".join(context.args)
    schedule = load_schedule()
    schedule["custom_message"] = msg
    save_schedule(schedule)
    await update.message.reply_text(f"✅ Custom message set: {msg}")

async def listposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    schedule = load_schedule()
    posts = schedule["posts"]
    if not posts:
        await update.message.reply_text("📭 No posts!")
        return
    msg = "📋 *All Posts:*\n\n"
    for i, p in enumerate(posts, 1):
        if p["type"] == "video":
            msg += f"{i}. 🎬 {p['caption'][:50]}...\n"
        else:
            msg += f"{i}. 📝 {p['content'][:50]}...\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def removepost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /removepost <index>")
        return
    try:
        idx = int(context.args[0]) - 1
        schedule = load_schedule()
        if 0 <= idx < len(schedule["posts"]):
            schedule["posts"].pop(idx)
            save_schedule(schedule)
            await update.message.reply_text(f"✅ Removed post #{idx + 1}")
        else:
            await update.message.reply_text("❌ Invalid index!")
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
    s = context.bot.daily_stats
    msg = f"📊 *Stats - {today}*\n📝 Today: {s['posted']}\n📋 Queue: {len(schedule['posts'])}\n⏰ Time: {schedule['post_time']}\n📦 Count: {schedule['daily_count']}"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ---------- AUTO-POST ----------
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    schedule = load_schedule()
    posts = schedule["posts"]
    count = min(schedule["daily_count"], len(posts))
    if not posts:
        return
    posted = 0
    for i in range(count):
        if i >= len(posts): break
        post = posts[i]
        try:
            if post["type"] == "video":
                await context.bot.send_video(chat_id=CHANNEL_ID, video=post["file_id"], caption=post["caption"])
            else:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=post["content"])
            posted += 1
            await context.bot.send_message(chat_id=CHANNEL_ID, text=schedule["custom_message"])
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Error: {e}")
    if posted > 0:
        schedule["posts"] = schedule["posts"][posted:]
        save_schedule(schedule)
        if not hasattr(context.bot, 'daily_stats'):
            context.bot.daily_stats = {"today": datetime.now().strftime("%d-%m-%Y"), "posted": 0}
        context.bot.daily_stats["posted"] += posted
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ {posted} posts posted! Remaining: {len(schedule['posts'])}")

# ---------- DAILY REPORT ----------
async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    schedule = load_schedule()
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": datetime.now().strftime("%d-%m-%Y"), "posted": 0}
    s = context.bot.daily_stats
    report = f"📊 Daily Report - {datetime.now().strftime('%d-%m-%Y')}\n📝 Posts: {s['posted']}\n📋 Queue: {len(schedule['posts'])}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=report)
    s["posted"] = 0

# ---------- CHECK TIME ----------
async def check_time(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M")
    schedule = load_schedule()
    if now == schedule["post_time"]:
        await auto_post(context)

# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(ChatJoinRequestHandler(auto_approve))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addpost", addpost))
    app.add_handler(CommandHandler("addvideo", addvideo))
    app.add_handler(CommandHandler("cancelvideo", cancelvideo))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("setcount", setcount))
    app.add_handler(CommandHandler("setmessage", setmessage))
    app.add_handler(CommandHandler("listposts", listposts))
    app.add_handler(CommandHandler("removepost", removepost))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    # 🔥 FIXED - CORRECT WAY
    app.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND, handle_video))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(check_time, interval=60, first=10)
        job_queue.run_daily(daily_report, time=time(23, 59, 0))
        print("✅ JobQueue ready!")
    
    print("🤖 Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
