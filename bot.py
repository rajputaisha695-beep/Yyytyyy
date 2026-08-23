import asyncio
import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"
CHANNEL_ID = -1003598998273
ADMIN_ID = 8961906024
# -------------------------

# ---------- WELCOME MESSAGE ----------
WELCOME_MESSAGE = """🎉 *Welcome to our channel!* 🎉

Thank you for joining! We're glad to have you here.

📌 *Rules:*
1️⃣ No Spam
2️⃣ Be Respectful
3️⃣ No Promotions

Enjoy your stay! 😊

🕐 Joined at: {time}
"""

SCHEDULE_FILE = "schedule.json"

def get_ist():
    return datetime.now() + timedelta(hours=5, minutes=30)

def ist_str():
    return get_ist().strftime("%I:%M:%S %p")

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return {"posts": [], "daily_count": 1, "post_time": "07:00", "custom_message": "📌 Thanks for joining!"}

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
        
        print(f"✅ {user.first_name} approved at {ist_str()}!")
        
        try:
            welcome_text = WELCOME_MESSAGE.format(
                time=ist_str(),
                first_name=user.first_name,
                username=user.username or "No username"
            )
            
            await context.bot.send_message(
                chat_id=user.id,
                text=welcome_text,
                parse_mode="Markdown"
            )
            print(f"📤 Welcome DM sent to {user.first_name}")
        except Exception as e:
            print(f"❌ Could not send DM: {e}")
        
    except Exception as e:
        print(f"❌ Auto-approve error: {e}")

# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    await update.message.reply_text(
        f"🤖 *Bot*\n🕐 {ist_str()}\n\n"
        f"/addpost <text> - Add text\n"
        f"/addforward - Forward mode\n"
        f"/settime <HH:MM AM/PM> - Set time\n"
        f"/setcount <num> - Daily count\n"
        f"/setwelcome <msg> - Set welcome message\n"
        f"/viewwelcome - View welcome message\n"
        f"/listposts - All posts\n"
        f"/removepost <index> - Remove\n"
        f"/stats - Stats\n"
        f"/postnow - Post now!\n"
        f"/approveall - Approve ALL pending 🔥\n"
        f"/time - IST time",
        parse_mode="Markdown"
    )

# ---------- 🔥 APPROVE ALL - 100% WORKING ----------
async def approveall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    msg = await update.message.reply_text("📥 Fetching pending join requests...")
    
    try:
        # 🔥 FIX: Direct API call using bot
        bot = context.bot
        
        # Get all pending join requests
        pending_requests = []
        async for request in bot.get_chat_join_requests(CHANNEL_ID):
            pending_requests.append(request)
        
        if not pending_requests:
            await msg.edit_text("✅ No pending requests found!")
            return
        
        total = len(pending_requests)
        await msg.edit_text(f"📊 Found {total} pending requests. Approving...")
        
        approved = 0
        failed = 0
        
        for request in pending_requests:
            user = request.from_user
            try:
                await bot.approve_chat_join_request(
                    chat_id=CHANNEL_ID,
                    user_id=user.id
                )
                approved += 1
                
                # Welcome DM
                try:
                    welcome_text = WELCOME_MESSAGE.format(
                        time=ist_str(),
                        first_name=user.first_name,
                        username=user.username or "No username"
                    )
                    await bot.send_message(
                        chat_id=user.id,
                        text=welcome_text,
                        parse_mode="Markdown"
                    )
                except:
                    pass
                
                await asyncio.sleep(0.3)
                
            except Exception as e:
                failed += 1
                print(f"❌ Error: {e}")
        
        await msg.edit_text(
            f"✅ *Approve Complete!*\n\n"
            f"✅ Approved: {approved}\n"
            f"❌ Failed: {failed}\n"
            f"📋 Total: {total}\n"
            f"🕐 {ist_str()}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
        print(f"❌ ApproveAll Error: {e}")

# ---------- SET WELCOME ----------
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ /setwelcome <your welcome message>")
        return
    
    global WELCOME_MESSAGE
    WELCOME_MESSAGE = " ".join(context.args)
    
    with open("welcome.txt", "w") as f:
        f.write(WELCOME_MESSAGE)
    
    await update.message.reply_text(f"✅ Welcome message updated!")

async def viewwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    await update.message.reply_text(
        f"📋 *Current Welcome Message:*\n\n{WELCOME_MESSAGE}",
        parse_mode="Markdown"
    )

# ---------- OTHER COMMANDS ----------
async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ /addpost <text>")
        return
    text = " ".join(context.args)
    s = load_schedule()
    s["posts"].append({"type": "text", "content": text})
    save_schedule(s)
    await update.message.reply_text(f"✅ Added! Total: {len(s['posts'])}")

async def addforward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    context.user_data['waiting_forward'] = True
    await update.message.reply_text(f"📤 Forward Mode ON\n\nForward a message now!\n/cancelforward to cancel")

async def cancelforward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    context.user_data['waiting_forward'] = False
    await update.message.reply_text("❌ Cancelled!")

async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.user_data.get('waiting_forward'):
        return
    
    msg = update.message
    if msg.forward_from or msg.forward_from_chat:
        data = {
            "type": "forward",
            "chat_id": msg.forward_from_chat.id if msg.forward_from_chat else msg.forward_from.id,
            "message_id": msg.forward_from_message_id,
            "caption": msg.caption or msg.text or "Forwarded"
        }
        s = load_schedule()
        s["posts"].append(data)
        save_schedule(s)
        context.user_data['waiting_forward'] = False
        await update.message.reply_text(f"✅ Forward added! Total: {len(s['posts'])}")
    else:
        await update.message.reply_text("❌ Please forward a message!")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ /settime 07:00 AM")
        return
    t = " ".join(context.args).upper()
    try:
        if "AM" in t or "PM" in t:
            parts = t.replace("AM", "").replace("PM", "").strip().split(":")
            h, m = int(parts[0]), int(parts[1])
            if "PM" in t and h != 12: h += 12
            elif "AM" in t and h == 12: h = 0
            s = load_schedule()
            s["post_time"] = f"{h:02d}:{m:02d}"
            save_schedule(s)
            await update.message.reply_text(f"✅ Time set to {t} IST!")
    except:
        await update.message.reply_text("❌ Invalid! Use HH:MM AM/PM")

async def setcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ /setcount 5")
        return
    try:
        c = int(context.args[0])
        s = load_schedule()
        s["daily_count"] = c
        save_schedule(s)
        await update.message.reply_text(f"✅ Daily count: {c}")
    except:
        await update.message.reply_text("❌ Invalid number!")

async def setmessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ /setmessage <msg>")
        return
    msg = " ".join(context.args)
    s = load_schedule()
    s["custom_message"] = msg
    save_schedule(s)
    await update.message.reply_text(f"✅ Custom message set!")

async def listposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    s = load_schedule()
    if not s["posts"]:
        await update.message.reply_text("📭 No posts!")
        return
    msg = "📋 *Posts:*\n"
    for i, p in enumerate(s["posts"], 1):
        msg += f"{i}. {'📤' if p['type']=='forward' else '📝'} {p.get('caption', p.get('content', ''))[:50]}...\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def removepost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ /removepost <index>")
        return
    try:
        i = int(context.args[0]) - 1
        s = load_schedule()
        if 0 <= i < len(s["posts"]):
            s["posts"].pop(i)
            save_schedule(s)
            await update.message.reply_text(f"✅ Removed #{i+1}")
        else:
            await update.message.reply_text("❌ Invalid index!")
    except:
        await update.message.reply_text("❌ Invalid number!")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    s = load_schedule()
    await update.message.reply_text(
        f"📊 *Stats*\n"
        f"📝 Queue: {len(s['posts'])}\n"
        f"⏰ Time: {s['post_time']} IST\n"
        f"📦 Daily: {s['daily_count']}\n"
        f"🕐 {ist_str()}",
        parse_mode="Markdown"
    )

