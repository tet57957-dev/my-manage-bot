import discord
from discord.ext import commands
import datetime, os, asyncio
from flask import Flask
from threading import Thread
app = Flask(__name__)
@app.route("/")
def home(): return "Manage Bot is alive!"
def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
Thread(target=run_web, daemon=True).start()

OWNER_ID = 1395077285362794550
TOKEN = os.getenv("DISCORD_TOKEN_2") or os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

def is_allowed(ctx):
    if ctx.author.id == OWNER_ID or ctx.author.id == ctx.guild.owner_id:
        return True
    try:
        if ctx.author.top_role.position > ctx.guild.me.top_role.position:
            return True
    except:
        pass
    return False

def is_owner(ctx):
    return is_allowed(ctx)

def can_affect(ctx, member):
    if member.id == OWNER_ID:
        return False
    if member.bot:
        return False
    try:
        if member.top_role.position >= ctx.guild.me.top_role.position:
            return False
    except:
        return False
    return True

no_perm_counts = {}
async def deny(ctx):
    uid = ctx.author.id
    cnt = no_perm_counts.get(uid, 0) + 1
    no_perm_counts[uid] = cnt
    await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ ต้องเป็นแอดมินเท่านั้น')
    if cnt >= 2:
        try:
            await ctx.author.timeout(datetime.timedelta(minutes=5), reason="พิมพ์คำสั่งที่ไม่มีสิทธิ์ซ้ำ")
        except:
            pass
        no_perm_counts[uid] = 0

vmute_locked_users = set()
vdeafen_locked_users = set()
mute_locked_channels = set()
deafen_locked_channels = set()

