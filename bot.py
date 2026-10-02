import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8835401302:AAFc4LNwV-XSqQIuvGv87pcR82abLElKWrM"

# Mandatory channels for start
CHANNELS = ["@PlusTechHub", "@Alphatech_earn", "@Eth_online_job"]

# Temporary database for users (balance, tasks, referrals)
user_data = {}

async def check_subscription(user_id, bot):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if user_id not in user_data:
        user_data[user_id] = {"balance": 0.0, "completed_tasks": [], "referred_count": 0}

    is_subscribed = await check_subscription(user_id, context.bot)

    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("Join Channel 1", url="https://t.me/PlusTechHub")],
            [InlineKeyboardButton("Join Channel 2", url="https://t.me/Alphatech_earn")],
            [InlineKeyboardButton("Join Channel 3", url="https://t.me/Eth_online_job")],
            [InlineKeyboardButton("✅ Verify", callback_data="verify_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome! To use this bot, you must join the following channels first:\n\n1. @PlusTechHub\n2. @Alphatech_earn\n3. @Eth_online_job\n\nAfter joining, click 'Verify'.",
            reply_markup=reply_markup
        )
    else:
        await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="balance"), InlineKeyboardButton("👥 Referral", callback_data="referral")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"), InlineKeyboardButton("📋 Tasks", callback_data="tasks")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info"), InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "Welcome to the bot! Choose an option below:"
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"balance": 0.0, "completed_tasks": [], "referred_count": 0}

    if query.data == "verify_sub":
        is_subscribed = await check_subscription(user_id, context.bot)
        if is_subscribed:
            await query.message.delete()
            await show_main_menu(update, context)
        else:
            await query.answer("You have not joined all channels yet!", show_alert=True)

    elif query.data == "balance":
        bal = user_data[user_id]["balance"]
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await query.message.edit_text(f"Your current balance is: {bal} Birr", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "referral":
        ref_count = user_data[user_id]["referred_count"]
        ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        text = f"👥 Referral Program\n\nInvite your friends and earn 3 Birr per referral!\n\nYour Referral Link:\n{ref_link}\n\nTotal Referred: {ref_count} users"
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "tasks":
        keyboard = [
            [InlineKeyboardButton("Task 1: Join Channel (+3 Birr)", callback_data="task_1")],
            [InlineKeyboardButton("Task 2: Join Channel (+3 Birr)", callback_data="task_2")],
            [InlineKeyboardButton("Task 3: Join Channel (+3 Birr)", callback_data="task_3")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        await query.message.edit_text("Available Tasks (Each task gives 3 Birr):", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in ["task_1", "task_2", "task_3"]:
        task_names = {"task_1": "@money_power54", "task_2": "@faron_tech", "task_3": "@Hbret_earnn"}
        channel_links = {"task_1": "https://t.me/money_power54", "task_2": "https://t.me/faron_tech", "task_3": "https://t.me/Hbret_earnn"}
        
        if query.data not in user_data[user_id]["completed_tasks"]:
            keyboard = [
                [InlineKeyboardButton("🔗 Go to Channel", url=channel_links[query.data])],
                [InlineKeyboardButton("✅ Confirm & Claim 3 Birr", callback_data=f"claim_{query.data}")],
                [InlineKeyboardButton("🔙 Back", callback_data="tasks")]
            ]
            await query.message.edit_text(f"Join this channel: {task_names[query.data]}\nAfter joining, click 'Confirm & Claim 3 Birr'.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.answer("You have already completed this task!", show_alert=True)

    elif query.data.startswith("claim_"):
        actual_task = query.data.replace("claim_", "")
        if actual_task not in user_data[user_id]["completed_tasks"]:
            user_data[user_id]["balance"] += 3.0
            user_data[user_id]["completed_tasks"].append(actual_task)
            await query.answer("Congratulations! You earned 3 Birr.", show_alert=True)
            await show_main_menu(update, context)
        else:
            await query.answer("You have already claimed this task!", show_alert=True)

    elif query.data == "withdraw":
        keyboard = [
            [InlineKeyboardButton("Telebirr", callback_data="wd_telebirr"), InlineKeyboardButton("CBE", callback_data="wd_cbe")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        await query.message.edit_text("Select your withdrawal method (Telebirr / CBE):", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in ["wd_telebirr", "wd_cbe"]:
        bal = user_data[user_id]["balance"]
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        if bal < 60.0:
            await query.message.edit_text(f"Your current balance is {bal} Birr.\nMinimum withdrawal threshold is 60 Birr. You need {60.0 - bal} Birr more to withdraw.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.message.edit_text(f"Your balance is {bal} Birr. Withdrawal request submitted successfully! Please wait for admin approval.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "support":
        keyboard = [
            [InlineKeyboardButton("Contact Support", url="https://t.me/YourAdminUsername")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        await query.message.edit_text("If you have any questions or issues, contact our support admin below:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "info":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await query.message.edit_text("This bot allows you to earn rewards by completing tasks and referrals. Minimum withdrawal is 60 Birr.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "main_menu":
        await show_main_menu(update, context)

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
