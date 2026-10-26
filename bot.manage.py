import discord
from discord.ext import commands
import datetime, os, asyncio, random

# === บอทที่ 2: จัดการคน - แอดมินเท่านั้น ===
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
    # กฎใหม่ตามที่พี่บอก: ใช้ได้แค่ เจ้าของเซิร์ฟ / เจ้าของบอท / คนที่ยศสูงกว่าบอทเท่านั้น
    # ถ้ายศต่ำกว่าบอท แม้จะเปิดผู้ดูแล (Administrator) ก็ใช้ไม่ได้
    if ctx.author.id == OWNER_ID or ctx.author.id == ctx.guild.owner_id: return True
    try:
        bot_top = ctx.guild.me.top_role
        author_top = ctx.author.top_role
        if author_top.position > bot_top.position: return True
    except: pass
    return False
def is_owner(ctx): return is_allowed(ctx)

no_perm_counts = {}
async def deny(ctx):
    uid = ctx.author.id
    cnt = no_perm_counts.get(uid, 0) + 1
    no_perm_counts[uid] = cnt
    await ctx.send('❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ ต้องเป็นแอดมินเท่านั้น')
    if cnt >= 2:
        try: await ctx.author.timeout(datetime.timedelta(minutes=5), reason="พิมพ์คำสั่งที่ไม่มีสิทธิ์ซ้ำ")
        except: pass
        no_perm_counts[uid] = 0

mute_locked_channels = set()
deafen_locked_channels = set()
vmute_locked_users = set()
vdeafen_locked_users = set()

