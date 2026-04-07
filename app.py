import os, sqlite3, asyncio, bcrypt, stripe, io
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# --- CONFIGURATION ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DB = "legalos_v4.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS dossiers(id INTEGER PRIMARY KEY, user_id INTEGER, nom TEXT, date TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, dossier_id INTEGER, role TEXT, content TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS docs(id INTEGER PRIMARY KEY, dossier_id INTEGER, path TEXT, content TEXT)")
init_db()

STEPS = ["Qualification", "Stratégie", "Base légale", "Inventaire", "Risques", "Amiable", "Action", "Rédaction", "Audience"]

# --- LOGIQUE IA (KAREEM) ---
async def call_kareem(msg, step, history, context_docs=""):
    system = f"""Tu es Kareem, une IA juridique d'élite. 
    TON STYLE : Précis, stratégique, utilisant la méthode Freeman. 
    ÉTAPE ACTUELLE : {step}.
    DOCUMENTS ANALYSÉS : {context_docs}
    CONSIGNE : Analyse la situation et propose une étape concrète."""
    
    messages = [{"role": "system", "content": system}]
    for h in history[-8:]:
        messages.append({"role": h[0], "content": h[1]})
    messages.append({"role": "user", "content": msg})

    res = await asyncio.to_thread(client.chat.completions.create, model="llama-3.3-70b-versatile", messages=messages)
    return res.choices[0].message.content

# --- UTILITAIRES ---
def get_pdf_text(file_content):
    try:
        reader = PdfReader(io.BytesIO(file_content))
        return "\n".join([p.extract_text() for p in reader.pages])[:8000]
    except: return ""

def generate_pdf_report(d_id):
    filename = f"Rapport_Kareem_{d_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph(f"DOSSIER JURIDIQUE #{d_id}", styles['Title']), Spacer(1, 20)]
    with sqlite3.connect(DB) as conn:
        msgs = conn.execute("SELECT role, content FROM messages WHERE dossier_id=?", (d_id,)).fetchall()
    for role, content in msgs:
        label = "VOUS" if role == "user" else "KAREEM"
        elements.append(Paragraph(f"<b>{label}:</b> {content}", styles['Normal']))
        elements.append(Spacer(1, 10))
    doc.build(elements)
    return filename

# --- PAGES ---

@ui.page('/')
def login_page():
    ui.query('body').style("background-color: #0b0e14;")
    with ui.card().classes('absolute-center p-12 bg-[#141820] border border-white/5 shadow-2xl w-full max-w-md rounded-2xl'):
        ui.label('LEGAL OS').classes('text-3xl font-black text-emerald-500 mb-2 text-center tracking-tighter')
        ui.label('Interface Kareem').classes('text-slate-500 text-sm mb-8 text-center')
        
        email = ui.input("Email").props('dark outlined color=emerald').classes('w-full mb-4')
        pwd = ui.input("Mot de passe", password=True).props('dark outlined color=emerald').classes('w-full mb-6')

        async def auth():
            with sqlite3.connect(DB) as conn:
                u = conn.execute("SELECT id, password FROM users WHERE email=?", (email.value,)).fetchone()
            if u and bcrypt.checkpw(pwd.value.encode(), u[1]):
                app.storage.user.update({"id": u[0]})
                ui.navigate.to("/dashboard")
            else: ui.notify("Identifiants incorrects", color='red')

        ui.button("DÉMARRER LA SESSION", on_click=auth).classes('w-full py-4 bg-emerald-600 font-bold rounded-xl')

