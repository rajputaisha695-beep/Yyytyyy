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

# ---------- IST TIME ----------
def get_ist_time():
    """Current IST time return kare"""
    return datetime.now() + timedelta(hours=5, minutes=30)

def get_ist_time_str():
    """IST time as string (HH:MM:SS)"""
    return get_ist_time().strftime("%I:%M:%S %p")  # 12-hour format with AM/PM

def get_ist_date_str():
    """IST date as string (DD-MM-YYYY)"""
    return get_ist_time().strftime("%d-%m-%Y")

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
        
        print(f"✅ {user.first_name} approved!")
        
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"🎉 Welcome to our channel!\n\n🕐 IST: {get_ist_time_str()}"
            )
        except:
            pass
        
    except Exception as e:
        print(f"❌ Auto-approve error: {e}")

# ---------- FORWARD COMMAND ----------
async def addforward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    context.user_data['waiting_for_forward'] = True
    await update.message.reply_text(
        f"📤 *Forward Mode ON*\n\n"
        f"Ab mujhe kisi bhi chat/channel se *message forward* karo.\n"
        f"Mein usko schedule me add kar dunga!\n\n"
        f"🕐 IST: {get_ist_time_str()}\n\n"
        f"❌ Cancel: /cancelforward",
        parse_mode="Markdown"
    )

async def cancelforward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    context.user_data['waiting_for_forward'] = False
    await update.message.reply_text(f"❌ Forward mode cancelled!\n\n🕐 IST: {get_ist_time_str()}")

# ---------- HANDLE FORWARDED MESSAGE ----------
async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.user_data.get('waiting_for_forward'):
        return
    
    if update.message.forward_from or update.message.forward_from_chat:
        forward_data = {
            "type": "forward",
            "chat_id": update.message.forward_from_chat.id if update.message.forward_from_chat else update.message.forward_from.id,
            "message_id": update.message.forward_from_message_id,
            "caption": update.message.caption or update.message.text or "📌 Forwarded Post",
            "added_at": get_ist_time_str()
        }
        
        schedule = load_schedule()
        schedule["posts"].append(forward_data)
        save_schedule(schedule)
        
        context.user_data['waiting_for_forward'] = False
        
        await update.message.reply_text(
            f"✅ Forward added to schedule!\n\n"
            f"📝 Caption: {forward_data['caption'][:100]}...\n"
            f"📊 Total posts: {len(schedule['posts'])}\n"
            f"🕐 Added at: {get_ist_time_str()}"
        )
        print(f"📤 Forward added at {get_ist_time_str()}!")
    else:
        await update.message.reply_text(f"❌ Please forward a message!\n\n🕐 IST: {get_ist_time_str()}")

# ---------- TEXT POST ----------
async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /addpost <your post content>\n\n🕐 IST: {get_ist_time_str()}")
        return
    
    post_text = " ".join(context.args)
    schedule = load_schedule()
    schedule["posts"].append({"type": "text", "content": post_text, "added_at": get_ist_time_str()})
    save_schedule(schedule)
    
    await update.message.reply_text(
        f"✅ Text post added!\n\n"
        f"📝 {post_text}\n\n"
        f"📊 Total: {len(schedule['posts'])}\n"
        f"🕐 Added at: {get_ist_time_str()}"
    )

