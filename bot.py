import asyncio
import os
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = "8773675256:AAG4iVamzSa3WxZzBNCysfT7yETKdOiziB8"
GROUP_ID = -1003915549696  
ADMIN_ID = 8961906024


MSG_FILE = "messages.json"

# ---------- LOAD/SAVE ----------
def load_messages():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("messages", [])
    return []

def save_messages(messages):
    with open(MSG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"messages": messages}, f, ensure_ascii=False, indent=2)

# ---------- IST TIME ----------
def ist_str():
    return (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

# ---------- 🔥 NEW MEMBER ----------
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    if update.message.chat.id != GROUP_ID:
        return

    messages = load_messages()
    if not messages:
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue

        print(f"🆕 New member: {member.first_name}")

        # 🔥 Saare messages bhejo
        for msg in messages:
            try:
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=msg,
                    parse_mode=None
                )
                print("📤 Message sent!")
                await asyncio.sleep(2)  # 2 second gap
            except Exception as e:
                print(f"❌ Error: {e}")

# ---------- 🔥 SET MESSAGE ----------
async def setmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    # Agar command ke saath kuch likha hai toh wahi save karo
    if context.args:
        msg = " ".join(context.args)
        msg = msg.replace("\\n", "\n")
        
        # 🔥 Check if message contains separator "---"
        if "---" in msg:
            parts = msg.split("---")
            messages = [p.strip() for p in parts if p.strip()]
            save_messages(messages)
            await update.message.reply_text(
                f"✅ *{len(messages)} messages saved!*\n\n"
                f"📋 *Preview:*\n" + "\n\n---\n\n".join([f"Msg {i+1}:\n{m}" for i, m in enumerate(messages)]),
                parse_mode="Markdown"
            )
        else:
            save_messages([msg])
            await update.message.reply_text(
                f"✅ *Message saved!*\n\n```\n{msg}\n```",
                parse_mode="Markdown"
            )
        return

    # Multi-line mode
    context.user_data['collecting'] = True
    context.user_data['temp_msgs'] = []
    context.user_data['current_msg'] = []

    await update.message.reply_text(
        "📝 *Send your messages one by one.*\n"
        "Type your message and send.\n"
        "Use `---` to separate messages.\n"
        "When done, type: `/done`\n"
        "Cancel: `/cancel`",
        parse_mode="Markdown"
    )

# ---------- COLLECT ----------
async def collect_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.user_data.get('collecting'):
        return

    text = update.message.text

    if text == "/done":
        temp_msgs = context.user_data.get('temp_msgs', [])
        if temp_msgs:
            save_messages(temp_msgs)
            preview = "\n\n---\n\n".join([f"Msg {i+1}:\n{m}" for i, m in enumerate(temp_msgs)])
            await update.message.reply_text(
                f"✅ *{len(temp_msgs)} messages saved!*\n\n{preview}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ No messages to save!")
        context.user_data['collecting'] = False
        context.user_data['temp_msgs'] = []
        context.user_data['current_msg'] = []
        return

    if text == "/cancel":
        context.user_data['collecting'] = False
        context.user_data['temp_msgs'] = []
        context.user_data['current_msg'] = []
        await update.message.reply_text("❌ Cancelled!")
        return

    # 🔥 Check if it's a separator
    if text == "---":
        # Save current message
        current_msg = context.user_data.get('current_msg', [])
        if current_msg:
            context.user_data['temp_msgs'].append("\n".join(current_msg))
            context.user_data['current_msg'] = []
            await update.message.reply_text(f"✅ Message {len(context.user_data['temp_msgs'])} saved! Send next or /done")
        else:
            await update.message.reply_text("⚠️ No message to save! Type your message first.")
        return

    # Add line to current message
    context.user_data['current_msg'].append(text)
    await update.message.reply_text(f"✅ Line added to current message!")

# ---------- VIEW ----------
async def viewmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    messages = load_messages()
    if not messages:
        await update.message.reply_text("📭 No messages set! Use /setmsg")
        return

    preview = "\n\n---\n\n".join([f"📋 Msg {i+1}:\n{m}" for i, m in enumerate(messages)])
    
    if len(preview) > 4000:
        preview = preview[:4000] + "\n\n... (truncated)"
    
    await update.message.reply_text(
        f"📋 *Current Messages:*\n\n{preview}\n\n📊 Total: {len(messages)}",
        parse_mode="Markdown"
    )

# ---------- CLEAR ----------
async def clearmmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    save_messages([])
    await update.message.reply_text("✅ All messages cleared!")

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    messages = load_messages()
    await update.message.reply_text(
        f"🤖 *Group Welcome Bot*\n🕐 {ist_str()}\n\n"
        f"/setmsg <message> - Set message (use \\n for newline)\n"
        f"/setmsg - Multi-line mode\n"
        f"/viewmsg - View messages\n"
        f"/clearmmsg - Clear messages\n"
        f"/stats - Group stats\n\n"
        f"📊 Messages: {len(messages)}",
        parse_mode="Markdown"
    )

# ---------- STATS ----------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    try:
        count = await context.bot.get_chat_member_count(GROUP_ID)
        messages = load_messages()
        await update.message.reply_text(
            f"📊 *Group Stats*\n👥 Members: {count}\n📝 Messages: {len(messages)}\n🕐 {ist_str()}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setmsg", setmsg))
    app.add_handler(CommandHandler("viewmsg", viewmsg))
    app.add_handler(CommandHandler("clearmmsg", clearmmsg))
    app.add_handler(CommandHandler("stats", stats))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_msg))

    print("=" * 50)
    print("🤖 Group Welcome Bot Running!")
    print(f"📢 Group: {GROUP_ID}")
    print("📋 /setmsg - Set messages")
    print("=" * 50)

    app.run_polling()

if __name__ == "__main__":
    main()
