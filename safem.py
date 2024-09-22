import telebot
import json
import random
import os
import shutil
from telebot import types
from datetime import datetime, timedelta

# Bot token and Admin ID
TOKEN = '7251587760:AAFvBuFvbHpCGJ19Ah3KNswBeOuIxQWY3pw'
ADMIN_USER_ID = 5195444280

bot = telebot.TeleBot(TOKEN)

# File paths
data_file = 'data.json'
broadcast_file = 'broadcast.json'

# Load user data from JSON
def load_users():
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return {}

users = load_users()

# Load broadcast data
def load_broadcast_users():
    if os.path.exists(broadcast_file):
        with open(broadcast_file, 'r') as f:
            return json.load(f)
    return []

# Save users to JSON
def save_users():
    with open(data_file, 'w') as f:
        json.dump(users, f, indent=4)

# Save broadcast data
def save_broadcast_users(broadcast_users):
    with open(broadcast_file, 'w') as f:
        json.dump(broadcast_users, f, indent=4)

# Add user to broadcast list
def add_to_broadcast_list(user_id):
    broadcast_users = load_broadcast_users()
    if user_id not in broadcast_users:
        broadcast_users.append(user_id)
        save_broadcast_users(broadcast_users)

# Helper function to check if a user is an admin
def is_admin(user_id):
    return user_id == ADMIN_USER_ID

# Function to set the welcome message with any type of content
welcome_message_id = None

@bot.message_handler(commands=['setwelcome'])
def set_welcome(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "You are not authorized to set the welcome message.")
        return
    msg = bot.send_message(message.chat.id, "Please send the welcome message (text, image, video, etc.)")
    bot.register_next_step_handler(msg, save_welcome_message)

def save_welcome_message(message):
    global welcome_message_id
    welcome_message_id = message.message_id
    bot.send_message(message.chat.id, "Welcome message set successfully!")

# Broadcast functionality
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'You are not authorized to use this command.')
        return
    msg = bot.send_message(message.chat.id, 'What would you like to broadcast?')
    bot.register_next_step_handler(msg, handle_broadcast)

def handle_broadcast(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'You are not authorized to use this command.')
        return

    broadcast_message_id = message.message_id
    broadcast_users = load_broadcast_users()

    for user_id in broadcast_users:
        try:
            bot.copy_message(user_id, message.chat.id, broadcast_message_id)
        except telebot.apihelper.ApiTelegramException as e:
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user':
                broadcast_users.remove(user_id)
            else:
                print(f'Error sending message to {user_id}: {e}')
    
    save_broadcast_users(broadcast_users)  
    bot.send_message(message.chat.id, 'Broadcast message sent to all users.')

# Daily bonus functionality
def add_daily_bonus(user_id):
    bonus = random.randint(1, 3)
    users[user_id]['balance'] += bonus
    users[user_id]['last_bonus_claim'] = datetime.now().isoformat()
    save_users()
    return bonus

@bot.message_handler(func=lambda message: message.text == "💳Claim Daily Bonus")
def claim_daily_bonus(message):
    user_id = message.from_user.id
    if str(user_id) not in users:
        users[str(user_id)] = {'balance': 0, 'referred_by': None, 'last_bonus_claim': None}
    
    last_claim_time = users[str(user_id)].get('last_bonus_claim')
    if last_claim_time:
        last_claim_time = datetime.fromisoformat(last_claim_time)
        if datetime.now() - last_claim_time < timedelta(days=1):
            remaining_time = timedelta(days=1) - (datetime.now() - last_claim_time)
            bot.send_message(message.chat.id, f"You need to wait for a little while to claim again. Remaining time: {remaining_time}.")
            return
    
    bonus = add_daily_bonus(str(user_id))
    bot.send_message(message.chat.id, f"Congratulations! You received {bonus} coins as a daily bonus! Your new balance is {users[str(user_id)]['balance']} coins.")

# Referral system
def generate_referral_link(user_id):
    referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    return referral_link

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    referred_by = None

    if user_id not in users:
        if len(message.text.split()) > 1:
            referred_by = message.text.split()[1]
            if referred_by != user_id and referred_by in users:
                users[user_id] = {'balance': 0, 'referred_by': referred_by, 'referral_rewarded': False}
            else:
                users[user_id] = {'balance': 0, 'referred_by': None}
        else:
            users[user_id] = {'balance': 0, 'referred_by': None}
        
        save_users()  
        add_to_broadcast_list(user_id)

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Join Haxkx", url="https://t.me/Haxkx")
    btn2 = types.InlineKeyboardButton("Join Dark Web", url="https://t.me/darkwebs01")
    check_btn = types.InlineKeyboardButton("Check", callback_data="check_membership")
    keyboard.add(btn1, btn2)
    keyboard.add(check_btn)
    bot.send_photo(message.chat.id, "https://envs.sh/PXc.jpg", "Please join all channels to proceed:", reply_markup=keyboard)

# Membership verification callback
@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_membership(call):
    user_id = call.from_user.id
    try:
        member_in_channel_1 = bot.get_chat_member("@Haxkx", user_id)
        member_in_channel_2 = bot.get_chat_member("@darkwebs01", user_id)
        
        if member_in_channel_1.status in ['member', 'administrator', 'creator'] and \
           member_in_channel_2.status in ['member', 'administrator', 'creator']:
            bot.send_message(call.message.chat.id, "Thank you for joining all channels!")
            
            if users[str(call.from_user.id)]['referred_by'] and not users[users[str(call.from_user.id)]['referred_by']].get('referral_rewarded', False):
                referrer_id = users[str(call.from_user.id)]['referred_by']
                users[referrer_id]['balance'] += 1
                users[referrer_id]['referral_rewarded'] = True  
                save_users()  

            if welcome_message_id:
                bot.copy_message(call.message.chat.id, ADMIN_USER_ID, welcome_message_id)
            else:
                bot.send_message(call.message.chat.id, "Welcome to the bot!")
            
            send_menu_buttons(call.message)
        else:
            bot.send_message(call.message.chat.id, "You have not joined all channels. Please do so and click Check again.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error checking channel membership: {e}")

