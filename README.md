
# 🌍 EthnoGuessr Discord Bot

A fun and competitive GeoGuessr-style bot for Discord, built to track daily scores, announce winners, and crown the **King of the Racers** 👑.

---

## ✨ Features

- 📊 Auto-records EthnoGuessr scores from messages
- 🏆 Announces daily winners with role assignment
- 🧾 Commands to view leaderboards and king history
- 💾 Persists scores, wins, and config across restarts
- 🔐 Role-restricted admin/test features

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/eweiland76/ethnoguessr.git
cd ethnoguessr
```

### 2. Set Up Environment

Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

> ⚠️ Never commit your `.env` file to GitHub!

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python bot/main.py
```

---

## 🧠 Bot Commands

| Command                      | Description                                           |
|-----------------------------|-------------------------------------------------------|
| `!ethnoboard`               | Show today’s leaderboard                             |
| `!topkings`                 | Show all-time kings                                  |
| `!testscore <avg> <best>`   | Test submit a score (authorized users)              |
| `!addscore @user <avg> <best>` | Manually add a score (authorized users)         |
| `!deletescore @user`        | Remove a user's score                                |
| `!testreset`                | Force a winner announcement & reset scores (test)    |
| `!channel <announce_id> <score_id>` | Set announcement and score channel IDs    |
| `!johnny`                   | Show all available commands                          |

---

## 📁 Folder Structure

```
ethnoguessr/
├── bot/
│   ├── main.py                # Main bot logic
│   └── (optional utils files: storage.py, config.py, etc.)
├── data/                      # Score & config files saved here
│   ├── scores_<guild>.txt
│   ├── king_wins_<guild>.txt
│   └── guild_configs.txt
├── .env                       # Discord token (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📦 Dependencies

- discord.py
- apscheduler
- python-dotenv

Install via:

```bash
pip install -r requirements.txt
```

---

## 🛡 License

MIT License. Use, modify, and enhance freely!

---

## 🛠 Built With Love

Made for EthnoGuessr players who take competition (way too) seriously.

👑 Long live the King.
