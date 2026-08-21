import asyncio
import json
import os
from datetime import datetime, time, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"
CHANNEL_ID = -1003550209252
ADMIN_ID = 8961906024
# -------------------------

# Schedule file
SCHEDULE_FILE = "schedule.json"

# ---------- IST TIME FUNCTION ----------
def get_ist_time():
    """Indian Standard Time (UTC+5:30)"""
    return datetime.now() + timedelta(hours=5, minutes=30)

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
        "🤖 *Auto-Post Bot* (IST Timezone)\n\n"
        "📌 *Commands:*\n"
        "/addpost <text> - Text post add karo\n"
        "/addvideo - Video + Caption post add karo\n"
        "/settime <HH:MM AM/PM> - Post time set karo (IST)\n"
        "/setcount <number> - Daily post count\n"
        "/setmessage <message> - Post ke baad ka message\n"
        "/listposts - Saare posts dekho\n"
        "/removepost <index> - Post remove karo\n"
        "/stats - Aaj ki stats\n"
        "/help - Help\n\n"
        "*Example:*\n"
        "/addpost Hello everyone!\n"
        "/settime 07:00 AM",
        parse_mode="Markdown"
    )

async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /addpost <your post content>")
        return
    
    post_text = " ".join(context.args)
    schedule = load_schedule()
    schedule["posts"].append({"type": "text", "content": post_text})
    save_schedule(schedule)
    
    await update.message.reply_text(f"✅ Text post added!\n\n📝 {post_text}\n\n📊 Total posts: {len(schedule['posts'])}")

async def addvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    context.user_data['waiting_for_video'] = True
    await update.message.reply_text(
        "🎬 *Video Add Mode ON*\n\n"
        "Ab mujhe video bhejo with caption.\n\n"
        "❌ Cancel: /cancelvideo",
        parse_mode="Markdown"
    )

async def cancelvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    context.user_data['waiting_for_video'] = False
    await update.message.reply_text("❌ Video add cancelled!")

# ---------- VIDEO HANDLER ----------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.user_data.get('waiting_for_video'):
        return
    
    if update.message.video:
        video = update.message.video
        caption = update.message.caption or "🎬 New Video"
        
        video_data = {
            "type": "video",
            "file_id": video.file_id,
            "caption": caption,
            "duration": video.duration
        }
        
        schedule = load_schedule()
        schedule["posts"].append(video_data)
        save_schedule(schedule)
        
        context.user_data['waiting_for_video'] = False
        
        await update.message.reply_text(
            f"✅ Video added!\n\n"
            f"🎬 Duration: {video.duration}s\n"
            f"📝 Caption: {caption[:100]}...\n"
            f"📊 Total: {len(schedule['posts'])}"
        )
    else:
        await update.message.reply_text("❌ Please send a video file!")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /settime 07:00 AM or /settime 09:30 PM")
        return
    
    time_str = " ".join(context.args).upper()
    
    try:
        if "AM" in time_str or "PM" in time_str:
            time_parts = time_str.replace("AM", "").replace("PM", "").strip().split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            if "PM" in time_str and hour != 12:
                hour += 12
            elif "AM" in time_str and hour == 12:
                hour = 0
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                schedule = load_schedule()
                schedule["post_time"] = f"{hour:02d}:{minute:02d}"
                save_schedule(schedule)
                await update.message.reply_text(f"✅ Post time set to {time_str} IST daily!")
                return
        else:
            datetime.strptime(time_str, "%H:%M")
            schedule = load_schedule()
            schedule["post_time"] = time_str
            save_schedule(schedule)
            await update.message.reply_text(f"✅ Post time set to {time_str} IST daily!")
            return
    except:
        await update.message.reply_text("❌ Invalid time! Use HH:MM AM/PM")

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
        await update.message.reply_text("❌ Invalid number!")

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
        await update.message.reply_text("📭 No posts added yet!")
        return
    
    message = "📋 *All Posts:*\n\n"
    for i, post in enumerate(posts, 1):
        if post["type"] == "video":
            message += f"{i}. 🎬 Video - {post['caption'][:100]}{'...' if len(post['caption']) > 100 else ''}\n\n"
        else:
            message += f"{i}. 📝 {post['content'][:100]}{'...' if len(post['content']) > 100 else ''}\n\n"
    
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
            schedule["posts"].pop(index)
            save_schedule(schedule)
            await update.message.reply_text(f"✅ Removed post #{index + 1}")
        else:
            await update.message.reply_text("❌ Invalid index!")
    except:
        await update.message.reply_text("❌ Invalid number!")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    schedule = load_schedule()
    now = get_ist_time()
    today = now.strftime("%d-%m-%Y")
    
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": today, "posted": 0}
    
    stats_data = context.bot.daily_stats
    message = f"📊 *Daily Stats - {today} (IST)*\n\n"
    message += f"📝 Posts Today: {stats_data['posted']}\n"
    message += f"📋 Queue: {len(schedule['posts'])}\n"
    message += f"⏰ Time: {schedule['post_time']} IST\n"
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
        
        post = posts[i]
        
        try:
            if post["type"] == "video":
                await context.bot.send_video(
                    chat_id=CHANNEL_ID,
                    video=post["file_id"],
                    caption=post["caption"]
                )
                print(f"📹 Video posted: {post['caption'][:50]}...")
            else:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=post["content"]
                )
                print(f"📤 Posted: {post['content'][:50]}...")
            
            posted_today += 1
            
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
            context.bot.daily_stats = {"today": get_ist_time().strftime("%d-%m-%Y"), "posted": 0}
        context.bot.daily_stats["posted"] += posted_today
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📊 *Daily Post Report*\n\n"
                 f"✅ {posted_today} posts posted today!\n"
                 f"📝 Remaining: {len(schedule['posts'])}\n"
                 f"📅 {get_ist_time().strftime('%d-%m-%Y')} (IST)",
            parse_mode="Markdown"
        )

# ---------- DAILY REPORT ----------
async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    schedule = load_schedule()
    
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": get_ist_time().strftime("%d-%m-%Y"), "posted": 0}
    
    stats_data = context.bot.daily_stats
    
    report = f"📊 *Daily Report - {get_ist_time().strftime('%d-%m-%Y')} (IST)*\n\n"
    report += f"📝 Posts Today: {stats_data['posted']}\n"
    report += f"📋 Queue: {len(schedule['posts'])}\n"
    report += f"⏰ Next Time: {schedule['post_time']} IST\n"
    report += f"📦 Daily Count: {schedule['daily_count']}\n"
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode="Markdown")
    
    context.bot.daily_stats["posted"] = 0
    context.bot.daily_stats["today"] = get_ist_time().strftime("%d-%m-%Y")

# ---------- CHECK TIME ----------
async def check_time(context: ContextTypes.DEFAULT_TYPE):
    now = get_ist_time().strftime("%H:%M")
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
    app.add_handler(CommandHandler("addvideo", addvideo))
    app.add_handler(CommandHandler("cancelvideo", cancelvideo))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("setcount", setcount))
    app.add_handler(CommandHandler("setmessage", setmessage))
    app.add_handler(CommandHandler("listposts", listposts))
    app.add_handler(CommandHandler("removepost", removepost))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    # 🔥 FIXED: Video handler - DON'T USE filters.PRIVATE
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
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
    print("🕐 Timezone: IST (UTC+5:30)")
    print("✅ Auto-approve: ON")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()
