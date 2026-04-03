# © Telegram : @KingVJ01 , GitHub : @VJBots
# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import requests
from motor.motor_asyncio import AsyncIOMotorClient
from plugins.clone import mongo_db

# -------------------------
# Shortener Function
# -------------------------
async def get_short_link(user, link, second=False):
    """
    Generate a short link using either the first or second shortener.
    """
    if second:
        api_key = user.get("shortener_api2")
        base_site = user.get("base_site2")
    else:
        api_key = user.get("shortener_api")
        base_site = user.get("base_site")

    if not api_key or not base_site:
        return link  # fallback to original link

    try:
        response = requests.get(f"https://{base_site}/api?api={api_key}&url={link}")
        data = response.json()
        if response.status_code == 200 and data.get("status") == "success":
            return data.get("shortenedUrl", link)
        else:
            return link
    except Exception as e:
        print(f"Shortener error: {e}")
        return link

# -------------------------
# User Functions
# -------------------------
async def get_user(user_id):
    """
    Fetch user record from MongoDB. If not found, create a new one.
    """
    user_id = int(user_id)
    user = mongo_db.user.find_one({"user_id": user_id})
    if not user:
        res = {
            "user_id": user_id,
            "shortener_api": None,
            "base_site": None,
            "shortener_api2": None,
            "base_site2": None
        }
        mongo_db.user.insert_one(res)
        user = mongo_db.user.find_one({"user_id": user_id})
    return user

async def update_user_info(user_id, value: dict):
    """
    Update user record in MongoDB with new values.
    """
    user_id = int(user_id)
    myquery = {"user_id": user_id}
    newvalues = {"$set": value}
    mongo_db.user.update_one(myquery, newvalues)
