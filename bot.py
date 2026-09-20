import asyncio
import os
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"
CHANNEL_ID = -1003550209252   # 🔥 APNA CHANNEL ID DAALO
ADMIN_ID = 7022423338
# -------------------------

MSG_FILE = "welcome.json"

# ---------- LOAD/SAVE ----------
def load_msg():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("message", "")
    return ""

def save_msg(msg):
    with open(MSG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"message": msg}, f, ensure_ascii=False, indent=2)

# ---------- IST TIME ----------
def ist_str():
    return (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

# ---------- 🔥 AUTO APPROVE + WELCOME DM ----------
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.chat_join_request.from_user
        chat = update.chat_join_request.chat

        # Approve karo
        await context.bot.approve_chat_join_request(
            chat_id=chat.id,
            user_id=user.id
        )
        print(f"✅ {user.first_name} approved at {ist_str()}!")

        # 🔥 Welcome DM bhejo (sirf member ke inbox me)
        msg = load_msg()
        if msg:
            try:
                final_msg = msg.format(
                    first_name=user.first_name or "Unknown",
                    username=user.username or "No Username",
                    user_id=user.id
                )
                await context.bot.send_message(
                    chat_id=user.id,
                    text=final_msg,
                    parse_mode=None
                )
                print(f"📤 Welcome DM sent to {user.first_name}!")
            except Exception as e:
                print(f"❌ Could not send DM: {e}")
        else:
            # Default welcome message
            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=f"🎉 Welcome {user.first_name}!\n\nThank you for joining our channel!\n🕐 {ist_str()}"
                )
                print(f"📤 Default welcome sent to {user.first_name}!")
            except:
                pass

    except Exception as e:
        print(f"❌ Auto-approve error: {e}")

# ---------- 🔥 SET WELCOME MESSAGE ----------
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ *Usage:*\n"
            "/setwelcome <your welcome message>\n\n"
            "*Example:*\n"
            "/setwelcome 🎉 Welcome {first_name}! Thanks for joining!",
            parse_mode="Markdown"
        )
        return

    msg = " ".join(context.args)
    # \n ko newline me convert karo
    msg = msg.replace("\\n", "\n")
    save_msg(msg)

    await update.message.reply_text(
        f"✅ *Welcome message saved!*\n\n```\n{msg}\n```",
        parse_mode="Markdown"
    )

# ---------- VIEW WELCOME ----------
async def viewwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    msg = load_msg()
    if not msg:
        await update.message.reply_text("📭 No welcome message set! Use /setwelcome")
        return

    await update.message.reply_text(
        f"📋 *Current Welcome Message:*\n\n```\n{msg}\n```",
        parse_mode="Markdown"
    )

# ---------- CLEAR ----------
async def clearwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    save_msg("")
    await update.message.reply_text("✅ Welcome message cleared!")

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    msg = load_msg()
    await update.message.reply_text(
        f"🤖 *Channel Welcome Bot*\n🕐 {ist_str()}\n\n"
        f"/setwelcome <msg> - Set welcome message\n"
        f"/viewwelcome - View welcome message\n"
        f"/clearwelcome - Clear message\n"
        f"/stats - Channel stats\n\n"
        f"📊 Welcome Message: {'✅ Set' if msg else '❌ Not set'}\n\n"
        f"📌 *Variables:*\n"
        f"{{first_name}} - Member name\n"
        f"{{username}} - Member username\n"
        f"{{user_id}} - Member ID",
        parse_mode="Markdown"
    )

# ---------- STATS ----------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    try:
        count = await context.bot.get_chat_member_count(CHANNEL_ID)
        msg = load_msg()
        await update.message.reply_text(
            f"📊 *Channel Stats*\n"
            f"👥 Members: {count}\n"
            f"📝 Welcome Message: {'✅ Set' if msg else '❌ Not set'}\n"
            f"🕐 {ist_str()}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # 🔥 Auto Approve + Welcome DM
    app.add_handler(ChatJoinRequestHandler(auto_approve))

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setwelcome", setwelcome))
    app.add_handler(CommandHandler("viewwelcome", viewwelcome))
    app.add_handler(CommandHandler("clearwelcome", clearwelcome))
    app.add_handler(CommandHandler("stats", stats))

    print("=" * 50)
    print("🤖 Channel Welcome Bot Running!")
    print(f"📢 Channel: {CHANNEL_ID}")
    print("✅ Auto-approve: ON")
    print("📤 Welcome DM: ON")
    print("=" * 50)

    app.run_polling()

if __name__ == "__main__":
    main()