@bot.event
async def on_ready():
    print(f"✅ บอทจัดการคน ออนไลน์แล้ว: {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    try:
        if member.id in vmute_locked_users and after.mute == False and member.voice:
            await member.edit(mute=True)
        if member.id in vdeafen_locked_users and after.deaf == False and member.voice:
            await member.edit(deafen=True)
        if after.channel and after.channel.id in mute_locked_channels and not after.mute:
            await member.edit(mute=True)
        if after.channel and after.channel.id in deafen_locked_channels and not after.deaf:
            await member.edit(deafen=True)
    except:
        pass

@bot.command()
async def ping(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    await ctx.send(f"🏓 ปิง {round(bot.latency*1000)} ms")

@bot.command()
async def vmute(ctx, member: discord.Member = None):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not member:
        await ctx.send("❌ ใส่ @คน หรือ ID ครับ"); return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท ปิดไมค์ไม่ได้ครับ"); return
    try:
        vmute_locked_users.add(member.id)
        await member.edit(mute=True)
        await ctx.send(f"🔇 ปิดไมค์ {member.mention} แล้ว")
    except:
        await ctx.send("❌ ปิดไม่ได้ครับ")

@bot.command()
async def vunmute(ctx, member: discord.Member = None):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not member:
        return
    try:
        vmute_locked_users.discard(member.id)
        await member.edit(mute=False)
        await ctx.send(f"🔊 เปิดไมค์ {member.mention} แล้ว")
    except:
        await ctx.send("❌ เปิดไม่ได้ครับ")

@bot.command()
async def vdeafen(ctx, member: discord.Member = None):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not member:
        return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท ปิดหูฟังไม่ได้ครับ"); return
    try:
        vdeafen_locked_users.add(member.id)
        await member.edit(deafen=True)
        await ctx.send(f"🔇 ปิดหูฟัง {member.mention} แล้ว")
    except:
        await ctx.send("❌ ปิดไม่ได้ครับ")

@bot.command()
async def vundeafen(ctx, member: discord.Member = None):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not member:
        return
    try:
        vdeafen_locked_users.discard(member.id)
        await member.edit(deafen=False)
        await ctx.send(f"🔊 เปิดหูฟัง {member.mention} แล้ว")
    except:
        await ctx.send("❌ เปิดไม่ได้ครับ")

@bot.command()
async def muteall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    mute_locked_channels.add(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vmute_locked_users.add(m.id)
        try:
            await m.edit(mute=True)
        except:
            pass
    await ctx.send(f"🔇 ปิดไมค์ทุกคนในห้อง {ch.name} แล้ว")

@bot.command()
async def unmuteall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    mute_locked_channels.discard(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vmute_locked_users.discard(m.id)
        try:
            await m.edit(mute=False)
        except:
            pass
    await ctx.send(f"🔊 เปิดไมค์ทุกคนในห้อง {ch.name} แล้ว")

@bot.command()
async def deafenall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    deafen_locked_channels.add(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vdeafen_locked_users.add(m.id)
        try:
            await m.edit(deafen=True)
        except:
            pass
    await ctx.send(f"🔇 ปิดหูฟังทุกคนในห้อง {ch.name} แล้ว")

@bot.command()
async def undeafenall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    deafen_locked_channels.discard(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vdeafen_locked_users.discard(m.id)
        try:
            await m.edit(deafen=False)
        except:
            pass
    await ctx.send(f"🔊 เปิดหูฟังทุกคนในห้อง {ch.name} แล้ว")

@bot.command()
async def lockall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    mute_locked_channels.add(ch.id)
    deafen_locked_channels.add(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vmute_locked_users.add(m.id)
        vdeafen_locked_users.add(m.id)
        try:
            await m.edit(mute=True, deafen=True)
        except:
            pass
    await ctx.send(f"🔒 ปิดทั้งไมค์+หูฟังทุกคนในห้อง {ch.name} แล้ว")

@bot.command()
async def unlockall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    mute_locked_channels.discard(ch.id)
    deafen_locked_channels.discard(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vmute_locked_users.discard(m.id)
        vdeafen_locked_users.discard(m.id)
        try:
            await m.edit(mute=False, deafen=False)
        except:
            pass
    await ctx.send(f"🔓 เปิดทั้งไมค์+หูฟังทุกคนในห้อง {ch.name} แล้ว")

@bot.command()
async def lockmic(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    mute_locked_channels.add(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vmute_locked_users.add(m.id)
        try:
            await m.edit(mute=True)
        except:
            pass
    await ctx.send("🔒 ล็อคไมค์แล้ว")

@bot.command()
async def unlockmic(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    mute_locked_channels.discard(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vmute_locked_users.discard(m.id)
        try:
            await m.edit(mute=False)
        except:
            pass
    await ctx.send("🔓 ปลดล็อคไมค์แล้ว")

@bot.command()
async def lockdeafen(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    deafen_locked_channels.add(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vdeafen_locked_users.add(m.id)
        try:
            await m.edit(deafen=True)
        except:
            pass
    await ctx.send("🔒 ล็อคหูฟังแล้ว")

@bot.command()
async def unlockdeafen(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    deafen_locked_channels.discard(ch.id)
    for m in ch.members:
        if not can_affect(ctx, m):
            continue
        vdeafen_locked_users.discard(m.id)
        try:
            await m.edit(deafen=False)
        except:
            pass
    await ctx.send("🔓 ปลดล็อคหูฟังแล้ว")

@bot.command()
async def lockvc(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    await ch.set_permissions(ctx.guild.default_role, connect=False)
    await ctx.send(f"🔒 ล็อคห้อง {ch.name} แล้ว")

@bot.command()
async def unlockvc(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    await ch.set_permissions(ctx.guild.default_role, connect=True)
    await ctx.send(f"🔓 ปลดล็อคห้อง {ch.name} แล้ว")

@bot.command()
async def lock(ctx, channel: discord.TextChannel = None):
    if not is_allowed(ctx):
        await deny(ctx); return
    ch = channel or ctx.channel
    await ch.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 ล็อคห้อง {ch.name} แล้ว")

@bot.command()
async def unlock(ctx, channel: discord.TextChannel = None):
    if not is_allowed(ctx):
        await deny(ctx); return
    ch = channel or ctx.channel
    await ch.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"🔓 ปลดล็อคห้อง {ch.name} แล้ว")

@bot.command()
async def muteallchat(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    for ch in ctx.guild.text_channels:
        try:
            await ch.set_permissions(ctx.guild.default_role, send_messages=False)
        except:
            pass
    await ctx.send("🔒 ปิดแชททุกห้องแล้ว")

@bot.command()
async def unmuteallchat(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    for ch in ctx.guild.text_channels:
        try:
            await ch.set_permissions(ctx.guild.default_role, send_messages=True)
        except:
            pass
    await ctx.send("🔓 เปิดแชททุกห้องแล้ว")

@bot.command()
async def slowmode(ctx, sec: int = 5):
    if not is_allowed(ctx):
        await deny(ctx); return
    await ctx.channel.edit(slowmode_delay=sec)
    await ctx.send(f"🐢 เปิดพิมพ์ช้า {sec} วิแล้ว")

@bot.command()
async def noslow(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    await ctx.channel.edit(slowmode_delay=0)
    await ctx.send("🐢 ปิดพิมพ์ช้าแล้ว")

@bot.command()
async def slowmodeall(ctx, sec: int = 5):
    if not is_allowed(ctx):
        await deny(ctx); return
    for ch in ctx.guild.text_channels:
        try:
            await ch.edit(slowmode_delay=sec)
        except:
            pass
    await ctx.send(f"🐢 เปิดพิมพ์ช้า {sec} วิทุกห้องแล้ว")

@bot.command()
async def norole(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    if not hasattr(bot, "locked_roles_backup"):
        bot.locked_roles_backup = {}
    for m in list(ch.members):
        if m.id == ctx.guild.owner_id or m.id == OWNER_ID:
            continue
        if not can_affect(ctx, m):
            continue
        roles_to_remove = [r for r in m.roles if not r.is_default() and r.position < ctx.guild.me.top_role.position]
        if roles_to_remove:
            bot.locked_roles_backup[m.id] = roles_to_remove
            try:
                await m.remove_roles(*roles_to_remove)
            except:
                pass
    await ctx.send(f"🔒 ล็อคยศคนในห้อง {ch.name} แล้ว")

@bot.command()
async def yesrole(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    backup = getattr(bot, "locked_roles_backup", {})
    for m in list(ch.members):
        if m.id in backup:
            try:
                await m.add_roles(*backup[m.id])
            except:
                pass
    bot.locked_roles_backup = {}
    await ctx.send(f"🔓 ปลดล็อคยศคนในห้อง {ch.name} แล้ว")

@bot.command()
async def move(ctx, member: discord.Member, channel: discord.VoiceChannel):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท ย้ายไม่ได้ครับ"); return
    try:
        await member.move_to(channel)
        await ctx.send(f"↔️ ย้าย {member.mention} ไป {channel.name} แล้ว")
    except:
        await ctx.send("❌ ย้ายไม่ได้ครับ")

@bot.command()
async def moveall(ctx, channel: discord.VoiceChannel):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    for m in list(ctx.author.voice.channel.members):
        if not can_affect(ctx, m):
            continue
        try:
            await m.move_to(channel)
        except:
            pass
    await ctx.send(f"↔️ ย้ายทุกคนไป {channel.name} แล้ว")

@bot.command()
async def disconnect(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท ตัดไม่ได้ครับ"); return
    try:
        await member.move_to(None)
        await ctx.send(f"✂️ ตัดสาย {member.mention} แล้ว")
    except:
        await ctx.send("❌ ตัดไม่ได้ครับ")

@bot.command()
async def disconnectall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    for m in list(ctx.author.voice.channel.members):
        if not can_affect(ctx, m):
            continue
        try:
            await m.move_to(None)
        except:
            pass
    await ctx.send("✂️ ตัดสายทุกคนแล้ว")

@bot.command()
async def vcinfo(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    ch = ctx.author.voice.channel
    await ctx.send(f"🎤 ห้อง {ch.name} มี {len(ch.members)} คน")

@bot.command()
async def clearallvc(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        return
    await ctx.send(f"🧹 ล้างห้องเสียง {ctx.author.voice.channel.name} แล้ว")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=""):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท แบนไม่ได้ครับ"); return
    try:
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"🔨 แบน {member.mention} แล้ว")
    except:
        await ctx.send("❌ แบนไม่ได้ครับ")

@bot.command()
async def unban(ctx, user_id: int):
    if not is_allowed(ctx):
        await deny(ctx); return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ ปลดแบน {user} แล้ว")
    except:
        await ctx.send("❌ ปลดไม่ได้ครับ")

@bot.command()
async def unbanall(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    bans = [b async for b in ctx.guild.bans()]
    for b in bans:
        try:
            await ctx.guild.unban(b.user)
        except:
            pass
    await ctx.send(f"✅ ปลดแบนทุกคน {len(bans)} คนแล้ว")

@bot.command()
async def listbans(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    bans = [b async for b in ctx.guild.bans()]
    if not bans:
        await ctx.send("✅ ไม่มีคนโดนแบนครับ")
    else:
        await ctx.send("🔨 คนโดนแบน: " + ", ".join([b.user.name for b in bans]))

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=""):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท เตะไม่ได้ครับ"); return
    try:
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f"👢 เตะ {member.mention} แล้ว")
    except:
        await ctx.send("❌ เตะไม่ได้ครับ")

@bot.command()
async def massban(ctx, *members: discord.Member):
    if not is_allowed(ctx):
        await deny(ctx); return
    for m in members:
        if not can_affect(ctx, m):
            continue
        try:
            await ctx.guild.ban(m)
        except:
            pass
    await ctx.send(f"🔨 แบน {len(members)} คนแล้ว")

def parse_duration(s):
    s = s.strip().lower()
    if s.endswith('d'):
        return datetime.timedelta(days=int(s[:-1]))
    if s.endswith('h'):
        return datetime.timedelta(hours=int(s[:-1]))
    if s.endswith('m'):
        return datetime.timedelta(minutes=int(s[:-1]))
    if s.endswith('s'):
        return datetime.timedelta(seconds=int(s[:-1]))
    return datetime.timedelta(minutes=int(s))

@bot.command()
async def timeout(ctx, member: discord.Member, duration: str = "10m"):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท หมดเวลาไม่ได้ครับ"); return
    try:
        td = parse_duration(duration)
        await member.timeout(td, reason=f"timeout by {ctx.author}")
        await ctx.send(f"⏱️ หมดเวลา {member.mention} {duration} แล้ว")
    except Exception as e:
        await ctx.send(f"❌ หมดเวลาไม่ได้ครับ {e}")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await deny(ctx); return
    try:
        await member.timeout(None)
        await ctx.send(f"✅ ปลดหมดเวลา {member.mention} แล้ว")
    except:
        await ctx.send("❌ ปลดไม่ได้ครับ")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason=""):
    if not is_allowed(ctx):
        await deny(ctx); return
    embed = discord.Embed(title="⚠️ เตือน", description=f"{member.mention} {reason}", color=0xff0000)
    await ctx.send(embed=embed)

@bot.command()
async def clear(ctx, amount: int = 10):
    if not is_allowed(ctx):
        await deny(ctx); return
    deleted = await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"🧹 ลบ {len(deleted)-1} ข้อความแล้ว")

@bot.command()
async def purge(ctx, amount: int = 100):
    if not is_allowed(ctx):
        await deny(ctx); return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 ลบ {len(deleted)} ข้อความแล้ว")

@bot.command()
async def purgebot(ctx, target: discord.Member = None):
    if not is_allowed(ctx):
        await deny(ctx); return
    deleted = 0
    async for msg in ctx.channel.history(limit=1000):
        if target:
            if msg.author.id == target.id:
                try:
                    await msg.delete(); deleted += 1; await asyncio.sleep(0.2)
                except:
                    pass
        else:
            if msg.author.bot and "rreqzn1l" in msg.author.name.lower():
                try:
                    await msg.delete(); deleted += 1; await asyncio.sleep(0.2)
                except:
                    pass
    name = target.display_name if target else "rreqzn1l"
    await ctx.send(f"🤖 ลบข้อความของ {name} ทั้งหมด {deleted} ข้อความแล้ว (ไม่ลบ Kanopi)")

@bot.command()
async def nuke(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    ch = ctx.channel
    new = await ch.clone(reason="nuke")
    await ch.delete()
    await new.send("🧹 ล้างห้องใหม่แล้ว")

@bot.command()
async def mutelist(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not ctx.author.voice:
        await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    lines = []
    for m in ctx.author.voice.channel.members:
        if m.id in vmute_locked_users:
            lines.append(f"🔇 {m.display_name} - ล็อคไมค์")
        if m.id in vdeafen_locked_users:
            lines.append(f"🔇 {m.display_name} - ล็อคหูฟัง")
    if not lines:
        await ctx.send("✅ ไม่มีใครโดนล็อคครับ")
    else:
        await ctx.send("🔇 คนที่โดนล็อค:\n" + "\n".join(lines))

@bot.command()
async def mutecheck(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await deny(ctx); return
    await ctx.send(f"🔍 {member.mention} | ปิดไมค์: {'ใช่ (ล็อค)' if member.id in vmute_locked_users else 'ไม่'} | ปิดหูฟัง: {'ใช่ (ล็อค)' if member.id in vdeafen_locked_users else 'ไม่'}")

@bot.command(name="tempMute")
async def tempMute(ctx, member: discord.Member, minutes: int = 5):
    if not is_allowed(ctx):
        await deny(ctx); return
    if not can_affect(ctx, member):
        await ctx.send("❌ คนนี้ยศสูงกว่าบอท ปิดไมค์ไม่ได้ครับ"); return
    try:
        vmute_locked_users.add(member.id)
        await member.edit(mute=True)
        await ctx.send(f"🔇 ปิดไมค์ {member.mention} {minutes} นาที")
        await asyncio.sleep(minutes*60)
        vmute_locked_users.discard(member.id)
        await member.edit(mute=False)
    except:
        pass

@bot.command(name="help")
async def help_cmd(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    embed = discord.Embed(title="📋 คำสั่งทั้งหมด - Bot Manage (rreqzn2l)", description="ใช้ในห้อง setup / หลังบ้านได้เลย\nทั้งหมด 49 คำสั่ง | สมาชิกใช้ไม่ได้", color=0x2b2d31)
    embed.add_field(name="🔇 ปิดไมค์/หูฟัง", value="!vmute @คน ปิดไมค์คนเดียว\n!vunmute @คน เปิดไมค์\n!vdeafen @คน ปิดหูฟัง\n!vundeafen @คน เปิดหูฟัง\n!muteall / !unmuteall ปิด/เปิดไมค์ทั้งห้อง (เฉพาะยศต่ำกว่าบอท)\n!deafenall / !undeafenall ปิด/เปิดหูฟังทั้งห้อง\n!lockall / !unlockall ปิด/เปิดทั้งไมค์+หูฟัง\n!lockmic / !unlockmic ล็อคไมค์\n!lockdeafen / !unlockdeafen ล็อคหูฟัง\n!tempMute @คน 5 ปิดไมค์ชั่วคราว\n!mutelist / !mutecheck ดูใครโดนล็อค", inline=False)
    embed.add_field(name="🔒 ล็อคห้อง/แชท", value="!lockvc / !unlockvc ล็อคห้องเสียง\n!lock / !unlock ล็อคห้องแชท\n!muteallchat / !unmuteallchat ปิดแชททุกห้อง\n!slowmode 5 / !noslow พิมพ์ช้า\n!slowmodeall 5 พิมพ์ช้าทุกห้อง\n!norole / !yesrole ล็อคยศในห้อง", inline=False)
    embed.add_field(name="↔️ ย้าย/ตัดสาย", value="!move @คน #ห้อง / !moveall #ห้อง ย้าย\n!disconnect @คน ตัดสายคนเดียว\n!disconnectall ตัดสายทุกคน\n!vcinfo ดู Snapshot ห้องเสียง\n!clearallvc ล้างห้องเสียง", inline=False)
    embed.add_field(name="🔨 แบน/เตะ/จัดการคน", value="!ban @คน เหตุผล แบน\n!kick @คน เหตุผล เตะ\n!unban ID ปลดแบน\n!unbanall / !listbans\n!massban แบนหลายคน\n!timeout @คน 7d หมดเวลา 7 วัน / 10m 10 นาที\n!untimeout @คน ปลดหมดเวลา\n!warn @คน เหตุผล เตือน (แบบกล่อง)\n!clear 10 = ลบ 10 ข้อความตามเลขที่พิมพ์\n!purge 100 = ลบ 100 ข้อความตามเลขที่พิมพ์\n!purgebot = ลบข้อความบอท rreqzn1l ทั้งหมดในห้อง ไม่ลบ Kanopi\n!purgebot @บอท = ลบข้อความบอทตัวนั้นทั้งหมด\n!nuke ล้างห้องใหม่", inline=False)
    embed.add_field(name="📢 อื่นๆ", value="!ping เช็คปิง\n!help / !cmds ดูคำสั่งทั้งหมด", inline=False)
    embed.set_footer(text="ใช้ได้แค่: แอดมินเท่านั้น | ยศสูงกว่าบอทเท่านั้น | ยศต่ำกว่าบอทใช้ไม่ได้")
    await ctx.send(embed=embed)

@bot.command(name="cmds")
async def cmds_alias(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    cmd = bot.get_command("help")
    if cmd:
        await cmd.callback(ctx)

@bot.command(name="commands")
async def commands_alias(ctx):
    if not is_allowed(ctx):
        await deny(ctx); return
    cmd = bot.get_command("help")
    if cmd:
        await cmd.callback(ctx)

bot.run(TOKEN)