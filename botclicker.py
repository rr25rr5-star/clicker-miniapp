from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.utils import executor
from flask import Flask, request, jsonify
import threading

API_TOKEN = "8416665434:AAH1vf8VD0f1xdvjtakEF0GPRXrvCq1AvLg"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# In-memory database (real loyihada PostgreSQL yoki MongoDB ishlatish tavsiya qilinadi)
users_data = {}

# /start komandasi
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "Play Clicker", web_app=WebAppInfo(url="https://rr25rr5-star.github.io/clicker-miniapp/")
        )
    )
    await message.answer("Clicker o‘yiningizni boshlang!", reply_markup=keyboard)

# Flask backend Mini App uchun
app = Flask(__name__)

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    user_id = str(data["user_id"])
    coins_add = data.get("coins_add", 0)
    progress_change = data.get("progress_change", 0)

    if user_id not in users_data:
        users_data[user_id] = {"coins": 0, "progress": 1000, "multiplier": 1}

    users_data[user_id]["coins"] += coins_add * users_data[user_id]["multiplier"]
    users_data[user_id]["progress"] += progress_change

    # Progress max/min limits
    if users_data[user_id]["progress"] > 1000:
        users_data[user_id]["progress"] = 1000
    if users_data[user_id]["progress"] < 0:
        users_data[user_id]["progress"] = 0

    return jsonify(users_data[user_id])

@app.route("/leaderboard")
def leaderboard():
    # Reyting coins bo'yicha
    sorted_users = sorted(users_data.items(), key=lambda x: x[1]["coins"], reverse=True)
    return jsonify([{ "user_id": k, **v } for k,v in sorted_users])

def start_flask():
    app.run(port=5000)

threading.Thread(target=start_flask).start()
executor.start_polling(dp, skip_updates=True)
