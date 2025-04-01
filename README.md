
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

## 🚀 Setup & Usage

### 1. Clone the Repo

```bash
git clone https://github.com/eweiland76/ethnoguessr.git
cd ethnoguessr
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

> ⚠️ Do **not** commit your `.env` file to GitHub.

### 4. Run the Bot

```bash
python ethnoguessr_bot.py
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

## 🗃 Persistence

All scores, wins, and settings are saved to `.txt` files:

- `scores_<guild_id>.txt`
- `king_wins_<guild_id>.txt`
- `guild_configs.txt`

These are automatically reloaded when the bot restarts.

---

## 📦 Dependencies

```
discord.py
apscheduler
python-dotenv
```

---

## 🛡 License

MIT License. Use, modify, and enhance freely.

---

## 👑 Long live the King.