# Function to display menu buttons after verification
def send_menu_buttons(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💸My Balance")
    btn2 = types.KeyboardButton("💳Claim Daily Bonus")
    btn3 = types.KeyboardButton("🙋Referral Link")
    btn4 = types.KeyboardButton("💅Create Follower Bot")
    btn5 = types.KeyboardButton("🤭Statistics")
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, "Have a Great day!", reply_markup=keyboard)

# Handle "💸My Balance" button click
@bot.message_handler(func=lambda message: message.text == "💸My Balance")
def my_balance(message):
    user_id = str(message.from_user.id)
    user_info = users.get(user_id, None)

    if user_info:
        user_name = message.from_user.first_name
        user_username = message.from_user.username if message.from_user.username else "Not Set"
        balance = user_info.get('balance', 0)
        referred_by = user_info.get('referred_by', "None")
        last_bonus_claim = user_info.get('last_bonus_claim', "Not Claimed")

        user_details = (
            f"💵Balance: {balance} coins\n"
            f"🙋User ID: {user_id}\n"
            f"🏷️Name: {user_name}\n"
            f"💅Username: @{user_username}\n"
            f"👾Referred By: {referred_by}\n"
            f"😭Last Bonus Claim: {last_bonus_claim}"
        )
        bot.send_message(message.chat.id, user_details)
    else:
        bot.send_message(message.chat.id, "User data not found.")

@bot.message_handler(func=lambda message: message.text == "🙋Referral Link")
def send_referral_link(message):
    user_id = str(message.from_user.id)
    referral_link = generate_referral_link(user_id)
    bot.send_message(message.chat.id, f"Here is your referral link: \n\n{referral_link}\n\nYou will get 1 coin per referral. Share more to earn more!")

@bot.message_handler(func=lambda message: message.text == "💅Create Follower Bot")
def handle_create_bot(message):
    user_id = str(message.from_user.id)
    balance = users.get(user_id, {}).get('balance', 0)
    
    if balance < 10:
        bot.send_message(message.chat.id, "You need 10 coins to create your own bot.")
        return

    bot.send_message(message.chat.id, "Please provide your fake account username (without @):")
    bot.register_next_step_handler(message, process_bot_username)

def process_bot_username(message):
    user_id = str(message.from_user.id)
    username = message.text.strip()

    bot.send_message(message.chat.id, "Please provide the password for that fake account:")
    bot.register_next_step_handler(message, process_bot_password, username)

def process_bot_password(message, username):
    user_id = str(message.from_user.id)
    password = message.text.strip()

    bot.send_message(message.chat.id, "Now, please provide the target username (without @) where you want followers:")
    bot.register_next_step_handler(message, create_bot_folder, username, password)

def create_bot_folder(message, username, password):
    user_id = str(message.from_user.id)
    target_username = message.text.strip()

    user_folder = username  # Use the username directly without "@"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    shutil.copy('indo.py', os.path.join(user_folder, 'run.py'))

    with open(os.path.join(user_folder, 'run.py'), 'r') as file:
        code = file.read()

    code = code.replace('userid_by_tanji', password)
    code = code.replace('username_by_tanji', username)
    code = code.replace('bot_token_by_tanji', target_username)

    with open(os.path.join(user_folder, 'run.py'), 'w') as file:
        file.write(code)

    users[user_id]['balance'] -= 10
    save_users()
    bot.send_message(message.chat.id, "Your script is ready! \n \n check your followers in Instagram \n \n if you dont received followers than check your fake account id pass and login and check if it ask to approval \n \n 10 coins has been deducted.")

@bot.message_handler(func=lambda message: message.text == "🤭Statistics")
def show_statistics(message):
    total_users = len(users)
    total_funds = sum(user['balance'] for user in users.values())
    bots_created = sum(1 for user in users.values() if 'referred_by' in user and user['referred_by'])

    stats_message = (
        f"🙋Total Users: {total_users}\n"
        f"💵Total Funds: {total_funds} coins\n"
        f"👾Total Scripts Created: {bots_created}"
    )
    bot.send_message(message.chat.id, stats_message)

# Admin command to add funds
@bot.message_handler(commands=['addfund'])
def add_fund(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return

    msg = bot.send_message(message.chat.id, "Please send the user ID of the user to add funds.")
    bot.register_next_step_handler(msg, process_add_fund_userid)

def process_add_fund_userid(message):
    target_user_id = message.text.strip()
    target_user_id = str(target_user_id)

    if target_user_id not in users:
        bot.send_message(message.chat.id, "User ID not found.")
        return

    msg = bot.send_message(message.chat.id, "Please specify the amount of coins to add.")
    bot.register_next_step_handler(msg, process_add_fund_amount, target_user_id)

def process_add_fund_amount(message, target_user_id):
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Invalid amount. Please enter a valid number.")
        return

    if amount <= 0:
        bot.send_message(message.chat.id, "Amount must be greater than zero.")
        return

    users[target_user_id]['balance'] += amount
    save_users()

    bot.send_message(target_user_id, f"Admin has added {amount} coins to your balance.")
    bot.send_message(message.chat.id, f"Added {amount} coins to user {target_user_id}'s balance.")

# Start polling with extended timeout
bot.polling(none_stop=True, interval=0, timeout=60)
