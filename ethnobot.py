import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import re
import os
import pytz
from pytz import utc
from datetime import datetime, timedelta, timezone


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
scheduler = AsyncIOScheduler()

bot.guild_configs = {}
ETHNO_KING_ROLE_ID = xxx
AUTHORIZED_ROLE_ID = xxx
UNAUTHORIZED_IMAGE_URL = "https://i.imgur.com/02JdB5S.gif"

ethno_scores = {}
king_wins = {}

# File utils
def get_score_file(guild_id): return f"scores_{guild_id}.txt"
def get_win_file(guild_id): return f"king_wins_{guild_id}.txt"
def get_config_file(): return "guild_configs.txt"

def save_scores(guild_id):
    if guild_id not in ethno_scores:
        return
    with open(get_score_file(guild_id), "w") as f:
        for user_id, data in ethno_scores[guild_id].items():
            f.write(f"{user_id},{data['average']},{data['best']},{data['name']}\n")

def load_scores(guild_id):
    ethno_scores[guild_id] = {}
    path = get_score_file(guild_id)
    if not os.path.exists(path): return
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 4:
                uid, avg, best, name = parts[0], int(parts[1]), int(parts[2]), ','.join(parts[3:])
                ethno_scores[guild_id][int(uid)] = {'average': avg, 'best': best, 'name': name}

def save_king_wins(guild_id):
    if guild_id not in king_wins:
        return
    with open(get_win_file(guild_id), "w") as f:
        for uid, wins in king_wins[guild_id].items():
            f.write(f"{uid},{wins}\n")

def load_king_wins(guild_id):
    king_wins[guild_id] = {}
    path = get_win_file(guild_id)
    if not os.path.exists(path): return
    with open(path, "r") as f:
        for line in f:
            uid, wins = line.strip().split(',')
            king_wins[guild_id][int(uid)] = int(wins)

def save_guild_configs():
    with open(get_config_file(), "w") as f:
        for gid, config in bot.guild_configs.items():
            f.write(f"{gid},{config['announce_channel_id']},{config['score_channel_id']}\n")

def load_guild_configs():
    if not os.path.exists(get_config_file()):
        return
    with open(get_config_file(), "r") as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 3:
                gid, announce_id, score_id = int(parts[0]), int(parts[1]), int(parts[2])
                bot.guild_configs[gid] = {
                    "announce_channel_id": announce_id,
                    "score_channel_id": score_id
                }
# --- Role/Authorization Helpers ---
def has_authorized_role(ctx):
    return any(role.id == AUTHORIZED_ROLE_ID for role in ctx.author.roles) or ctx.author.id == xxx

async def unauthorized_response(ctx):
    await ctx.send("⛔ You are not authorized to use this command.")
    await ctx.send(UNAUTHORIZED_IMAGE_URL)

# --- Winner Announcement ---
async def announce_ethno_winner(guild_id):
    guild = bot.get_guild(guild_id)
    if not guild or not ethno_scores.get(guild_id): return

    load_king_wins(guild_id)
    king_wins.setdefault(guild_id, {})

    top_user_id, top_data = max(ethno_scores[guild_id].items(), key=lambda x: x[1]['average'])
    top_member = guild.get_member(top_user_id) or await guild.fetch_member(top_user_id)

    king_role = guild.get_role(ETHNO_KING_ROLE_ID)
    if king_role:
        for m in guild.members:
            if king_role in m.roles and m.id != top_user_id:
                await m.remove_roles(king_role)
        await top_member.add_roles(king_role)

    king_wins[guild_id][top_user_id] = king_wins[guild_id].get(top_user_id, 0) + 1
    save_king_wins(guild_id)

    announce_channel_id = bot.guild_configs.get(guild_id, {}).get("announce_channel_id")
    channel = bot.get_channel(announce_channel_id)
    if channel:
        await channel.send(f"👑 All hail <@{top_user_id}> – **King of the Racers**! 🏆 👑")
        await channel.send(
            f"• 🧮 Average Score: {top_data['average']}\n"
            f"• 🥇 Best Round: {top_data['best']}"
        )