@ui.page('/dashboard')
def dashboard():
    uid = app.storage.user.get("id")
    if not uid: return ui.navigate.to('/')
    ui.query('body').style("background-color: #0b0e14; color: white;")

    with ui.column().classes('w-full max-w-4xl mx-auto p-8'):
        ui.label('Dossiers en cours').classes('text-4xl font-black mb-12 tracking-tight')
        
        with ui.row().classes('w-full gap-4 mb-12'):
            nom = ui.input(placeholder="Nom du litige...").props('dark outlined color=emerald').classes('flex-grow')
            ui.button('CRÉER', on_click=lambda: create_d(uid, nom.value)).classes('bg-emerald-600 px-8 rounded-lg')

        with sqlite3.connect(DB) as conn:
            dossiers = conn.execute("SELECT id, nom, date FROM dossiers WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
        
        for d in dossiers:
            with ui.card().classes('w-full bg-[#141820] border border-white/5 p-6 mb-4 hover:border-emerald-500 transition-all cursor-pointer rounded-xl'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(d[1]).classes('text-xl font-bold text-slate-100')
                    ui.button('OUVRIR', on_click=lambda d=d: ui.navigate.to(f"/d/{d[0]}")).props('flat color=emerald')

def create_d(uid, nom):
    if not nom: return
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO dossiers VALUES(NULL,?,?,?)", (uid, nom, str(datetime.now())))
    ui.navigate.to('/dashboard')

@ui.page('/d/{d_id}')
async def dossier_view(d_id: int):
    uid = app.storage.user.get("id")
    if not uid: return ui.navigate.to('/')
    
    current_s = app.storage.user.get(f"s_{d_id}", 0)
    ui.query('body').style("background-color: #0b0e14; color: white;")

    # Navigation latérale
    with ui.left_drawer().classes('bg-[#0b0e14] border-r border-white/5 p-4'):
        ui.label('MÉTHODE FREEMAN').classes('text-[10px] font-black text-emerald-500 mb-6 px-4 tracking-widest')
        for i, s in enumerate(STEPS):
            is_active = (i == current_s)
            with ui.row().classes(f'w-full p-3 rounded-lg cursor-pointer mb-1 {"bg-emerald-500/10 text-emerald-400" if is_active else "text-slate-400 hover:bg-white/5"}'):
                ui.label(f"{i+1}. {s}").on('click', lambda i=i: set_step(d_id, i))

    # Zone de Chat
    chat_box = ui.column().classes('w-full max-w-3xl mx-auto p-6 pb-44 gap-8')
    
    with chat_box:
        with sqlite3.connect(DB) as conn:
            hist = conn.execute("SELECT role, content FROM messages WHERE dossier_id=? ORDER BY id ASC", (d_id,)).fetchall()
            docs = conn.execute("SELECT content FROM docs WHERE dossier_id=?", (d_id,)).fetchall()
            context_text = "\n".join([doc[0] for doc in docs])

        for role, text in hist:
            is_ai = (role == 'assistant')
            with ui.row().classes(f'w-full gap-4 no-wrap {"justify-end" if not is_ai else "justify-start"}'):
                if is_ai: ui.icon('smart_toy').classes('p-2 rounded-lg bg-blue-600')
                ui.markdown(text).classes(f'p-4 rounded-2xl max-w-xl {"bg-emerald-900/40" if not is_ai else "bg-slate-800/40 text-slate-200"}')
                if not is_ai: ui.icon('person').classes('p-2 rounded-lg bg-emerald-600')

    # Barre de saisie flottante
    with ui.footer().classes('bg-transparent p-6'):
        with ui.row().classes('w-full max-w-3xl mx-auto bg-[#1e293b]/90 backdrop-blur rounded-2xl p-3 shadow-2xl border border-white/10 items-center'):
            with ui.button(icon='attach_file').props('flat color=slate-400'):
                ui.upload(on_upload=lambda e: handle_up(d_id, e), auto_upload=True).classes('absolute opacity-0 w-full h-full')
            
            msg_in = ui.input(placeholder="Posez votre question...").props('dark borderless').classes('flex-grow px-4')
            
            async def send():
                v = msg_in.value
                if not v: return
                msg_in.value = ""
                
                with chat_box:
                    ui.markdown(v).classes('p-4 rounded-2xl bg-emerald-900/40 self-end max-w-xl')
                    res_area = ui.markdown("...").classes('p-4 rounded-2xl bg-slate-800/40 self-start max-w-xl text-slate-200')
                
                with sqlite3.connect(DB) as conn:
                    conn.execute("INSERT INTO messages (dossier_id, role, content) VALUES (?,?,?)", (d_id, "user", v))
                
                full_res = await call_kareem(v, STEPS[current_s], hist, context_text)
                res_area.content = ""
                for char in full_res:
                    res_area.content += char
                    await asyncio.sleep(0.003)
                
                with sqlite3.connect(DB) as conn:
                    conn.execute("INSERT INTO messages (dossier_id, role, content) VALUES (?,?,?)", (d_id, "assistant", full_res))

            ui.button(icon='send', on_click=send).props('round color=emerald')

async def handle_up(d_id, e):
    content = get_pdf_text(e.content.read())
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO docs (dossier_id, path, content) VALUES (?,?,?)", (d_id, e.name, content))
    ui.notify(f"Document {e.name} analysé.")
    await asyncio.sleep(1)
    ui.navigate.to(f"/d/{d_id}")

def set_step(d_id, i):
    app.storage.user.update({f"s_{d_id}": i})
    ui.navigate.to(f"/d/{d_id}")

ui.run(storage_secret="KAREEM_KEY_2026", port=8080)
