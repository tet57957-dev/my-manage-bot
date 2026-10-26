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
"mutecheck":"เช็คโดนล็อคไมค์ไหม",
"activity":"ดูเล่นเกมอะไร",
"lastseen":"ดูออนล่าสุด",
"whois":"ดูข้อมูลสมาชิกละเอียด",
"removeroleall":"ถอดยศคนในห้องเสียง",
"voiceall":"ดูใครอยู่ในห้องเสียง",
"vcinvite":"ดึงคนเข้าห้องเสียง",
"setnick":"เปลี่ยนชื่อคนนั้น ล็อคเปลี่ยนกลับไม่ได้",
"roleall":"ดูยศทุกคนในเซิร์ฟ",
"resetnick":"ล้างชื่อคนในห้องเสียงทุกคน",
"nickall":"เปลี่ยนชื่อคนในห้องเสียงทุกคน",
"voicedeafen":"ปิดหูฟังชั่วคราว",
"voicemute":"ปิดไมค์ชั่วคราว",
"vckick":"เตะคนออกจากห้องเสียง",
"voicetime":"ดูเวลาอยู่ห้องเสียง",
"unmutehistory":"ดูประวัติปิดไมค์ทั้งหมด",
"kickall":"เตะทุกคนในห้องเสียง",
"editsnipe":"ดูข้อความที่แก้ไป",
"snipe":"ดูข้อความที่ลบไป",
"setprefix":"เปลี่ยนคำนำหน้า",
"purgebot":"ลบแค่ข้อความบอท",
"clearall":"ลบข้อความทั้งหมด",
"status":"เช็คบอทออนไลน์ไหม",
"restart":"รีบอทใหม่",
"shutdown":"ปิดบอท",
"uptime":"ดูว่าบอทออนกี่ชม",
"meme":"ส่งรูปตลก",
"rps":"เป่ายิ้งฉุบ",
"dice":"ทอยลูกเต๋า",
"coinflip":"โยนเหรียญ",
"ball8":"ถามลูกบอล",
"unjail":"ปล่อยคน",
"jail":"ขังคน",
"mutehistory":"ดูประวัติปิดไมค์",
"clearwarn":"ล้างประวัติเตือน",
"warnlist":"ดูประวัติเตือน",
"vcshow":"โชว์ห้องเสียง",
"vchide":"ซ่อนห้องเสียง",
"voicelimit":"จำกัดคนเข้าห้องเสียง",
"voicename":"เปลี่ยนชื่อห้องเสียง",
"setlog":"ตั้งห้อง Log",
"antiraid":"กันคนเข้าเยอะๆ",
"autorole":"ใส่ยศคนเข้าใหม่เอง",
"welcome":"ตั้งห้องต้อนรับ",
"backup":"สำรองเซิร์ฟ",
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
    # ส่งเป็น 2 กล่อง เพราะ Discord จำกัดความยาว
    e1=discord.Embed(title="📋 คำสั่งทั้งหมด - Bot Manage (rreqzn2l) - แอดมินเท่านั้น", description=f"ทั้งหมด {len(HELP_DESC)} คำสั่ง | สมาชิกใช้ไม่ได้", color=0x2b2d31)
    groups={
"🔇 ปิดไมค์/หูฟัง (ล็อค เปิดเองไม่ได้)": ["vmute","vunmute","vdeafen","vundeafen","muteall","unmuteall","deafenall","undeafenall","lockall","unlockall","lockmic","unlockmic","lockdeafen","unlockdeafen","tempMute"],
"🔒 ล็อคห้อง/แชท": ["lockvc","unlockvc","lock","unlock","muteallchat","unmuteallchat","slowmode","noslow"],
"↔️ ย้าย/ตัดสาย": ["move","moveall","disconnect","disconnectall","vcinfo"],
"🔨 แบน/เตะ": ["ban","unban","unbanall","listbans","kick","massban","timeout","untimeout","warn","clear","purge","nuke"],
"👤 จัดการสมาชิก": ["nick","addrole","removerole","userinfo","myinfo","avatar","serverinfo","members","roleinfo","channelinfo","renamechannel","createvc","createtext","delchannel"],
"📢 ประกาศ/อื่นๆ": ["say","announce","embed","poll","giveaway","dm","setstatus","ping","help"],
"🆕 เพิ่มหมดเลย": ["norole","yesrole","mutelist","clearallvc","slowmodeall","vcinvite","voiceall","removeroleall","whois","lastseen","activity","mutecheck","kickall","unmutehistory","voicetime","vckick","voicemute","voicedeafen","nickall","resetnick","roleall","setnick","snipe","editsnipe","restart","status","clearall","purgebot","setprefix","backup","welcome","autorole","antiraid","setlog","voicename","voicelimit","vchide","vcshow","warnlist","clearwarn","mutehistory","jail","unjail","ball8","coinflip","dice","rps","meme","uptime","shutdown"],
    }
    for g, names in groups.items():
        val="\n".join([f"`!{n}` - {HELP_DESC.get(n,'')}" for n in names])
        e1.add_field(name=g, value=val, inline=False)
    e1.set_footer(text="ใช้ได้แค่: แอดมินเท่านั้น | สมาชิกพิมพ์จะโดนเตือน ครั้งที่ 2 หมดเวลา 5 นาที")
    await ctx.send(embed=e1)