# --- Scheduling Wrapper ---
def schedule_announce(gid):
    async def job():
        await announce_ethno_winner(gid)
    return job

# --- Startup ---
@bot.event
@bot.event
async def on_ready():
    load_guild_configs()
    print(f"Logged in as {bot.user}")

    for guild in bot.guilds:
        gid = guild.id
        load_scores(gid)

        # Announce winner at 23:55 UTC
        scheduler.add_job(schedule_announce(gid), 'cron', hour=23, minute=55, timezone=utc)

        # Reset scores and clear file at 00:00 UTC
        scheduler.add_job(
            lambda g=gid: (
                save_scores(g),
                ethno_scores[g].clear(),
                open(get_score_file(g), "w").close()
            ),
            'cron', hour=0, minute=0, timezone=utc
        )

    scheduler.start()

# --- Commands ---
@bot.command()
async def addscore(ctx, user: discord.Member, average: int, best: int):
    if not has_authorized_role(ctx): return await unauthorized_response(ctx)
    if not (1 <= average <= 5000 and 1 <= best <= 5000):
        return await ctx.send("⚠️ Scores must be between 1 and 5000.")
    gid = ctx.guild.id
    ethno_scores.setdefault(gid, {})[user.id] = {'average': average, 'best': best, 'name': user.display_name}
    save_scores(gid)
    await ctx.send(f"✅ Manually added score for **{user.display_name}**\n• 🧮 Avg: {average}\n• 🥇 Best: {best}")

@bot.command()
async def testreset(ctx):
    if not has_authorized_role(ctx): return await unauthorized_response(ctx)
    gid = ctx.guild.id
    if not ethno_scores.get(gid):
        return await ctx.send("⚠️ No scores to reset today.")
    await announce_ethno_winner(gid)
    ethno_scores[gid] = {}
    save_scores(gid)
    await ctx.send("🧹 Scores have been reset for today after announcing the current leader.")

@bot.command()
async def ethnoboard(ctx):
    gid = ctx.guild.id
    if not ethno_scores.get(gid):
        return await ctx.send("No scores recorded today. 🌍")

    load_king_wins(gid)
    scores = sorted(ethno_scores[gid].items(), key=lambda x: x[1]['average'], reverse=True)

    medals = ["🥇", "🥈", "🥉"]
    lines = ["### 🌎 EthnoGuessr Daily Leaderboard"]

    for i, (uid, data) in enumerate(scores):
        medal = medals[i] if i < 3 else ""
        name_line = f"{medal} **{data['name']}**".strip()
        stat_line = f" – Avg: {data['average']} | 👑 Wins: {king_wins[gid].get(uid, 0)}"
        lines.append(name_line)
        lines.append(stat_line)

    await ctx.send("\n".join(lines))



@bot.command()
async def testscore(ctx, average: int, best: int, user: discord.Member = None):
    if not (1 <= average <= 5000 and 1 <= best <= 5000):
        return await ctx.send("⚠️ Scores must be between 1 and 5000.")
    if not has_authorized_role(ctx): return await unauthorized_response(ctx)
    gid = ctx.guild.id
    target = user or ctx.author
    ethno_scores.setdefault(gid, {})[target.id] = {'average': average, 'best': best, 'name': target.display_name}
    save_scores(gid)
    await ctx.send(f"🧪 Test score recorded for **{target.display_name}**!\n• 🧮 Avg: {average}\n• 🥇 Best: {best}")

@bot.command()
async def deletescore(ctx, user: discord.Member):
    if not has_authorized_role(ctx): return await unauthorized_response(ctx)
    gid = ctx.guild.id
    if user.id in ethno_scores.get(gid, {}):
        del ethno_scores[gid][user.id]
        save_scores(gid)
        await ctx.send(f"🗑️ Removed score for **{user.display_name}**.")
    else:
        await ctx.send(f"⚠️ No score found for **{user.display_name}** to delete.")