async def postnow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(f"⏳ Posting... ({ist_str()})")
    await auto_post(context)

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(f"🕐 IST: {ist_str()}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ---------- AUTO POST ----------
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    s = load_schedule()
    posts = s["posts"]
    if not posts:
        return
    
    count = min(s["daily_count"], len(posts))
    posted = 0
    
    for i in range(count):
        if i >= len(posts):
            break
        p = posts[i]
        try:
            if p["type"] == "forward":
                await context.bot.forward_message(
                    chat_id=CHANNEL_ID,
                    from_chat_id=p["chat_id"],
                    message_id=p["message_id"]
                )
            else:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=p["content"]
                )
            posted += 1
            await context.bot.send_message(chat_id=CHANNEL_ID, text=s["custom_message"])
            await asyncio.sleep(3)
        except Exception as e:
            print(f"❌ Post error: {e}")
    
    if posted > 0:
        s["posts"] = s["posts"][posted:]
        save_schedule(s)

# ---------- CHECK TIME ----------
async def check_time(context: ContextTypes.DEFAULT_TYPE):
    now = get_ist().strftime("%H:%M")
    s = load_schedule()
    if now == s["post_time"]:
        await auto_post(context)

# ---------- MAIN ----------
def main():
    global WELCOME_MESSAGE
    if os.path.exists("welcome.txt"):
        with open("welcome.txt", "r") as f:
            WELCOME_MESSAGE = f.read()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(ChatJoinRequestHandler(auto_approve))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addpost", addpost))
    app.add_handler(CommandHandler("addforward", addforward))
    app.add_handler(CommandHandler("cancelforward", cancelforward))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("setcount", setcount))
    app.add_handler(CommandHandler("setmessage", setmessage))
    app.add_handler(CommandHandler("setwelcome", setwelcome))
    app.add_handler(CommandHandler("viewwelcome", viewwelcome))
    app.add_handler(CommandHandler("listposts", listposts))
    app.add_handler(CommandHandler("removepost", removepost))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("postnow", postnow))
    app.add_handler(CommandHandler("approveall", approveall))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.FORWARDED, handle_forward))
    
    print("=" * 50)
    print(f"🤖 Bot Running! IST: {ist_str()}")
    print(f"📢 Channel: {CHANNEL_ID}")
    print("📋 /approveall - Approve ALL pending")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()
