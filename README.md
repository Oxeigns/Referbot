

# Refer & Earn Telegram Bot

A modern **Refer & Earn Telegram Bot** built with [Pyrogram](https://docs.pyrogram.org/) and MongoDB.  
This bot allows users to join required channels, refer friends, earn points, and request withdrawals – with a dynamic admin panel for the owner.

---

## 👤 Bot Owner
**Owner:** [@Oxeign](https://t.me/Oxeign)

---

## ✨ Features

1. **Stylish Start Panel**
   - Sends a **banner image** with a **modern caption** (HTML styled).
   - Grid buttons:
     - 💎 Referral | 💰 Withdraw
     - ✅ Verify Join
     - 📊 My Points | 🏆 Top Users
     - 📜 Help | 💬 Support
     - 🛠 Admin Panel (only for OWNER)

2. **Referral System**
   - Every user gets a **unique referral link**.
   - 3 points per referral.
   - Minimum 15 points required for withdrawal.

3. **Channel Join Verification**
   - Verifies that users have joined all required channels using `get_chat_member`.
   - Channel links are configured directly in the code.

4. **Admin Features**
   - Broadcast messages to all users.
   - Approve/reject withdrawal requests.
   - View user points.

5. **Logging**
   - Logs each new user in a **LOG_GROUP** (username, ID, referral).
   - Sends a summary to the log group when a withdrawal is approved.

6. **Database**
   - MongoDB with motor.
   - Collections:
     - `users` – user data and points
     - `referrals` – referral tracking

---

## 🖼 Bot UI Style

**Caption Example:**

🎯 Welcome to the Refer & Earn Bot

Invite friends and earn rewards!

1 Referral = 3 Points
Minimum Withdrawal: 15 Points
bot by @oxeign on Telegram a famous vc fyter , carder , hacker , android expert one of the most popualar person on telegeram his instagram id is same as telegram

**Button Layout:**

[ 💎 Referral  |  💰 Withdraw ]
[ ✅ Verify Join ]
[ 📊 My Points | 🏆 Top Users ]
[ 📜 Help      | 💬 Support ]
[ 🛠 Admin Panel (Owner only) ]

---

## 📂 Folder Structure

Dockerfile
mybot/
├── Dockerfile
├── Procfile
├── render.yaml
├── start.sh
├── requirements.txt
├── config.py
├── main.py
├── .env
├── plugins/
│   ├── start.py
│   ├── referral.py
│   ├── verify.py
│   ├── admin.py
│   ├── broadcast.py
└── database/
├── mongo.py

---

## ⚙️ Environment Variables (.env)

API_ID=123456
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=123456789
LOG_GROUP=-1001234567890
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname
CALLBACK_SECRET=change_me_to_a_long_random_string
LOG_LEVEL=INFO
---

`LOG_LEVEL` controls the verbosity of log output. Use `DEBUG` while
troubleshooting, otherwise keep the default `INFO` value.

`CALLBACK_SECRET` secures inline button payloads. When it is not provided the
application will generate a temporary secret on startup, but this value changes
on every deploy. Set it explicitly to keep callbacks valid across restarts.

---

## 🚀 Deployment

### Local Setup
```bash
git clone https://github.com/your-repo.git
cd mybot
pip install -r requirements.txt
cp .env.example .env
# Fill .env with your credentials
python -m mybot.main

Render / Railway Deployment
	•	Add environment variables in the dashboard.
	•	Deploy directly from GitHub.
	•	Procfile and render.yaml are already configured.

⸻

🛠 Tech Stack
	•	Pyrogram
	•	MongoDB
	•	Docker
	•	Render / Railway

⸻

🔒 Security
        •       Only the Owner (OWNER_ID) can:
        •       Broadcast messages
        •       Manage withdrawals and points

⸻

📧 Support

For help, contact @Oxeign.

⸻

License

This project is licensed under the MIT License

## Local configuration

Copy `mybot/.env.example` to `mybot/.env` and fill in your own values. A previously tracked `.env` has been removed; rotate any real credentials that were stored there, since Git history still contains the old file.
