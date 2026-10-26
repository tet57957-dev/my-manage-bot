import discord
from discord.ext import commands
import datetime, os

# === บอทที่ 2: บอทจัดการคน (ไม่กันอะไรเลย ใช้คำสั่งอย่างเดียว) ===
# เอาไว้สำหรับพี่ดิวคนเดียว หัวดิสเท่านั้น

OWNER_ID = 1395077285362794550
TOKEN = os.getenv("DISCORD_TOKEN_2") or os.getenv("DISCORD_TOKEN")

from flask import Flask
from threading import Thread
app = Flask(__name__)
@app.route("/")
def home(): return "Manage Bot is alive!"
def run_web():
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
Thread(target=run_web, daemon=True).start()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
  print(f"✅ บอทจัดการคน ออนไลน์แล้ว: {bot.user}")

def is_allowed(ctx):
    if ctx.author.id == OWNER_ID or ctx.author.id == ctx.guild.owner_id: return True
    try:
        if ctx.author.top_role.position > ctx.guild.me.top_role.position: return True
    except: pass
    return False
def is_owner(ctx): return is_allowed(ctx)
def can_affect(ctx, member):
    if member.id == OWNER_ID: return False
    if member.bot: return False
    try:
        if member.top_role.position >= ctx.guild.me.top_role.position: return False
    except: return False
    return True
no_perm_counts = {}
async def deny(ctx):
    import datetime
    uid = ctx.author.id
    cnt = no_perm_counts.get(uid, 0) + 1
    no_perm_counts[uid] = cnt
    await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ ต้องเป็นแอดมินเท่านั้น')
    if cnt >= 2:
        try: await ctx.author.timeout(datetime.timedelta(minutes=5), reason="พิมพ์คำสั่งที่ไม่มีสิทธิ์ซ้ำ")
        except: pass
        no_perm_counts[uid] = 0


# --- คำสั่งแบน/เตะ/หมดเวลา ---
@bot.command()
async def ban(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
  if not is_owner(ctx): return
  await member.ban(reason=reason)
  await ctx.send(f"✅ Case # {member} has been banned. เหตุผล: {reason}")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
  if not is_owner(ctx): return
  await member.kick(reason=reason)
  await ctx.send(f"👢 เตะ {member.mention} แล้ว เหตุผล: {reason}")

@bot.command()
async def unban(ctx, user_id: int):
  if not is_owner(ctx): return
  user = await bot.fetch_user(user_id)
  await ctx.guild.unban(user)
  await ctx.send(f"✅ ปลดแบน {user} แล้ว")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int = 10):
  if not is_owner(ctx): return
  await member.timeout(datetime.timedelta(minutes=minutes), reason=f"timeout by {ctx.author}")
  await ctx.send(f"⏱️ หมดเวลา {member.mention} {minutes} นาทีแล้ว")

@bot.command()
async def untimeout(ctx, member: discord.Member):
  if not is_owner(ctx): return
  await member.timeout(None)
  await ctx.send(f"⏱️ ปลดหมดเวลา {member.mention} แล้ว")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="เตือน"):
  if not is_owner(ctx): return
  await ctx.send(f"⚠️ เตือน {member.mention} เหตุผล: {reason}")

# --- จัดการคนเดียวในห้องเสียง ---
@bot.command()
async def vmute(ctx, member: discord.Member):
  if not is_owner(ctx): return
  await member.edit(mute=True); await ctx.send(f"🔇 ปิดไมค์ {member.mention} แล้ว")
@bot.command()
async def vunmute(ctx, member: discord.Member):
  if not is_owner(ctx): return
  await member.edit(mute=False); await ctx.send(f"🔊 เปิดไมค์ {member.mention} แล้ว")
@bot.command()
async def vdeafen(ctx, member: discord.Member):
  if not is_owner(ctx): return
  await member.edit(deafen=True); await ctx.send(f"🎧 ปิดหูฟัง {member.mention} แล้ว")
@bot.command()
async def vundeafen(ctx, member: discord.Member):
  if not is_owner(ctx): return
  await member.edit(deafen=False); await ctx.send(f"🎧 เปิดหูฟัง {member.mention} แล้ว")
@bot.command()
async def move(ctx, member: discord.Member, channel: discord.VoiceChannel):
  if not is_owner(ctx): return
  await member.move_to(channel); await ctx.send(f"↔️ ย้าย {member.mention} ไป {channel.name} แล้ว")
@bot.command()
async def disconnect(ctx, member: discord.Member):
  if not is_owner(ctx): return
  await member.move_to(None); await ctx.send(f"📞 ตัดสาย {member.mention} แล้ว")