# ---------- OTHER COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    await update.message.reply_text(
        f"🤖 *Auto-Post Bot*\n\n"
        f"🕐 *IST Time:* {get_ist_time_str()}\n"
        f"📅 *Date:* {get_ist_date_str()}\n\n"
        f"📌 *Commands:*\n"
        f"/addpost <text> - Text post add\n"
        f"/addforward - Forward message add\n"
        f"/settime <HH:MM AM/PM> - Post time set\n"
        f"/setcount <number> - Daily post count\n"
        f"/setmessage <msg> - Custom message\n"
        f"/listposts - All posts\n"
        f"/removepost <index> - Remove\n"
        f"/stats - Today's stats\n"
        f"/time - Current IST time\n"
        f"/help - Help",
        parse_mode="Markdown"
    )

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /settime 07:00 AM\n\n🕐 IST: {get_ist_time_str()}")
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
                await update.message.reply_text(
                    f"✅ Time set to {time_str} IST!\n\n"
                    f"🕐 Current IST: {get_ist_time_str()}"
                )
                return
        else:
            datetime.strptime(time_str, "%H:%M")
            schedule = load_schedule()
            schedule["post_time"] = time_str
            save_schedule(schedule)
            await update.message.reply_text(
                f"✅ Time set to {time_str} IST!\n\n"
                f"🕐 Current IST: {get_ist_time_str()}"
            )
            return
    except:
        await update.message.reply_text(f"❌ Invalid time! Use HH:MM AM/PM\n\n🕐 IST: {get_ist_time_str()}")

async def setcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /setcount 10\n\n🕐 IST: {get_ist_time_str()}")
        return
    
    try:
        count = int(context.args[0])
        if count < 1:
            await update.message.reply_text("❌ Count must be at least 1!")
            return
        
        schedule = load_schedule()
        schedule["daily_count"] = count
        save_schedule(schedule)
        await update.message.reply_text(
            f"✅ Daily count set to {count}\n\n"
            f"🕐 IST: {get_ist_time_str()}"
        )
    except:
        await update.message.reply_text(f"❌ Invalid number!\n\n🕐 IST: {get_ist_time_str()}")

async def setmessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /setmessage <msg>\n\n🕐 IST: {get_ist_time_str()}")
        return
    
    msg = " ".join(context.args)
    schedule = load_schedule()
    schedule["custom_message"] = msg
    save_schedule(schedule)
    await update.message.reply_text(
        f"✅ Custom message set!\n\n"
        f"📌 {msg}\n\n"
        f"🕐 IST: {get_ist_time_str()}"
    )