@bot.command()
async def topkings(ctx):
    gid = ctx.guild.id
    load_king_wins(gid)
    if not king_wins.get(gid): return await ctx.send("👑 No King of the Day wins yet.")
    sorted_kings = sorted(king_wins[gid].items(), key=lambda x: x[1], reverse=True)
    lines = [f"**{i+1}. <@{uid}>** – 👑 Wins: {wins}" for i, (uid, wins) in enumerate(sorted_kings)]
    await ctx.send("### 🏆 All-Time Kings\n" + "\n".join(lines))

@bot.command()
async def channel(ctx, announce_channel_id: int, score_channel_id: int):
    if not (ctx.author.id == ctx.guild.owner_id or has_authorized_role(ctx)):
        return await ctx.send("⛔ Only the owner or authorized users can configure channels.")
    bot.guild_configs[ctx.guild.id] = {"announce_channel_id": announce_channel_id, "score_channel_id": score_channel_id}
    save_guild_configs()
    await ctx.send(f"✅ Channels updated:\n• Announce: <#{announce_channel_id}>\n• Score: <#{score_channel_id}>")

@bot.command()
async def timeleft(ctx):
    now = datetime.now(timezone.utc)

    # Define reset and announce times in UTC
    reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    announce_time = now.replace(hour=23, minute=55, second=0, microsecond=0)

    if announce_time < now:
        announce_time += timedelta(days=1)

    time_until_announce = announce_time - now
    time_until_reset = reset_time - now

    def format_td(td):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    await ctx.send(
        f"🕒 Time until winner announcement (UTC): `{format_td(time_until_announce)}`\n"
        f"🔄 Time until score reset (UTC): `{format_td(time_until_reset)}`"
    )

@bot.command()
async def johnny(ctx):
    await ctx.send(
        """### 📘 EthnoGuessr Bot Commands
**!ethnoboard** – Show today's leaderboard
**!topkings** – Show all-time King of the Day winners
**!testscore <avg> <best> [@user]** – Simulate score
**!addscore @user <avg> <best>** – Manually add score
**!deletescore @user** – Delete score
**!channel <announce_id> <score_id>** – Set bot channels
**!timeleft** – Show time left until reset and winner announcement
**!testreset** – Reset scores for testing and announce winner"""
    )

# --- Message Listener ---
@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        return await bot.process_commands(message)

    gid = message.guild.id

    if gid not in ethno_scores:
        load_scores(gid)
    if gid not in bot.guild_configs:
        load_guild_configs()

    config = bot.guild_configs.get(gid)
    if config and message.channel.id == config.get("score_channel_id"):
        print(f"[DEBUG] Message from {message.author.display_name}:\n{message.content}\n")

        # Normalize message: remove line breaks for better regex matching
        content = message.content.replace("\n", " ").strip()

        # Match average score from message
        avg_match = re.search(r"average of (\d+)", content, re.IGNORECASE)
        if not avg_match:
            print("[DEBUG] No average score found.")
            return await bot.process_commands(message)

        avg = int(avg_match.group(1))

        # 🚨 Cheat detection
        if avg == 5000:
            await message.channel.send(f"🚨 Cheater detected: **{message.author.display_name}**.")
            return await bot.process_commands(message)

        # Prevent multiple submissions
        if message.author.id in ethno_scores.get(gid, {}):
            await message.channel.send(f"⚠️ **{message.author.display_name}** already posted today.")
            return await bot.process_commands(message)

        # ✅ Save score
        ethno_scores.setdefault(gid, {})[message.author.id] = {
            'average': avg,
            'best': avg,
            'name': message.author.display_name
        }
        save_scores(gid)

        await message.channel.send(
            f"📊 Recorded EthnoGuessr results for **{message.author.display_name}**!\n"
            f"• 🧮 Average Score: {avg}"
        )

    await bot.process_commands(message)


# --- Bot Runner ---
bot.run(os.getenv('DISCORD_TOKEN'))