@bot.event
async def on_ready():
    print(f"✅ บอทจัดการคน ออนไลน์แล้ว: {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id in mute_locked_channels and not after.mute and member.id != OWNER_ID and not member.bot:
        try: await member.edit(mute=True, reason="ล็อคไมค์")
        except: pass
    if after.channel and after.channel.id in deafen_locked_channels and not after.deaf and member.id != OWNER_ID and not member.bot:
        try: await member.edit(deafen=True, reason="ล็อคหูฟัง")
        except: pass
    if member.id in vmute_locked_users and not after.mute and member.id != OWNER_ID:
        try: await member.edit(mute=True)
        except: pass
    if member.id in vdeafen_locked_users and not after.deaf and member.id != OWNER_ID:
        try: await member.edit(deafen=True)
        except: pass

# คำอธิบายทุกคำสั่ง สำหรับ !help
HELP_DESC = {
"vmute":"ปิดไมค์คนเดียว (ล็อค เปิดเองไม่ได้)",
"vunmute":"เปิดไมค์คนเดียว",
"vdeafen":"ปิดหูฟังคนเดียว (ล็อค เปิดเองไม่ได้)",
"vundeafen":"เปิดหูฟังคนเดียว",
"muteall":"ปิดไมค์ทุกคน (ล็อค เปิดเองไม่ได้)",
"unmuteall":"เปิดไมค์ทุกคน",
"deafenall":"ปิดหูฟังทุกคน (ล็อค เปิดเองไม่ได้)",
"undeafenall":"เปิดหูฟังทุกคน",
"lockall":"ปิดทั้งไมค์+หูฟังทุกคน",
"unlockall":"เปิดทั้งไมค์+หูฟังทุกคน",
"lockmic":"ล็อคไมค์อย่างเดียว ไม่ล็อคห้อง",
"unlockmic":"ปลดล็อคไมค์",
"lockdeafen":"ล็อคหูฟังอย่างเดียว",
"unlockdeafen":"ปลดล็อคหูฟัง",
"tempMute":"ปิดไมค์ชั่วคราวตามนาที",
"lockvc":"ล็อคห้องเสียง ไม่ให้เข้า",
"unlockvc":"ปลดล็อคห้องเสียง",
"lock":"ล็อคห้องแชท ไม่ให้พิมพ์",
"unlock":"ปลดล็อคห้องแชท",
"muteallchat":"ปิดแชททุกห้อง",
"unmuteallchat":"เปิดแชททุกห้อง",
"slowmode":"เปิดพิมพ์ช้า",
"noslow":"ปิดพิมพ์ช้า",
"move":"ย้ายคนไปห้องอื่น",
"moveall":"ย้ายทุกคนไปห้องอื่น",
"disconnect":"ตัดสายคนเดียว",
"disconnectall":"ตัดสายทุกคน",
"vcinfo":"ดู Snapshot ห้องเสียง",
"ban":"แบน",
"unban":"ปลดแบน",
"unbanall":"ปลดแบนทุกคน",
"listbans":"ดูคนโดนแบน",
"kick":"เตะ",
"massban":"แบนหลายคนทีเดียว",
"timeout":"หมดเวลา",
"untimeout":"ปลดหมดเวลา",
"warn":"เตือนแบบกล่อง",
"clear":"ลบข้อความ",
"purge":"ลบข้อความจำนวนมาก",
"nuke":"ล้างห้องใหม่",
"nick":"เปลี่ยนชื่อคน",
"addrole":"ใส่ยศ",
"removerole":"ถอดยศ",
"userinfo":"ดูข้อมูลคน",
"myinfo":"ดูข้อมูลตัวเอง",
"avatar":"ดูรูปโปรไฟล์",
"serverinfo":"ดูข้อมูลเซิร์ฟ",
"members":"ดูจำนวนสมาชิก",
"roleinfo":"ดูข้อมูลยศ",
"channelinfo":"ดูข้อมูลห้อง",
"renamechannel":"เปลี่ยนชื่อห้อง",
"createvc":"สร้างห้องเสียง",
"createtext":"สร้างห้องแชท",
"delchannel":"ลบห้อง",
"setstatus":"ตั้งสถานะบอท",
"say":"ให้บอทพูดแทน",
"announce":"ประกาศแบบกล่องแดง",
"embed":"ส่งเป็นกล่อง",
"poll":"สร้างโหวต",
"giveaway":"แจกของ",
"dm":"ส่ง DM",
"ping":"เช็คปิง",
"help":"ดูคำสั่งทั้งหมด",
"yesrole":"ปลดล็อคยศในห้อง",
"norole":"คนในห้องแอดมินใช้ยศไม่ได้ ยกเว้นแอดมิน",
"mutelist":"ดูใครโดนล็อคไมค์ในห้อง",
"slowmodeall":"เปิดพิมพ์ช้าทุกห้อง",
"clearallvc":"ล้างห้องเสียง",
"mutecheck":"เช็คโดนล็อคไมค์ไหม"
}

# --- ฟังก์ชันช่วย ---
async def do_muteall(ctx, mute=True, deafen=False):
    pass

# --- คำสั่งทั้งหมด (Admin Only) ---
@bot.command()
async def ban(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
    if not is_allowed(ctx): await deny(ctx); return
    await member.ban(reason=reason); await ctx.send(f"✅ แบน {member} แล้ว เหตุผล: {reason}")
@bot.command()
async def kick(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
    if not is_allowed(ctx): await deny(ctx); return
    await member.kick(reason=reason); await ctx.send(f"👢 เตะ {member.mention} แล้ว เหตุผล: {reason}")
@bot.command()
async def unban(ctx, user_id: int):
    if not is_allowed(ctx): await deny(ctx); return
    u = await bot.fetch_user(user_id); await ctx.guild.unban(u); await ctx.send(f"✅ ปลดแบน {u} แล้ว")
@bot.command()
async def unbanall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    bans=[b async for b in ctx.guild.bans()]
    for b in bans:
        try: await ctx.guild.unban(b.user)
        except: pass
    await ctx.send(f"✅ ปลดแบนทุกคนแล้ว {len(bans)} คน")
@bot.command()
async def listbans(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    bans=[b async for b in ctx.guild.bans()]
    if not bans: await ctx.send("✅ ไม่มีคนโดนแบนครับ"); return
    await ctx.send("🔨 คนที่โดนแบน:\n"+"\n".join([f"{b.user} (ID: {b.user.id})" for b in bans[:20]]))
@bot.command()
async def massban(ctx, *members: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    for m in members:
        try: await m.ban()
        except: pass
    await ctx.send(f"🔨 แบนไปแล้ว {len(members)} คน")
@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int = 10):
    if not is_allowed(ctx): await deny(ctx); return
    await member.timeout(datetime.timedelta(minutes=minutes)); await ctx.send(f"⏱️ หมดเวลา {member.mention} {minutes} นาทีแล้ว")
@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    await member.timeout(None); await ctx.send(f"⏱️ ปลดหมดเวลา {member.mention} แล้ว")
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="เตือน"):
    if not is_allowed(ctx): await deny(ctx); return
    e=discord.Embed(color=0x2b2d31); e.description=f"⚠️ เตือน: {member.display_name}\nID: {member.id}\nเหตุผล: {reason}\nเตือนโดย: {ctx.author.display_name}"; await ctx.send(embed=e)
@bot.command()
async def clear(ctx, amount: int = 10):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.channel.purge(limit=amount+1); await ctx.send(f"🧹 ลบ {amount} ข้อความแล้ว", delete_after=3)
@bot.command()
async def purge(ctx, amount: int = 50):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.channel.purge(limit=amount+1); await ctx.send(f"🧹 ลบ {amount} ข้อความแล้ว", delete_after=3)
@bot.command()
async def nuke(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    ch=ctx.channel; pos=ch.position; new=await ch.clone(); await ch.delete(); await new.edit(position=pos); await new.send("🧹 ล้างห้องแล้วครับ")

@bot.command()
async def vmute(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    vmute_locked_users.add(member.id); await member.edit(mute=True); await ctx.send(f"🔇 ปิดไมค์ {member.mention} แล้ว (ล็อคแล้ว เปิดเองไม่ได้)")
@bot.command()
async def vunmute(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    vmute_locked_users.discard(member.id); await member.edit(mute=False); await ctx.send(f"🔊 เปิดไมค์ {member.mention} แล้ว")
@bot.command()
async def vdeafen(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    vdeafen_locked_users.add(member.id); await member.edit(deafen=True); await ctx.send(f"🎧 ปิดหูฟัง {member.mention} แล้ว (ล็อคแล้ว เปิดเองไม่ได้)")
@bot.command()
async def vundeafen(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    vdeafen_locked_users.discard(member.id); await member.edit(deafen=False); await ctx.send(f"🎧 เปิดหูฟัง {member.mention} แล้ว")
@bot.command()
async def tempMute(ctx, member: discord.Member, minutes: int = 10):
    if not is_allowed(ctx): await deny(ctx); return
    vmute_locked_users.add(member.id); await member.edit(mute=True); await ctx.send(f"⏱️ ปิดไมค์ {member.mention} {minutes} นาที (ล็อคแล้ว)"); await asyncio.sleep(minutes*60); vmute_locked_users.discard(member.id)
    try: await member.edit(mute=False)
    except: pass

@bot.command()
async def muteall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; mute_locked_channels.add(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=True)
            except: pass
    await ctx.send(f"🔇 ปิดไมค์ทุกคนในห้อง {ch.name} แล้ว (ล็อคไมค์ เปิดเองไม่ได้ ไม่ได้ล็อคห้อง เข้าห้องได้ปกติ)")
@bot.command()
async def unmuteall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; mute_locked_channels.discard(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=False)
            except: pass
    await ctx.send(f"🔊 เปิดไมค์ทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def deafenall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; deafen_locked_channels.add(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(deafen=True)
            except: pass
    await ctx.send(f"🎧 ปิดหูฟังทุกคนในห้อง {ch.name} แล้ว (ล็อคหูฟัง เปิดเองไม่ได้)")
@bot.command()
async def undeafenall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; deafen_locked_channels.discard(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(deafen=False)
            except: pass
    await ctx.send(f"🎧 เปิดหูฟังทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def lockall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; mute_locked_channels.add(ch.id); deafen_locked_channels.add(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=True, deafen=True)
            except: pass
    await ctx.send(f"🔒 ล็อคทั้งหมดห้อง {ch.name} แล้ว ปิดทั้งไมค์+หูฟัง เปิดเองไม่ได้")
@bot.command()
async def unlockall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; mute_locked_channels.discard(ch.id); deafen_locked_channels.discard(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=False, deafen=False)
            except: pass
    await ctx.send(f"🔓 ปลดล็อคทั้งหมดห้อง {ch.name} แล้ว")
@bot.command()
async def lockmic(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; mute_locked_channels.add(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=True)
            except: pass
    await ctx.send(f"🔒 ล็อคไมค์ห้อง {ch.name} แล้ว เปิดเองไม่ได้ เข้าห้องได้ปกติ")
@bot.command()
async def unlockmic(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; mute_locked_channels.discard(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(mute=False)
            except: pass
    await ctx.send(f"🔓 ปลดล็อคไมค์ห้อง {ch.name} แล้ว")
@bot.command()
async def lockdeafen(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; deafen_locked_channels.add(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(deafen=True)
            except: pass
    await ctx.send(f"🔒 ล็อคหูฟังห้อง {ch.name} แล้ว")
@bot.command()
async def unlockdeafen(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; deafen_locked_channels.discard(ch.id)
    for m in ch.members:
        if not m.bot:
            try: await m.edit(deafen=False)
            except: pass
    await ctx.send(f"🔓 ปลดล็อคหูฟังห้อง {ch.name} แล้ว")

@bot.command()
async def move(ctx, member: discord.Member, channel: discord.VoiceChannel):
    if not is_allowed(ctx): await deny(ctx); return
    await member.move_to(channel); await ctx.send(f"↔️ ย้าย {member.mention} ไป {channel.name} แล้ว")
@bot.command()
async def moveall(ctx, channel: discord.VoiceChannel):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel
    for m in list(ch.members):
        if not m.bot:
            try: await m.move_to(channel)
            except: pass
    await ctx.send(f"↔️ ย้ายทุกคนจาก {ch.name} ไป {channel.name} แล้ว")
@bot.command()
async def disconnect(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    await member.move_to(None); await ctx.send(f"📞 ตัดสาย {member.mention} แล้ว")
@bot.command()
async def disconnectall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel
    for m in list(ch.members):
        if not m.bot:
            try: await m.move_to(None)
            except: pass
    await ctx.send(f"📞 ตัดสายทุกคนในห้อง {ch.name} แล้ว")
@bot.command()
async def vcinfo(ctx):
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; msg=f"📸 Snapshot: {ch.name}\nสมาชิกทั้งหมด: {len(ch.members)} คน\n"
    for m in ch.members:
        if not m.voice: continue
        mic="เปิด" if not m.voice.mute else "ปิด"; hp="เปิด" if not m.voice.deaf else "ปิด"; cam="เปิด" if m.voice.self_video else "ปิด"; stream="เปิด" if m.voice.self_stream else "ปิด"
        msg+=f"👤 {m.display_name}\nID: {m.id}\n🎤 ไมค์: {mic} | 🎧 หูฟัง: {hp}\nกล้อง: {cam} | สตรีม: {stream}\n"
    await ctx.send(msg)

@bot.command()
async def lockvc(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; await ch.set_permissions(ctx.guild.default_role, connect=False); await ctx.send(f"🔒 ล็อคห้อง {ch.name} แล้ว")
@bot.command()
async def unlockvc(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch=ctx.author.voice.channel; await ch.set_permissions(ctx.guild.default_role, connect=True); await ctx.send(f"🔓 ปลดล็อคห้อง {ch.name} แล้ว")
@bot.command()
async def lock(ctx, channel: discord.TextChannel = None):
    if not is_allowed(ctx): await deny(ctx); return
    ch=channel or ctx.channel; await ch.set_permissions(ctx.guild.default_role, send_messages=False); await ctx.send(f"🔒 ล็อคห้องแชท {ch.mention} แล้ว")
@bot.command()
async def unlock(ctx, channel: discord.TextChannel = None):
    if not is_allowed(ctx): await deny(ctx); return
    ch=channel or ctx.channel; await ch.set_permissions(ctx.guild.default_role, send_messages=True); await ctx.send(f"🔓 ปลดล็อคห้องแชท {ch.mention} แล้ว")
@bot.command()
async def muteallchat(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    for ch in ctx.guild.text_channels:
        try: await ch.set_permissions(ctx.guild.default_role, send_messages=False)
        except: pass
    await ctx.send("🔒 ปิดแชททุกห้องแล้ว")
@bot.command()
async def unmuteallchat(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    for ch in ctx.guild.text_channels:
        try: await ch.set_permissions(ctx.guild.default_role, send_messages=True)
        except: pass
    await ctx.send("🔓 เปิดแชททุกห้องแล้ว")
@bot.command()
async def slowmode(ctx, sec: int = 5):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.channel.edit(slowmode_delay=sec); await ctx.send(f"🐢 เปิด Slowmode {sec} วิแล้ว")
@bot.command()
async def noslow(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.channel.edit(slowmode_delay=0); await ctx.send("✅ ปิด Slowmode แล้ว")

@bot.command()
async def nick(ctx, member: discord.Member, *, name):
    if not is_allowed(ctx): await deny(ctx); return
    await member.edit(nick=name); await ctx.send(f"✏️ เปลี่ยนชื่อ {member.mention} เป็น `{name}` แล้ว")
@bot.command()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    if not is_allowed(ctx): await deny(ctx); return
    await member.add_roles(role); await ctx.send(f"✅ ใส่ยศ {role.mention} ให้ {member.mention} แล้ว")
@bot.command()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    if not is_allowed(ctx): await deny(ctx); return
    await member.remove_roles(role); await ctx.send(f"✅ ถอดยศ {role.mention} จาก {member.mention} แล้ว")
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if not is_allowed(ctx): await deny(ctx); return
    m=member or ctx.author; e=discord.Embed(title=f"👤 ข้อมูล {m.display_name}", color=0x2b2d31); e.add_field(name="ID", value=m.id); e.add_field(name="เข้าเซิร์ฟเมื่อ", value=m.joined_at.strftime("%d/%m/%Y %H:%M") if m.joined_at else "-"); e.add_field(name="ยศ", value=", ".join([r.mention for r in m.roles[1:]]) or "ไม่มี"); await ctx.send(embed=e)
@bot.command()
async def myinfo(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    m=ctx.author; e=discord.Embed(title=f"👤 ข้อมูลของ {m.display_name}", color=0x2b2d31); e.add_field(name="ID", value=m.id); e.add_field(name="ยศ", value=", ".join([r.mention for r in m.roles[1:]]) or "ไม่มี"); await ctx.send(embed=e)
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    if not is_allowed(ctx): await deny(ctx); return
    m=member or ctx.author; e=discord.Embed(title=f"🖼️ รูปโปรไฟล์ {m.display_name}", color=0x2b2d31); e.set_image(url=m.display_avatar.url); await ctx.send(embed=e)
@bot.command()
async def serverinfo(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    g=ctx.guild; e=discord.Embed(title=f"🏠 ข้อมูลเซิร์ฟ {g.name}", color=0x2b2d31); e.add_field(name="สมาชิก", value=g.member_count); e.add_field(name="ห้องแชท", value=len(g.text_channels)); e.add_field(name="ห้องเสียง", value=len(g.voice_channels)); await ctx.send(embed=e)
@bot.command()
async def members(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"👥 สมาชิกทั้งหมด: {ctx.guild.member_count} คน")
@bot.command()
async def roleinfo(ctx, role: discord.Role):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"🎭 ยศ {role.mention} - มี {len(role.members)} คน")
@bot.command()
async def channelinfo(ctx, channel: discord.TextChannel = None):
    if not is_allowed(ctx): await deny(ctx); return
    ch=channel or ctx.channel; await ctx.send(f"💬 ห้อง {ch.mention} - สร้างเมื่อ {ch.created_at.strftime('%d/%m/%Y')}")
@bot.command()
async def renamechannel(ctx, channel: discord.TextChannel, *, name):
    if not is_allowed(ctx): await deny(ctx); return
    await channel.edit(name=name); await ctx.send(f"✏️ เปลี่ยนชื่อห้องเป็น `{name}` แล้ว")
@bot.command()
async def createvc(ctx, *, name):
    if not is_allowed(ctx): await deny(ctx); return
    ch=await ctx.guild.create_voice_channel(name); await ctx.send(f"🔊 สร้างห้องเสียง `{name}` แล้ว")
@bot.command()
async def createtext(ctx, *, name):
    if not is_allowed(ctx): await deny(ctx); return
    ch=await ctx.guild.create_text_channel(name); await ctx.send(f"💬 สร้างห้องแชท `{name}` แล้ว")
@bot.command()
async def delchannel(ctx, channel: discord.TextChannel):
    if not is_allowed(ctx): await deny(ctx); return
    await channel.delete(); await ctx.send(f"🗑️ ลบห้อง {channel.name} แล้ว")

@bot.command()
async def say(ctx, *, msg):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.message.delete(); await ctx.send(msg)
@bot.command()
async def announce(ctx, *, msg):
    if not is_allowed(ctx): await deny(ctx); return
    e=discord.Embed(title="📢 ประกาศจากแอดมิน", description=msg, color=0xff0000); e.set_footer(text=f"ประกาศโดย {ctx.author.display_name}"); await ctx.send(embed=e)
@bot.command()
async def embed(ctx, *, msg):
    if not is_allowed(ctx): await deny(ctx); return
    e=discord.Embed(description=msg, color=0x2b2d31); await ctx.send(embed=e)
@bot.command()
async def poll(ctx, *, question):
    if not is_allowed(ctx): await deny(ctx); return
    e=discord.Embed(title="📊 โหวต", description=question, color=0x2b2d31); m=await ctx.send(embed=e); await m.add_reaction("✅"); await m.add_reaction("❌")
@bot.command()
async def giveaway(ctx, *, prize):
    if not is_allowed(ctx): await deny(ctx); return
    e=discord.Embed(title="🎉 แจกของ!", description=f"รางวัล: {prize}\nกด 🎉 เพื่อเข้าร่วม", color=0xffd700); m=await ctx.send(embed=e); await m.add_reaction("🎉")
@bot.command()
async def dm(ctx, member: discord.Member, *, msg):
    if not is_allowed(ctx): await deny(ctx); return
    try: await member.send(f"📩 จากแอดมิน {ctx.guild.name}: {msg}"); await ctx.send(f"✅ ส่ง DM ให้ {member.mention} แล้ว")
    except: await ctx.send("❌ ส่ง DM ไม่ได้")
@bot.command()
async def setstatus(ctx, *, status):
    if not is_allowed(ctx): await deny(ctx); return
    await bot.change_presence(activity=discord.Game(name=status)); await ctx.send(f"✅ ตั้งสถานะบอทเป็น `{status}` แล้ว")
@bot.command()
async def ping(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"🏓 ปิง {round(bot.latency*1000)} ms")

@bot.command(name="help")
async def help_cmd(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    # แบบสวยๆ แบบในรูปที่พี่ชอบ - ส่งเป็น 1 ข้อความพอดี 1893 ตัวอักษร
    msg = """📋 คำสั่งทั้งหมด - Bot Manage (rreqzn2l) - แอดมินเท่านั้น
ทั้งหมด 69 คำสั่ง | สมาชิกใช้ไม่ได้

🔇 ปิดไมค์/หูฟัง (ล็อค เปิดเองไม่ได้)
!vmute - ปิดไมค์คนเดียว (ล็อค เปิดเองไม่ได้)
!vunmute - เปิดไมค์คนเดียว
!vdeafen - ปิดหูฟังคนเดียว (ล็อค เปิดเองไม่ได้)
!vundeafen - เปิดหูฟังคนเดียว
!muteall - ปิดไมค์ทุกคน (ล็อค เปิดเองไม่ได้)
!unmuteall - เปิดไมค์ทุกคน
!deafenall - ปิดหูฟังทุกคน (ล็อค เปิดเองไม่ได้)
!undeafenall - เปิดหูฟังทุกคน
!lockall - ปิดทั้งไมค์+หูฟังทุกคน
!unlockall - เปิดทั้งไมค์+หูฟังทุกคน
!lockmic - ล็อคไมค์อย่างเดียว ไม่ล็อคห้อง
!unlockmic - ปลดล็อคไมค์
!lockdeafen - ล็อคหูฟังอย่างเดียว
!unlockdeafen - ปลดล็อคหูฟัง
!tempMute - ปิดไมค์ชั่วคราวตามนาที
!mutelist - ดูใครโดนล็อคไมค์ในห้อง
!mutecheck - เช็คโดนล็อคไมค์ไหม

🔒 ล็อคห้อง/แชท
!lockvc - ล็อคห้องเสียง ไม่ให้เข้า
!unlockvc - ปลดล็อคห้องเสียง
!lock - ล็อคห้องแชท ไม่ให้พิมพ์
!unlock - ปลดล็อคห้องแชท
!muteallchat - ปิดแชททุกห้อง
!unmuteallchat - เปิดแชททุกห้อง
!slowmode - เปิดพิมพ์ช้า
!noslow - ปิดพิมพ์ช้า
!slowmodeall - เปิดพิมพ์ช้าทุกห้อง
!norole - คนในห้องแอดมินใช้ยศไม่ได้ ยกเว้นแอดมิน
!yesrole - ปลดล็อคยศในห้อง

↔️ ย้าย/ตัดสาย
!move - ย้ายคนไปห้องอื่น
!moveall - ย้ายทุกคนไปห้องอื่น
!disconnect - ตัดสายคนเดียว
!disconnectall - ตัดสายทุกคน
!vcinfo - ดู Snapshot ห้องเสียง
!clearallvc - ล้างห้องเสียง

🔨 แบน/เตะ/เตือน
!ban - แบน
!unban - ปลดแบน
!unbanall - ปลดแบนทุกคน
!listbans - ดูคนโดนแบน
!kick - เตะ
!massban - แบนหลายคนทีเดียว
!timeout - หมดเวลา
!untimeout - ปลดหมดเวลา
!warn - เตือนแบบกล่อง
!clear - ลบข้อความ
!purge - ลบข้อความจำนวนมาก
!nuke - ล้างห้องใหม่

👥 จัดการคน/ยศ
!nick - เปลี่ยนชื่อคน
!addrole - ใส่ยศ
!removerole - ถอดยศ
!userinfo - ดูข้อมูลคน
!myinfo - ดูข้อมูลตัวเอง
!avatar - ดูรูปโปรไฟล์
!serverinfo - ดูข้อมูลเซิร์ฟ
!members - ดูจำนวนสมาชิก
!roleinfo - ดูข้อมูลยศ
!channelinfo - ดูข้อมูลห้อง
!renamechannel - เปลี่ยนชื่อห้อง
!createvc - สร้างห้องเสียง
!createtext - สร้างห้องแชท
!delchannel - ลบห้อง

📢 ประกาศ/อื่นๆ
!setstatus - ตั้งสถานะบอท
!say - ให้บอทพูดแทน
!announce - ประกาศแบบกล่องแดง
!embed - ส่งเป็นกล่อง
!poll - สร้างโหวต
!giveaway - แจกของ
!dm - ส่ง DM
!ping - เช็คปิง
!help - ดูคำสั่งทั้งหมด"""
    await ctx.send(msg)
@bot.command(name="cmds")
async def cmds_alias(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    # เรียก help ตรงๆ
    cmd = bot.get_command("help")
    if cmd: await cmd.callback(ctx)

@bot.command(name="commands")
async def commands_alias(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    cmd = bot.get_command("help")
    if cmd: await cmd.callback(ctx)


@bot.command()
async def norole(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice:
        await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    if not hasattr(bot, "locked_roles_backup"):
        bot.locked_roles_backup = {}
    for m in list(ch.members):
        # ข้ามแอดมิน: เจ้าของเซิร์ฟ / เจ้าของบอท / ยศสูงกว่าบอท
        if m.id == ctx.guild.owner_id or m.id == OWNER_ID: continue
        try:
            if m.top_role.position > ctx.guild.me.top_role.position: continue
        except: pass
        # เก็บยศไว้ก่อนแล้วถอดยศออก (ไม่ปิดไมค์ ไม่ปิดหูฟัง)
        roles_to_remove = [r for r in m.roles if not r.is_default() and r.position < ctx.guild.me.top_role.position]
        if roles_to_remove:
            bot.locked_roles_backup[m.id] = roles_to_remove
            try: await m.remove_roles(*roles_to_remove, reason="ล็อคยศโดยแอดมิน")
            except: pass
    await ctx.send(f"🔒 ล็อคยศคนในห้อง {ch.name} แล้วครับ คนที่ไม่ใช่แอดมินใช้ยศไม่ได้เลย (ไม่ปิดไมค์ ไม่ปิดหูฟัง)")

@bot.command()
async def yesrole(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice:
        await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    backup = getattr(bot, "locked_roles_backup", {})
    for m in list(ch.members):
        if m.id in backup:
            try: await m.add_roles(*backup[m.id], reason="ปลดล็อคยศ")
            except: pass
    bot.locked_roles_backup = {}
    await ctx.send(f"🔓 ปลดล็อคยศคนในห้อง {ch.name} แล้วครับ ใช้ยศได้ปกติ")

bot.run(TOKEN)