async def listposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    schedule = load_schedule()
    posts = schedule["posts"]
    
    if not posts:
        await update.message.reply_text(f"📭 No posts added!\n\n🕐 IST: {get_ist_time_str()}")
        return
    
    message = f"📋 *All Posts:*\n\n"
    for i, post in enumerate(posts, 1):
        if post["type"] == "forward":
            message += f"{i}. 📤 Forward - {post['caption'][:100]}{'...' if len(post['caption']) > 100 else ''}\n"
            message += f"   🕐 Added: {post.get('added_at', 'Unknown')}\n\n"
        else:
            message += f"{i}. 📝 {post['content'][:100]}{'...' if len(post['content']) > 100 else ''}\n"
            message += f"   🕐 Added: {post.get('added_at', 'Unknown')}\n\n"
    
    message += f"\n🕐 Current IST: {get_ist_time_str()}"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def removepost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /removepost <index>\n\n🕐 IST: {get_ist_time_str()}")
        return
    
    try:
        index = int(context.args[0]) - 1
        schedule = load_schedule()
        if 0 <= index < len(schedule["posts"]):
            removed = schedule["posts"].pop(index)
            save_schedule(schedule)
            await update.message.reply_text(
                f"✅ Removed post #{index + 1}\n\n"
                f"🕐 IST: {get_ist_time_str()}"
            )
        else:
            await update.message.reply_text(f"❌ Invalid index!\n\n🕐 IST: {get_ist_time_str()}")
    except:
        await update.message.reply_text(f"❌ Invalid number!\n\n🕐 IST: {get_ist_time_str()}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    schedule = load_schedule()
    today = get_ist_date_str()
    
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": today, "posted": 0}
    
    stats_data = context.bot.daily_stats
    message = f"📊 *Stats - {today} (IST)*\n\n"
    message += f"📝 Posted Today: {stats_data['posted']}\n"
    message += f"📋 Queue: {len(schedule['posts'])}\n"
    message += f"⏰ Time: {schedule['post_time']} IST\n"
    message += f"📦 Daily Count: {schedule['daily_count']}\n"
    message += f"\n🕐 Current IST: {get_ist_time_str()}"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/time command - Sirf live time dikhaye"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    await update.message.reply_text(
        f"🕐 *IST Time:* {get_ist_time_str()}\n"
        f"📅 *IST Date:* {get_ist_date_str()}",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ---------- AUTO-POST ----------
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    schedule = load_schedule()
    posts = schedule["posts"]
    daily_count = schedule["daily_count"]
    custom_msg = schedule["custom_message"]
    
    if not posts:
        print(f"📭 No posts in queue! ({get_ist_time_str()})")
        return
    
    count = min(daily_count, len(posts))
    posted_today = 0
    
    for i in range(count):
        if i >= len(posts):
            break
        
        post = posts[i]
        
        try:
            if post["type"] == "forward":
                await context.bot.forward_message(
                    chat_id=CHANNEL_ID,
                    from_chat_id=post["chat_id"],
                    message_id=post["message_id"]
                )
                print(f"📤 Forwarded at {get_ist_time_str()}: {post['caption'][:50]}...")
            else:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=post["content"]
                )
                print(f"📝 Text posted at {get_ist_time_str()}: {post['content'][:50]}...")
            
            posted_today += 1
            
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=custom_msg
            )
            
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Post error at {get_ist_time_str()}: {e}")
    
    if posted_today > 0:
        schedule["posts"] = schedule["posts"][posted_today:]
        save_schedule(schedule)
        print(f"✅ {posted_today} posts posted at {get_ist_time_str()}!")
        
        if not hasattr(context.bot, 'daily_stats'):
            context.bot.daily_stats = {"today": get_ist_date_str(), "posted": 0}
        context.bot.daily_stats["posted"] += posted_today
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📊 *Daily Report*\n\n"
                 f"✅ {posted_today} posts posted today!\n"
                 f"📝 Remaining: {len(schedule['posts'])}\n"
                 f"📅 {get_ist_date_str()} (IST)\n"
                 f"🕐 Posted at: {get_ist_time_str()}",
            parse_mode="Markdown"
        )

# ---------- DAILY REPORT ----------
async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    schedule = load_schedule()
    
    if not hasattr(context.bot, 'daily_stats'):
        context.bot.daily_stats = {"today": get_ist_date_str(), "posted": 0}
    
    stats_data = context.bot.daily_stats
    
    report = f"📊 *Daily Report - {get_ist_date_str()} (IST)*\n\n"
    report += f"📝 Posts Today: {stats_data['posted']}\n"
    report += f"📋 Queue: {len(schedule['posts'])}\n"
    report += f"⏰ Next Time: {schedule['post_time']} IST\n"
    report += f"📦 Daily Count: {schedule['daily_count']}\n"
    report += f"\n🕐 Report at: {get_ist_time_str()}"
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode="Markdown")
    
    context.bot.daily_stats["posted"] = 0
    context.bot.daily_stats["today"] = get_ist_date_str()

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
    app.add_handler(CommandHandler("addforward", addforward))
    app.add_handler(CommandHandler("cancelforward", cancelforward))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("setcount", setcount))
    app.add_handler(CommandHandler("setmessage", setmessage))
    app.add_handler(CommandHandler("listposts", listposts))
    app.add_handler(CommandHandler("removepost", removepost))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("time", time_command))  # 🔥 Live time command
    app.add_handler(CommandHandler("help", help_command))
    
    # Forward handler
    app.add_handler(MessageHandler(filters.FORWARDED, handle_forward))
    
    print("=" * 50)
    print("🤖 Auto-Approval + Forward Bot is running!")
    print(f"📢 Channel ID: {CHANNEL_ID}")
    print(f"👤 Admin ID: {ADMIN_ID}")
    print(f"🕐 Current IST Time: {get_ist_time_str()}")
    print(f"📅 Current IST Date: {get_ist_date_str()}")
    print("✅ Auto-approve: ON")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()
