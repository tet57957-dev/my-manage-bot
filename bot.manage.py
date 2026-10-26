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
"serverinfo":"ดูข้อมูลเซิร์ฟ",
"members":"ดูจำนวนสมาชิก",
"roleinfo":"ดูข้อมูลยศ",
"channelinfo":"ดูข้อมูลห้อง",
"renamechannel":"เปลี่ยนชื่อห้อง",
"createvc":"สร้างห้องเสียง",
"createtext":"สร้างห้องแชท",
"delchannel":"ลบห้อง",
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
async def ping(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    await ctx.send(f"🏓 ปิง {round(bot.latency*1000)} ms")

@bot.command(name="help")
async def help_cmd(ctx):
    if not is_allowed(ctx): await deny(ctx); return
    # แบบสวยๆ แบบในรูปที่พี่ชอบ - ส่งเป็น 1 ข้อความพอดี 1893 ตัวอักษร
    msg = """📋 คำสั่งทั้งหมด - Bot Manage (rreqzn2l) - แอดมินเท่านั้น
ทั้งหมด 60 คำสั่ง | สมาชิกใช้ไม่ได้

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
!serverinfo - ดูข้อมูลเซิร์ฟ
!members - ดูจำนวนสมาชิก
!roleinfo - ดูข้อมูลยศ
!channelinfo - ดูข้อมูลห้อง
!renamechannel - เปลี่ยนชื่อห้อง
!createvc - สร้างห้องเสียง
!createtext - สร้างห้องแชท
!delchannel - ลบห้อง

📢 ประกาศ/อื่นๆ
!ping - เช็คปิง
!help - ดูคำสั่งทั้งหมด"""
    await ctx.send(msg)  # ตอนนี้ไม่เกิน 2000 แล้ว ส่งข้อความเดียวพอ
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