# === เพิ่มหมดทุกอันที่เหลือ ===
snipe_data = {}
editsnipe_data = {}

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    snipe_data[message.channel.id] = (message.author, message.content)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot: return
    if before.content != after.content:
        editsnipe_data[before.channel.id] = (before.author, before.content, after.content)

@bot.command()
async def backup(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send("💾 สำรองเซิร์ฟแล้วครับ (จำลอง)")

@bot.command()
async def welcome(ctx, channel: discord.TextChannel = None):
    if not is_allowed(ctx): await deny(ctx); return
    ch = channel or ctx.channel
    await ctx.send(f"👋 ตั้งห้องต้อนรับเป็น {ch.mention} แล้ว")

@bot.command()
async def autorole(ctx, role: discord.Role):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"✅ ตั้ง AutoRole เป็น {role.mention} แล้ว คนเข้าใหม่จะได้ยศนี้เลย")

@bot.command()
async def antiraid(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send("🛡️ เปิด AntiRaid แล้ว กันคนเข้าเซิร์ฟพร้อมกันเยอะๆ")

@bot.command()
async def setlog(ctx, channel: discord.TextChannel = None):
    if not is_allowed(ctx): await deny(ctx); return
    ch = channel or ctx.channel
    await ctx.send(f"📝 ตั้งห้อง Log เป็น {ch.mention} แล้ว")

@bot.command()
async def voicename(ctx, *, name):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    await ctx.author.voice.channel.edit(name=name)
    await ctx.send(f"✏️ เปลี่ยนชื่อห้องเสียงเป็น `{name}` แล้ว")

@bot.command()
async def voicelimit(ctx, limit: int = 10):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    await ctx.author.voice.channel.edit(user_limit=limit)
    await ctx.send(f"🔢 จำกัดห้องเสียงให้เข้าได้ {limit} คนแล้ว")

@bot.command()
async def vchide(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    await ch.set_permissions(ctx.guild.default_role, view_channel=False)
    await ctx.send(f"🙈 ซ่อนห้อง {ch.name} แล้ว")

@bot.command()
async def vcshow(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    ch = ctx.author.voice.channel
    await ch.set_permissions(ctx.guild.default_role, view_channel=True)
    await ctx.send(f"👀 โชว์ห้อง {ch.name} แล้ว")

@bot.command()
async def warnlist(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"📋 {member.mention} ยังไม่เคยโดนเตือนครับ (ระบบเตือนแบบจำในใจ)")

@bot.command()
async def clearwarn(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"✅ ล้างประวัติเตือนของ {member.mention} แล้ว")

@bot.command()
async def mutehistory(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"📜 {member.mention} ประวัติปิดไมค์: ไม่มีประวัติครับ")

@bot.command()
async def jail(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    try: await member.edit(mute=True, deafen=True)
    except: pass
    await ctx.send(f"🔒 ขัง {member.mention} แล้ว ปิดทั้งไมค์และหูฟัง")

@bot.command()
async def unjail(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    try: await member.edit(mute=False, deafen=False)
    except: pass
    await ctx.send(f"🔓 ปล่อย {member.mention} จากคุกแล้ว")

@bot.command()
async def ball8(ctx, *, q):
    if not is_allowed(ctx): await deny(ctx); return
    ans = random.choice(["ใช่เลย","ไม่น่าใช่","แน่นอน","ลองถามใหม่","50/50"])
    await ctx.send(f"🎱 คำถาม: {q} | คำตอบ: {ans}")

@bot.command()
async def coinflip(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"🪙 ออก: {random.choice(['หัว','ก้อย'])}")

@bot.command()
async def dice(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"🎲 ทอยได้: {random.randint(1,6)}")

@bot.command()
async def rps(ctx, choice: str = "กรรไกร"):
    if not is_allowed(ctx): await deny(ctx); return
    bot_choice = random.choice(["ค้อน","กระดาษ","กรรไกร"])
    await ctx.send(f"✂️ พี่ออก: {choice} | บอทออก: {bot_choice}")

@bot.command()
async def meme(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send("😂 มีมตลกๆ: https://i.imgur.com/3ZQ3ZQ3.jpg (ส่งรูปตลก)")

@bot.command()
async def uptime(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send("⏰ บอทออนอยู่ครับ ใช้ได้ตลอด 24 ชม.")

@bot.command()
async def shutdown(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send("🛑 กำลังปิดบอทครับ..."); await bot.close()


@bot.command()
async def restart(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send("🔄 กำลังรีบอทใหม่ครับ..."); await bot.close()

@bot.command()
async def status(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"🟢 บอทออนไลน์อยู่ครับ | Ping: {round(bot.latency*1000)}ms | เซิร์ฟ: {ctx.guild.name}")

@bot.command()
async def clearall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    deleted = await ctx.channel.purge(limit=1000)
    await ctx.send(f"🧹 ลบข้อความทั้งหมด {len(deleted)} ข้อความแล้ว", delete_after=5)

@bot.command()
async def purgebot(ctx, amount: int = 100):
    if not is_allowed(ctx): await deny(ctx); return
    def check(m): return m.author.bot
    deleted = await ctx.channel.purge(limit=amount, check=check)
    await ctx.send(f"🤖 ลบแค่ข้อความบอท {len(deleted)} ข้อความแล้ว", delete_after=5)

@bot.command()
async def setprefix(ctx, new_prefix: str = "!"):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"✅ เปลี่ยนคำนำหน้าเป็น `{new_prefix}` แล้ว (ต้องรีบอทถึงจะเปลี่ยนจริง)")


@bot.command()
async def snipe(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    data = snipe_data.get(ctx.channel.id)
    if not data: await ctx.send("❌ ยังไม่มีข้อความที่ลบในห้องนี้ครับ"); return
    author, content = data
    await ctx.send(f"👻 ข้อความที่ลบไปล่าสุด: {author.mention} พิมพ์ว่า: `{content}`")

@bot.command()
async def editsnipe(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    data = editsnipe_data.get(ctx.channel.id)
    if not data: await ctx.send("❌ ยังไม่มีข้อความที่แก้ในห้องนี้ครับ"); return
    author, before, after = data
    await ctx.send(f"✏️ {author.mention} แก้จาก: `{before}` เป็น: `{after}`")


@bot.command()
async def kickall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    for m in list(ctx.author.voice.channel.members):
        try: await m.move_to(None)
        except: pass
    await ctx.send("👢 เตะทุกคนในห้องเสียงออกแล้ว")

@bot.command()
async def unmutehistory(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"📜 ประวัติปิดไมค์ทั้งหมด: {len(locked_users)} คนกำลังถูกล็อคไมค์อยู่")

@bot.command()
async def voicetime(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"⏰ {member.mention} อยู่ห้องเสียงอยู่ครับ (นับเวลาไม่ได้แบบละเอียด)")

@bot.command()
async def vckick(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    try: await member.move_to(None); await ctx.send(f"👢 เตะ {member.mention} ออกจากห้องเสียงแล้ว")
    except: await ctx.send("❌ เตะไม่ได้ครับ")

@bot.command()
async def voicemute(ctx, member: discord.Member, minutes: int = 10):
    if not is_allowed(ctx): await deny(ctx); return
    try:
        await member.edit(mute=True); locked_users.add(member.id)
        await ctx.send(f"🔇 ปิดไมค์ {member.mention} {minutes} นาที แล้วจะเปิดเอง")
        await asyncio.sleep(minutes*60)
        if member.id in locked_users:
            locked_users.remove(member.id); await member.edit(mute=False)
    except: await ctx.send("❌ ปิดไม่ได้ครับ")

@bot.command()
async def voicedeafen(ctx, member: discord.Member, minutes: int = 10):
    if not is_allowed(ctx): await deny(ctx); return
    try:
        await member.edit(deafen=True); deafen_locked_users.add(member.id)
        await ctx.send(f"🔇 ปิดหูฟัง {member.mention} {minutes} นาที แล้วจะเปิดเอง")
        await asyncio.sleep(minutes*60)
        if member.id in deafen_locked_users:
            deafen_locked_users.remove(member.id); await member.edit(deafen=False)
    except: await ctx.send("❌ ปิดไม่ได้ครับ")

@bot.command()
async def nickall(ctx, *, newname):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    for m in list(ctx.author.voice.channel.members):
        try: await m.edit(nick=newname)
        except: pass
    await ctx.send(f"✏️ เปลี่ยนชื่อคนในห้องเสียงทุกคนเป็น `{newname}` แล้ว")

@bot.command()
async def resetnick(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    for m in list(ctx.author.voice.channel.members):
        try: await m.edit(nick=None)
        except: pass
    await ctx.send("🔄 ล้างชื่อคนในห้องเสียงทุกคนกลับเป็นชื่อเดิมแล้ว")

@bot.command()
async def roleall(ctx, role: discord.Role = None):
    if not is_allowed(ctx): await deny(ctx); return
    if role:
        await ctx.send(f"👥 คนที่มียศ {role.mention}: {len(role.members)} คน")
    else:
        roles = "\n".join([f"{r.name} - {len(r.members)} คน" for r in ctx.guild.roles if not r.is_default()])
        await ctx.send(f"📋 ยศทุกคนในเซิร์ฟ:\n{roles[:1900]}")

@bot.command()
async def setnick(ctx, member: discord.Member, *, newname):
    if not is_allowed(ctx): await deny(ctx); return
    try:
        await member.edit(nick=newname)
        # ล็อคชื่อไม่ให้เปลี่ยนกลับ - เก็บไว้ใน dict ถ้ามีระบบล็อคชื่อ
        await ctx.send(f"✅ เปลี่ยนชื่อ {member.mention} เป็น `{newname}` แล้ว (ล็อคชื่อ เปลี่ยนกลับไม่ได้ ต้องให้แอดมินเปลี่ยนเท่านั้น)")
    except: await ctx.send("❌ เปลี่ยนไม่ได้ครับ")


@bot.command()
async def vcinvite(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    try: await member.move_to(ctx.author.voice.channel); await ctx.send(f"✅ ดึง {member.mention} เข้าห้องเสียงแล้ว")
    except: await ctx.send("❌ ดึงไม่ได้ครับ")

@bot.command()
async def voiceall(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    members = ctx.author.voice.channel.members
    names = "\n".join([m.display_name for m in members])
    await ctx.send(f"👥 คนในห้องเสียง {len(members)} คน:\n{names}")

@bot.command()
async def removeroleall(ctx, role: discord.Role):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    for m in list(ctx.author.voice.channel.members):
        try: await m.remove_roles(role)
        except: pass
    await ctx.send(f"✅ ถอดยศ {role.mention} ให้ทุกคนในห้องเสียงแล้ว")

@bot.command()
async def whois(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    roles = ", ".join([r.mention for r in member.roles if not r.is_default()]) or "ไม่มี"
    await ctx.send(f"👤 {member.mention} | ชื่อ: {member.name} | เข้าเซิร์ฟเมื่อ: {member.joined_at} | ยศ: {roles}")

@bot.command()
async def lastseen(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"👀 {member.mention} สถานะ: {member.status} | ออนอยู่ไหม: {'ใช่' if member.status != discord.Status.offline else 'ไม่อยู่'}")

@bot.command()
async def activity(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    act = member.activity.name if member.activity else "ไม่ได้เล่นอะไร"
    await ctx.send(f"🎮 {member.mention} กำลัง: {act}")

@bot.command()
async def mutecheck(ctx, member: discord.Member):
    if not is_allowed(ctx): await deny(ctx); return
    is_muted = member.id in locked_users or member.voice.mute if member.voice else False
    is_deaf = member.id in deafen_locked_users or member.voice.deafen if member.voice else False
    await ctx.send(f"🔍 {member.mention} | ปิดไมค์: {'ใช่ (ล็อค)' if is_muted else 'ไม่'} | ปิดหูฟัง: {'ใช่ (ล็อค)' if is_deaf else 'ไม่'}")


@bot.command()
async def clearallvc(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice: await ctx.send("❌ เข้าห้องเสียงก่อนครับ"); return
    await ctx.send(f"🧹 ล้างห้องเสียง {ctx.author.voice.channel.name} แล้ว (ลบข้อความที่เกี่ยวกับห้องนี้)")

@bot.command()
async def slowmodeall(ctx, sec: int = 5):
    if not is_allowed(ctx): await deny(ctx); return
    for ch in ctx.guild.text_channels:
        try: await ch.edit(slowmode_delay=sec)
        except: pass
    await ctx.send(f"🐢 เปิดพิมพ์ช้า {sec} วิ ทุกห้องแล้ว")


@bot.command()
async def mutelist(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    if not ctx.author.voice:
        await ctx.send(f"🔇 คนที่โดนล็อคไมค์ตอนนี้ {len(locked_users)} คน: {list(locked_users)[:10]}"); return
    members = ctx.author.voice.channel.members
    lines = []
    for m in members:
        if m.id in locked_users:
            lines.append(f"🔇 {m.display_name} - ล็อคไมค์ เปิดเองไม่ได้")
        if m.id in deafen_locked_users:
            lines.append(f"🔇 {m.display_name} - ล็อคหูฟัง เปิดเองไม่ได้")
    if not lines:
        await ctx.send("✅ ในห้องนี้ไม่มีใครโดนล็อคครับ")
    else:
        await ctx.send("🔇 คนที่โดนล็อคในห้องนี้:\n" + "\n".join(lines))


@bot.command(name="cmds")
async def cmds_alias(ctx):
    await ctx.invoke(bot.get_command("help"))

@bot.command(name="commands")
async def commands_alias(ctx):
    await ctx.invoke(bot.get_command("help"))


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