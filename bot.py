import asyncio
import os
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"

# 🔥 DONO ID DAALO
CHANNEL_ID = -1003550209252   # Channel ID
GROUP_ID = -1003550209252     # Group ID

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

# ---------- 🔥 AUTO APPROVE (Naye Requests) ----------
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.chat_join_request.from_user
        chat = update.chat_join_request.chat

        print(f"📥 New join request: {user.first_name} for {chat.id}")

        # Approve karo
        await context.bot.approve_chat_join_request(
            chat_id=chat.id,
            user_id=user.id
        )
        print(f"✅ {user.first_name} approved!")

        # Welcome DM bhejo
        await send_welcome_dm(context, user)

    except Exception as e:
        print(f"❌ Auto-approve error: {e}")

# ---------- 🔥 SEND WELCOME DM ----------
async def send_welcome_dm(context, user):
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
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"🎉 Welcome {user.first_name}!\n\nThank you for joining!\n🕐 {ist_str()}"
            )
            print(f"📤 Default welcome sent!")
        except:
            pass

# ---------- 🔥 APPROVE ALL PENDING REQUESTS ----------
async def approveall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    msg = await update.message.reply_text("📥 Fetching all pending join requests...")

    total_approved = 0
    total_failed = 0

    # 🔥 Dono IDs ke liye check karo
    for chat_id in [CHANNEL_ID, GROUP_ID]:
        try:
            pending = await context.bot.get_chat_join_requests(chat_id)
            requests_list = []
            async for req in pending:
                requests_list.append(req)

            if not requests_list:
                print(f"📭 No pending requests for {chat_id}")
                continue

            print(f"📊 Found {len(requests_list)} requests for {chat_id}")

            for req in requests_list:
                try:
                    user = req.from_user
                    await context.bot.approve_chat_join_request(
                        chat_id=chat_id,
                        user_id=user.id
                    )
                    total_approved += 1
                    print(f"✅ Approved: {user.first_name}")

                    # Welcome DM bhejo
                    await send_welcome_dm(context, user)
                    await asyncio.sleep(0.5)

                except Exception as e:
                    total_failed += 1
                    print(f"❌ Failed to approve: {e}")

        except Exception as e:
            print(f"❌ Error for {chat_id}: {e}")

    await msg.edit_text(
        f"✅ *Approve All Complete!*\n\n"
        f"✅ Approved: {total_approved}\n"
        f"❌ Failed: {total_failed}\n"
        f"🕐 {ist_str()}",
        parse_mode="Markdown"
    )

# ---------- 🔥 SET WELCOME ----------
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ /setwelcome <message>\n\n"
            "Variables:\n"
            "{first_name} - Member name\n"
            "{username} - Username\n"
            "{user_id} - ID"
        )
        return

    msg = " ".join(context.args)
    msg = msg.replace("\\n", "\n")
    save_msg(msg)

    await update.message.reply_text(
        f"✅ *Welcome message saved!*\n\n```\n{msg}\n```",
        parse_mode="Markdown"
    )

async def viewwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    msg = load_msg()
    if not msg:
        await update.message.reply_text("📭 No welcome message set!")
        return

    await update.message.reply_text(
        f"📋 *Welcome Message:*\n\n```\n{msg}\n```",
        parse_mode="Markdown"
    )

async def clearwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    save_msg("")
    await update.message.reply_text("✅ Cleared!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    msg = load_msg()
    await update.message.reply_text(
        f"🤖 *Bot Running*\n🕐 {ist_str()}\n\n"
        f"/setwelcome <msg> - Set welcome message\n"
        f"/viewwelcome - View message\n"
        f"/clearwelcome - Clear message\n"
        f"/approveall - Approve ALL pending requests 🔥\n"
        f"/stats - Stats\n\n"
        f"📊 Welcome: {'✅ Set' if msg else '❌ Not set'}",
        parse_mode="Markdown"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    try:
        ch_count = await context.bot.get_chat_member_count(CHANNEL_ID)
        gr_count = await context.bot.get_chat_member_count(GROUP_ID)
        msg = load_msg()
        await update.message.reply_text(
            f"📊 *Stats*\n"
            f"📢 Channel: {ch_count}\n"
            f"👥 Group: {gr_count}\n"
            f"📝 Welcome: {'✅' if msg else '❌'}\n"
            f"🕐 {ist_str()}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Auto Approve
    app.add_handler(ChatJoinRequestHandler(auto_approve))

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setwelcome", setwelcome))
    app.add_handler(CommandHandler("viewwelcome", viewwelcome))
    app.add_handler(CommandHandler("clearwelcome", clearwelcome))
    app.add_handler(CommandHandler("approveall", approveall))  # 🔥 New
    app.add_handler(CommandHandler("stats", stats))

    print("=" * 50)
    print("🤖 Bot Running!")
    print(f"📢 Channel: {CHANNEL_ID}")
    print(f"👥 Group: {GROUP_ID}")
    print("✅ Auto-approve: ON")
    print("📤 Welcome DM: ON")
    print("📋 /approveall - Approve ALL pending")
    print("=" * 50)

    app.run_polling()

if __name__ == "__main__":
    main()
