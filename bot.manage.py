import discord
from discord.ext import commands
import datetime, os

# === บอทที่ 2: บอทจัดการคน (ไม่กันอะไรเลย ใช้คำสั่งอย่างเดียว) ===
# เอาไว้สำหรับพี่ดิวคนเดียว หัวดิสเท่านั้น


# === ให้ออนตลอดบน Render - Flask Web Server ===
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

@bot.event
async def on_ready():
    print(f"✅ บอทจัดการคน ออนไลน์แล้ว: {bot.user}")

def is_allowed(ctx):
    # ใช้ได้ 2 แบบเท่านั้น: 1. หัวดิส 2. คนที่ยศสูงกว่าบอทนี้
    if ctx.author.id == OWNER_ID or ctx.author.id == ctx.guild.owner_id:
        return True
    # เช็คยศ: ยศสูงสุดของคนสั่ง ต้องสูงกว่ายศสูงสุดของบอท
    try:
        bot_top = ctx.guild.me.top_role
        author_top = ctx.author.top_role
        if author_top.position > bot_top.position:
            return True
    except:
        pass
    return False

def is_owner(ctx):
    return is_allowed(ctx)

# --- คำสั่งแบน/เตะ/หมดเวลา ---
@bot.command()
async def ban(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.ban(reason=reason)
    await ctx.send(f"✅ Case # {member} has been banned. เหตุผล: {reason}")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.kick(reason=reason)
    await ctx.send(f"👢 เตะ {member.mention} แล้ว เหตุผล: {reason}")

@bot.command()
async def unban(ctx, user_id: int):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ ปลดแบน {user} แล้ว")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int = 10):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.timeout(datetime.timedelta(minutes=minutes), reason=f"timeout by {ctx.author}")
    await ctx.send(f"⏱️ หมดเวลา {member.mention} {minutes} นาทีแล้ว")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.timeout(None)
    await ctx.send(f"⏱️ ปลดหมดเวลา {member.mention} แล้ว")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="เตือน"):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    embed = discord.Embed(color=0x2b2d31)
    embed.description = f"⚠️ เตือน: {member.display_name}\nID: {member.id}\nเหตุผล: {reason}\nเตือนโดย: {ctx.author.display_name}"
    await ctx.send(embed=embed)

# --- จัดการคนเดียวในห้องเสียง ---
@bot.command()
async def vmute(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.edit(mute=True); await ctx.send(f"🔇 ปิดไมค์ {member.mention} แล้ว")
@bot.command()
async def vunmute(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.edit(mute=False); await ctx.send(f"🔊 เปิดไมค์ {member.mention} แล้ว")
@bot.command()
async def vdeafen(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.edit(deafen=True); await ctx.send(f"🎧 ปิดหูฟัง {member.mention} แล้ว")
@bot.command()
async def vundeafen(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.edit(deafen=False); await ctx.send(f"🎧 เปิดหูฟัง {member.mention} แล้ว")
@bot.command()
async def move(ctx, member: discord.Member, channel: discord.VoiceChannel):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.move_to(channel); await ctx.send(f"↔️ ย้าย {member.mention} ไป {channel.name} แล้ว")
@bot.command()
async def disconnect(ctx, member: discord.Member):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await member.move_to(None); await ctx.send(f"📞 ตัดสาย {member.mention} แล้ว")

# --- จัดการทั้งห้อง ---
@bot.command()
async def muteall(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=True)
            except: pass
    await ctx.send(f"🔇 ปิดไมค์ทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def unmuteall(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=False)
            except: pass
    await ctx.send(f"🔊 เปิดไมค์ทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def deafenall(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not m.bot:
            try: await m.edit(deafen=True)
            except: pass
    await ctx.send(f"🎧 ปิดหูฟังทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def undeafenall(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    for m in ch.members:
        if not m.bot:
            try: await m.edit(deafen=False)
            except: pass
    await ctx.send(f"🎧 เปิดหูฟังทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def disconnectall(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    for m in list(ch.members):
        if not m.bot:
            try: await m.move_to(None)
            except: pass
    await ctx.send(f"📞 ตัดสายทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def lockvc(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    await ch.set_permissions(ctx.guild.default_role, connect=False)
    await ctx.send(f"🔒 ล็อคห้อง {ch.name} แล้ว")
@bot.command()
async def unlockvc(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    await ch.set_permissions(ctx.guild.default_role, connect=True)
    await ctx.send(f"🔓 ปลดล็อคห้อง {ch.name} แล้ว")
@bot.command()
async def moveall(ctx, channel: discord.VoiceChannel):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
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
        if not m.voice: continue
        mic = "เปิด" if not m.voice.mute else "ปิด"
        hp = "เปิด" if not m.voice.deaf else "ปิด"
        cam = "เปิด" if m.voice.self_video else "ปิด"
        stream = "เปิด" if m.voice.self_stream else "ปิด"
        msg += f"👤 {m.display_name}\nID: {m.id}\n🎤 ไมค์: {mic} | 🎧 หูฟัง: {hp}\nกล้อง: {cam} | สตรีม: {stream}\n"
    await ctx.send(msg)

@bot.command()
async def clear(ctx, amount: int = 10):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"🧹 ลบ {amount} ข้อความแล้ว", delete_after=3)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 ปิง {round(bot.latency*1000)} ms")


@bot.command(name="help")
async def help_cmd(ctx):
    if not is_allowed(ctx):
        await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ครับ ต้องเป็นหัวดิส หรือยศสูงกว่าบอทนี้เท่านั้น')
        return
    embed = discord.Embed(title="📋 คำสั่งทั้งหมด - Bot Manage (rreqzn2l)", description="ใช้ในห้อง setup / หลังบ้านได้เลย", color=0x2b2d31)
    embed.add_field(name="🔇 ปิดไมค์ / หูฟัง คนเดียว", value="`!vmute @คน / !vmute ID` ปิดไมค์คนเดียว\n`!vunmute @คน` เปิดไมค์\n`!vdeafen @คน` ปิดหูฟัง\n`!vundeafen @คน` เปิดหูฟัง", inline=False)
    embed.add_field(name="🔇 ปิดไมค์ ทั้งห้อง", value="`!muteall` / `!unmuteall` ปิด/เปิดไมค์ทั้งห้อง\n`!deafenall` / `!undeafenall` ปิด/เปิดหูฟังทั้งห้อง\n`!disconnectall` ตัดสายทั้งห้อง\n`!lockvc` / `!unlockvc` ล็อค/ปลดล็อคห้อง", inline=False)
    embed.add_field(name="↔️ ย้าย / ดูห้องเสียง", value="`!move @คน #ห้อง` / `!moveall #ห้อง` ย้าย\n`!disconnect @คน` ตัดสายคนเดียว\n`!vcinfo` ดู Snapshot ห้องเสียง", inline=False)
    embed.add_field(name="🔨 แบน / เตะ / จัดการคน", value="`!ban @คน เหตุผล` แบน\n`!kick @คน เหตุผล` เตะ\n`!unban ID` ปลดแบน\n`!timeout @คน 10` หมดเวลา 10 นาที\n`!untimeout @คน` ปลดหมดเวลา\n`!warn @คน เหตุผล` เตือน (แบบกล่อง)\n`!clear 10` ลบข้อความ 10 ข้อความ\n`!ping` เช็คปิง", inline=False)
    embed.set_footer(text="ใช้ได้แค่: หัวดิส + คนที่ยศสูงกว่าบอทเท่านั้น")
    await ctx.send(embed=embed)

bot.run(TOKEN)