# --- จัดการทั้งห้อง ---
@bot.command()
async def muteall(ctx):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  for m in ch.members:
    if not m.bot:
      try: await m.edit(mute=True)
      except: pass
  await ctx.send(f"🔇 ปิดไมค์ทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def unmuteall(ctx):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  for m in ch.members:
    if not m.bot:
      try: await m.edit(mute=False)
      except: pass
  await ctx.send(f"🔊 เปิดไมค์ทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def deafenall(ctx):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  for m in ch.members:
    if not m.bot:
      try: await m.edit(deafen=True)
      except: pass
  await ctx.send(f"🎧 ปิดหูฟังทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def undeafenall(ctx):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  for m in ch.members:
    if not m.bot:
      try: await m.edit(deafen=False)
      except: pass
  await ctx.send(f"🎧 เปิดหูฟังทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def disconnectall(ctx):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  for m in list(ch.members):
    if not m.bot:
      try: await m.move_to(None)
      except: pass
  await ctx.send(f"📞 ตัดสายทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def lockvc(ctx):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  await ch.set_permissions(ctx.guild.default_role, connect=False)
  await ctx.send(f"🔒 ล็อคห้อง {ch.name} แล้ว")
@bot.command()
async def unlockvc(ctx):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  await ch.set_permissions(ctx.guild.default_role, connect=True)
  await ctx.send(f"🔓 ปลดล็อคห้อง {ch.name} แล้ว")
@bot.command()
async def moveall(ctx, channel: discord.VoiceChannel):
  if not is_owner(ctx): return
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  for m in list(ch.members):
    if not m.bot:
      try: await m.move_to(channel)
      except: pass
  await ctx.send(f"↔️ ย้ายทุกคนจาก {ch.name} ไป {channel.name} แล้ว")
@bot.command()
async def vcinfo(ctx):
  if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
  ch = ctx.author.voice.channel
  msg = f"📸 Snapshot: {ch.name}\nสมาชิกทั้งหมด: {len(ch.members)} คน\n"
  for m in ch.members:
    mic = "เปิด" if not m.voice.mute else "ปิด"
    hp = "เปิด" if not m.voice.deaf else "ปิด"
    msg += f"👤 {m.display_name} ID: {m.id} 🎤 ไมค์: {mic} | 🎧 หูฟัง: {hp}\n"
  await ctx.send(msg)

@bot.command()
async def clear(ctx, amount: int = 10):
  if not is_owner(ctx): return
  await ctx.channel.purge(limit=amount+1)
  await ctx.send(f"🧹 ลบ {amount} ข้อความแล้ว")

@bot.command()
async def ping(ctx):
  await ctx.send(f"🏓 ปิง {round(bot.latency*1000)} ms")


# === คำสั่งที่หายไป: help / cmds / purge / purgebot / lockall ฯลฯ ===
@bot.command(name="help")
async def help_cmd(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ ต้องเป็นแอดมินเท่านั้น')
        return
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
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ ต้องเป็นแอดมินเท่านั้น'); return
    cmd = bot.get_command("help")
    if cmd: await cmd.callback(ctx)

@bot.command(name="commands")
async def commands_alias(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ ต้องเป็นแอดมินเท่านั้น'); return
    cmd = bot.get_command("help")
    if cmd: await cmd.callback(ctx)

@bot.command()
async def purge(ctx, amount: int = 100):
    if not is_allowed(ctx): await deny(ctx); return
    deleted = await ctx.channel.purge(limit=amount); await ctx.send(f"🧹 ลบ {len(deleted)} ข้อความแล้ว")

@bot.command()
async def purgebot(ctx, target: discord.Member = None):
    if not is_allowed(ctx): await deny(ctx); return
    deleted = 0
    async for msg in ctx.channel.history(limit=1000):
        if target:
            if msg.author.id == target.id:
                try: await msg.delete(); deleted += 1
                except: pass
        else:
            if msg.author.bot and "rreqzn1l" in msg.author.name.lower():
                try: await msg.delete(); deleted += 1
                except: pass
    name = target.display_name if target else "rreqzn1l"
    await ctx.send(f"🤖 ลบข้อความของ {name} ทั้งหมด {deleted} ข้อความแล้ว (ไม่ลบ Kanopi)")

@bot.command()
async def lockall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not can_affect(ctx, m): continue
        try: await m.edit(mute=True, deafen=True)
        except: pass
    await ctx.send(f"🔒 ปิดทั้งไมค์+หูฟังทุกคนใน {ch.name} แล้ว")

@bot.command()
async def unlockall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not can_affect(ctx, m): continue
        try: await m.edit(mute=False, deafen=False)
        except: pass
    await ctx.send(f"🔓 เปิดทั้งไมค์+หูฟังทุกคนใน {ch.name} แล้ว")

@bot.command()
async def lockmic(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not can_affect(ctx, m): continue
        try: await m.edit(mute=True)
        except: pass
    await ctx.send("🔒 ล็อคไมค์อย่างเดียวแล้ว")

@bot.command()
async def unlockmic(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not can_affect(ctx, m): continue
        try: await m.edit(mute=False)
        except: pass
    await ctx.send("🔓 ปลดล็อคไมค์แล้ว")

@bot.command()
async def lockdeafen(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not can_affect(ctx, m): continue
        try: await m.edit(deafen=True)
        except: pass
    await ctx.send("🔒 ล็อคหูฟังอย่างเดียวแล้ว")

@bot.command()
async def unlockdeafen(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not can_affect(ctx, m): continue
        try: await m.edit(deafen=False)
        except: pass
    await ctx.send("🔓 ปลดล็อคหูฟังแล้ว")


bot.run(TOKEN)