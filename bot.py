# pip install python-telegram-bot
import json, os
from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler,
                          MessageHandler, filters, ContextTypes)

TOKEN = "9151980359:AAEi5UaNWEne8LMV4EBAhC_ANncMNir2DDg"
ADMIN_ID = 8386741546
DB_FILE = "files.json"
MAX_LECTURES = 16

STAGES = {
    "1": "قۆناغی یەکەم 📕",
    "2": "قۆناغی دووەم 📘",
    "3": "قۆناغی سێیەم 📗",
    "4": "قۆناغی چوارەم 📙",
}
SEMESTERS = {"1": "سیمستەری یەکەم", "2": "سیمستەری دووەم"}

# ڕیزبەندی وانەکان (٠، ١، ٢...) بۆ caption ی فایلەکان گرنگە. بۆ بینینی ژمارەکان لە بۆتەکە /ids بنێرە
SUBJECTS = {
    "1": {
        "1": [
            "Basic Organic Chemistry (Theory)",
            "Basic Organic Chemistry (Practical)",
            "Kurdology",
            "Computer Science 1",
            "English",
            "Academic Discussion",
        ],
        "2": [
            "Academic Computing II",
            "Basic Inorganic Chemistry (Theory & Tutorial)",
            "Basic Inorganic Chemistry (Practical)",
            "Basic Analytical Chemistry (Theory & Tutorial)",
            "Basic Analytical Chemistry (Practical)",
            "Mathematics",
            "General Physics",
        ],
    },

    "2": {
        "1": [
            "Environmental Chemistry",
            "Organic Chemistry I",
            "Physical Chemistry I",
            "Analytical Chemistry",
            "Physical Chemistry I (Practical)",
            "Organic Chemistry I (Practical)",
            "Create Development Skills",
            "Analytical Chemistry (Practical)",
        ],
        "2": [
            "Physical Chemistry II",
            "Stereochemistry",
            "Inorganic Chemistry",
            "Natural Products Chemistry",
            "Physical Chemistry II (Practical)",
            "Natural Products Chemistry (Practical)",
            "Inorganic Chemistry (Practical)",
        ],
    },
    "3": {
        "1": [
            "Polymer Chemistry (Practical)",
            "Organic Chemistry II (Practical)",
            "Organic Chemistry II",
            "Surface Chemistry",
            "Biochemistry",
            "Biochemistry (Practical)",
            "Polymer Chemistry",
        ],
        "2": [
            "Separation Techniques (Practical)",
            "Industrial Chemistry",
            "Separation Techniques",
            "Organometallic Chemistry",
            "Clinical Biochemistry",
            "Clinical Biochemistry (Practical)",
        ],
    },
    "4": {
        "1": [
            "Nanochemistry",
            "Petroleum Chemistry",
            "Instrumental Analysis",
            "Quantum Chemistry",
            "Nanochemistry (Practical)",
            "Research work",
        ],
        "2": ["وانەی نموونە"],
    },
}


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def stages_menu():
    rows = [[Btn(n, callback_data=f"st|{k}")] for k, n in STAGES.items()]
    return "بەخێر بێیت بۆ بەشی زانستی کیمیا\n\nتکایە لە خوارەوە قۆناغەکەی خۆت هەڵبژێرە", Markup(rows)


def semesters_menu(st):
    rows = [[Btn(n, callback_data=f"sm|{st}|{k}")] for k, n in SEMESTERS.items()]
    rows.append([Btn("🔙 گەڕانەوە", callback_data="home")])
    return f"{STAGES[st]}\n\nسیمستەرەکە هەڵبژێرە", Markup(rows)


def subjects_menu(st, sm):
    rows = [[Btn(n, callback_data=f"sb|{st}|{sm}|{i}")]
            for i, n in enumerate(SUBJECTS[st][sm])]
    rows.append([Btn("🔙 گەڕانەوە", callback_data=f"st|{st}")])
    return f"{STAGES[st]} - {SEMESTERS[sm]}\n\nوانەکە هەڵبژێرە", Markup(rows)


def lectures_menu(st, sm, sb):
    name = SUBJECTS[st][sm][int(sb)]
    nums = [Btn(f"Lecture {n}", callback_data=f"lc|{st}|{sm}|{sb}|{n}")
            for n in range(1, MAX_LECTURES + 1)]
    rows = [nums[i:i+2] for i in range(0, len(nums), 2)]
    rows.append([Btn("🔙 گەڕانەوە", callback_data=f"sm|{st}|{sm}")])
    return f"📚 {name}\n\nکام Lecture دەتەوێت؟ (١ تا {MAX_LECTURES})", Markup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, kb = stages_menu()
    await update.message.reply_text(text, reply_markup=kb)


