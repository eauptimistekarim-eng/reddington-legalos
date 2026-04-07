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
stripe.api_key = os.getenv("STRIPE_KEY")
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
    TON STYLE : Précis, tranchant, sans fioritures. Tu parles comme un expert du droit français.
    CONTEXTE ÉTAPE : {step}.
    DOCUMENTS ANALYSÉS : {context_docs}
    CONSIGNE : Analyse la demande, réponds avec autorité et pose une question stratégique pour avancer."""
    
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

# --- INTERFACE ---

@ui.page('/')
def login_page():
    ui.query('body').style("background-color: #0b0e14; font-family: 'Inter', sans-serif;")
    with ui.card().classes('absolute-center p-12 bg-[#141820] border border-white/5 shadow-2xl w-full max-w-md rounded-2xl'):
        ui.label('LEGAL OS').classes('text-3xl font-black text-emerald-500 mb-2 text-center tracking-tighter')
        ui.label('Intelligence Juridique Freeman').classes('text-slate-500 text-sm mb-8 text-center')
        
        email = ui.input("Email").props('dark outlined color=emerald').classes('w-full mb-4')
        pwd = ui.input("Mot de passe", password=True).props('dark outlined color=emerald').classes('w-full mb-6')

        async def auth():
            with sqlite3.connect(DB) as conn:
                u = conn.execute("SELECT id, password FROM users WHERE email=?", (email.value,)).fetchone()
            if u and bcrypt.checkpw(pwd.value.encode(), u[1]):
                app.storage.user.update({"id": u[0]})
                ui.navigate.to("/dashboard")
            else: ui.notify("Identifiants incorrects", color='red')

        ui.button("ACCÉDER À L'INTERFACE", on_click=auth).classes('w-full py-4 bg-emerald-600 font-bold rounded-xl')

@ui.page('/dashboard')
def dashboard():
    uid = app.storage.user.get("id")
    if not uid: return ui.navigate.to('/')
    ui.query('body').style("background-color: #0b0e14; color: white;")

    with ui.column().classes('w-full max-w-4xl mx-auto p-8'):
        ui.label('Tableau de bord').classes('text-4xl font-black mb-12 tracking-tight')
        
        with ui.row().classes('w-full gap-4 mb-12'):
            nom = ui.input(placeholder="Nom du nouveau litige...").props('dark outlined color=emerald').classes('flex-grow')
            ui.button('CRÉER DOSSIER', on_click=lambda: create_d(uid, nom.value)).classes('bg-emerald-600 px-8 rounded-lg')

        with sqlite3.connect(DB) as conn:
            dossiers = conn.execute("SELECT id, nom, date FROM dossiers WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
        
        for d in dossiers:
            with ui.card().classes('w-full bg-[#141820] border border-white/5 p-6 mb-4 hover:border-emerald-500/50 transition-all cursor-pointer rounded-xl'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column():
                        ui.label(d[1]).classes('text-xl font-bold text-slate-100')
                        ui.label(f"Créé le {d[2][:10]}").classes('text-xs text-slate-500')
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
            is_active = (i == current_