async def admin_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ئەدمین: کردنەوە/داخستنی دۆخی ئەپلۆد"""
    if update.effective_user.id != ADMIN_ID:
        return
    on = not context.user_data.get("admin_mode", False)
    context.user_data["admin_mode"] = on
    context.user_data.pop("target", None)
    await update.message.reply_text(
        "🛠 دۆخی ئەدمین کرایەوە.\nلە /start وانەکە هەڵبژێرە، Lecture دابگرە، پاشان فایلەکە بنێرە."
        if on else "✅ دۆخی ئەدمین داخرا (وەک قوتابی دەبینیت)."
    )


async def ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ئەدمین: لیستی ژمارەی وانەکان بۆ caption"""
    if update.effective_user.id != ADMIN_ID:
        return
    lines = []
    for st, sems in SUBJECTS.items():
        for sm, subs in sems.items():
            lines.append(f"\n== قۆناغ {st} / سیمستەر {sm} ==")
            for i, name in enumerate(subs):
                lines.append(f"{st}|{sm}|{i}  ->  {name}")
    text = "\n".join(lines)
    for i in range(0, len(text), 3500):
        await update.message.reply_text(text[i:i+3500])


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    p = q.data.split("|")

    if p[0] == "home":
        text, kb = stages_menu()
    elif p[0] == "st":
        text, kb = semesters_menu(p[1])
    elif p[0] == "sm":
        text, kb = subjects_menu(p[1], p[2])
    elif p[0] == "sb":
        text, kb = lectures_menu(p[1], p[2], p[3])
    elif p[0] == "lc":
        if q.from_user.id == ADMIN_ID and context.user_data.get("admin_mode"):
            key = "|".join(p[1:])
            context.user_data["target"] = key
            st, sm, sb, lc = p[1], p[2], p[3], p[4]
            await q.message.reply_text(
                f"📤 فایلی ئەم لێکچەرە بنێرە:\n{SUBJECTS[st][sm][int(sb)]} ← Lecture {lc}"
            )
            return
        entry = load_db().get("|".join(p[1:]))
        if entry:
            if isinstance(entry, str):  # فایلی کۆن
                entry = {"id": entry, "name": ""}
            await q.message.reply_document(entry["id"], caption=entry["name"] or f"Lecture {p[4]}")
        else:
            await q.message.reply_text("⚠️ ئەم لێکچەرە هێشتا نەخراوەتە سەر.")
        return
    await q.edit_message_text(text, reply_markup=kb)


# ئەدمین: تەنها فایل بنێرە، پاشان بە دوگمە شوێنەکەی هەڵبژێرە (بێ caption، بێ ژمارە)
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    doc = update.message.document
    if not doc:
        await update.message.reply_text("❌ فایلەکە دەبێت وەک File بنێریت، نەک وێنە.")
        return
    name = os.path.splitext(doc.file_name or "")[0].strip()
    target = context.user_data.get("target")
    if target:
        st, sm, sb, lc = target.split("|")
        db = load_db()
        db[target] = {"id": doc.file_id, "name": name}
        save_db(db)
        await update.message.reply_text(
            f"✅ خرایە ناو Lecture {lc}:\n{SUBJECTS[st][sm][int(sb)]}\n\nدەتوانیت Lecture ی تر دابگریت."
        )
        return
    context.user_data["pending"] = {"id": doc.file_id, "name": name}
    rows = [[Btn(n, callback_data=f"u|st|{k}")] for k, n in STAGES.items()]
    await update.message.reply_text("📥 ئەم فایلە بۆ کام قۆناغە؟", reply_markup=Markup(rows))


async def upload_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ئەدمین: هەڵبژاردنی شوێنی فایل بە دوگمە (بێ caption)"""
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer()
        return
    await q.answer()
    p = q.data.split("|")  # u|step|...
    step = p[1]

    if step == "st":
        rows = [[Btn(n, callback_data=f"u|sm|{p[2]}|{k}")] for k, n in SEMESTERS.items()]
        await q.edit_message_text(f"{STAGES[p[2]]}\n\nکام سیمستەر؟", reply_markup=Markup(rows))
    elif step == "sm":
        st, sm = p[2], p[3]
        rows = [[Btn(n, callback_data=f"u|sb|{st}|{sm}|{i}")]
                for i, n in enumerate(SUBJECTS[st][sm])]
        await q.edit_message_text("کام وانە؟", reply_markup=Markup(rows))
    elif step == "sb":
        st, sm, sb = p[2], p[3], p[4]
        nums = [Btn(f"Lecture {n}", callback_data=f"u|lc|{st}|{sm}|{sb}|{n}")
                for n in range(1, MAX_LECTURES + 1)]
        rows = [nums[i:i+3] for i in range(0, len(nums), 3)]
        await q.edit_message_text("کام Lecture؟", reply_markup=Markup(rows))
    elif step == "lc":
        st, sm, sb, lc = p[2], p[3], p[4], p[5]
        pending = context.user_data.get("pending")
        if not pending:
            await q.edit_message_text("❌ فایلەکە نەماوە، دووبارە بینێرە.")
            return
        db = load_db()
        db[f"{st}|{sm}|{sb}|{lc}"] = pending
        save_db(db)
        context.user_data.pop("pending", None)
        await q.edit_message_text(f"✅ پاشەکەوت کرا:\n{SUBJECTS[st][sm][int(sb)]}\nLecture {lc}")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ids", ids))
app.add_handler(CommandHandler("admin", admin_mode))
app.add_handler(CallbackQueryHandler(upload_buttons, pattern=r"^u\|"))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.Document.ALL, upload))
app.run_polling()
