import os, sqlite3, asyncio, bcrypt, io
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app
from PyPDF2 import PdfReader

# --- CONFIG ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DB = "legalos_v5.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS dossiers(id INTEGER PRIMARY KEY, user_id INTEGER, nom TEXT, date TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, dossier_id INTEGER, role TEXT, content TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS docs(id INTEGER PRIMARY KEY, dossier_id INTEGER, name TEXT, content TEXT)")
init_db()

STEPS = ["Qualification","Stratégie","Base légale","Inventaire","Risques","Amiable","Action","Rédaction","Audience"]

# --- IA MULTI ROLE ---
async def call_kareem(msg, step, history, docs="", mode="strategist"):
    roles = {
        "strategist": "Stratège juridique expert (Méthode Freeman)",
        "opponent": "Avocat adverse agressif cherchant les failles",
        "judge": "Juge impartial et exigeant",
        "writer": "Juriste rédacteur d'actes"
    }
    
    system = f"""Tu es Kareem. Rôle : {roles.get(mode)}. 
    Style : Direct, sans politesse inutile. Étape actuelle : {step}.
    Analyse les documents fournis et l'historique pour donner une réponse technique."""

    messages = [{"role":"system","content":system}]
    for h in history[-6:]:
        messages.append({"role":h[0],"content":h[1]})
    messages.append({"role":"user","content":msg + f"\n\nDOCS: {docs[:4000]}"})

    res = await asyncio.to_thread(client.chat.completions.create, 
                                  model="llama-3.3-70b-versatile", 
                                  messages=messages)
    return res.choices[0].message.content

# --- UI COMPONENTS ---
def message_bubble(role, text):
    with ui.column().classes(f'w-full gap-1 {"items-end" if role == "user" else "items-start"}'):
        ui.label(role.upper()).classes('text-[10px] text-slate-500 font-bold px-2')
        with ui.card().classes(f'p-3 rounded-2xl shadow-none {"bg-emerald-600 text-white" if role == "user" else "bg-slate-800 text-slate-100"}'):
            ui.markdown(text).classes('text-sm')

# --- PAGES ---

@ui.page('/')
def login():
    ui.query('body').style("background-color: #0b0e14;")
    with ui.card().classes('absolute-center p-8 bg-[#141820] text-white border border-white/5 w-96 rounded-2xl'):
        ui.label("LEGAL OS V5").classes('text-3xl font-black text-emerald-500 mb-6 text-center')
        email = ui.input("Email").props('dark outlined color=emerald').classes('w-full mb-2')
        pwd = ui.input("Mot de passe", password=True).props('dark outlined color=emerald').classes('w-full mb-6')

        def connect():
            with sqlite3.connect(DB) as conn:
                u = conn.execute("SELECT id,password FROM users WHERE email=?", (email.value,)).fetchone()
            if u and bcrypt.checkpw(pwd.value.encode(), u[1]):
                app.storage.user.update({"id":u[0], "authenticated": True})
                ui.navigate.to('/dashboard')
            else: ui.notify("Erreur d'accès", color='red')

        ui.button("CONNEXION", on_click=connect).classes('w-full bg-emerald-600 font-bold py-4 rounded-xl')

@ui.page('/dashboard')
def dashboard():
    if not app.storage.user.get('authenticated'): return ui.navigate.to('/')
    uid = app.storage.user.get("id")
    
    ui.query('body').style("background-color: #0b0e14; color: white;")
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8'):
        ui.label("Mes Dossiers").classes('text-4xl font-black mb-8')
        
        with ui.row().classes('w-full mb-8 gap-2'):
            nom = ui.input(placeholder="Nom du nouveau litige...").props('dark outlined').classes('flex-grow')
            ui.button(icon='add', on_click=lambda: create(nom.value)).props('round color=emerald')

        def create(n):
            with sqlite3.connect(DB) as conn:
                conn.execute("INSERT INTO dossiers VALUES(NULL,?,?,?)",(uid,n,str(datetime.now())))
            ui.navigate.to('/dashboard')

        with sqlite3.connect(DB) as conn:
            dossiers = conn.execute("SELECT id,nom FROM dossiers WHERE user_id=?", (uid,)).fetchall()

        for d in dossiers:
            with ui.card().classes('w-full bg-slate-900 border border-white/5 mb-2 hover:border-emerald-500 cursor-pointer'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(d[1]).classes('font-bold text-lg')
                    ui.button(icon='login', on_click=lambda d=d: ui.navigate.to(f"/d/{d[0]}")).props('flat color=emerald')

@ui.page('/d/{d_id}')
async def dossier_page(d_id: int):
    if not app.storage.user.get('authenticated'): return ui.navigate.to('/')
    
    ui.query('body').style("background-color: #0b0e14; color: white;")
    step_idx = app.storage.user.get(f"s_{d_id}", 0)

    # Drawer (Méthode Freeman)
    with ui.left_drawer().classes('bg-[#0b0e14] border-r border-white/5'):
        ui.label("MÉTHODE FREEMAN").classes('text-xs font-black text-emerald-500 p-4 tracking-widest')
        for i, s in enumerate(STEPS):
            active = (i == step_idx)
            ui.button(f"{i+1}. {s}", on_click=lambda i=i: set_step(d_id, i)).props(f'flat {"color=emerald" if active else "color=slate-400"}').classes('w-full justify-start py-2')

    # Chat Area
    with ui.column().classes('w-full max-w-3xl mx-auto p-4 pb-40'):
        with sqlite3.connect(DB) as conn:
            hist = conn.execute("SELECT role,content FROM messages WHERE dossier_id=? ORDER BY id ASC", (d_id,)).fetchall()
            docs = conn.execute("SELECT content FROM docs WHERE dossier_id=?", (d_id,)).fetchall()
        
        docs_text = "\n".join([d[0] for d in docs])
        chat_container = ui.column().classes('w-full gap-4')
        
        with chat_container:
            for h in hist:
                message_bubble(h[0], h[1])

        # Input Area (Fixed bottom)
        with ui.footer().classes('bg-[#0b0e14] p-4'):
            with ui.row().classes('w-full max-w-3xl mx-auto items-center gap-2'):
                # Boutons de simulation
                with ui.row().classes('w-full mb-2 justify-center gap-2'):
                    ui.button("⚔️ ADVERSAIRE", on_click=lambda: simulate("opponent")).props('small outline color=red')
                    ui.button("⚖️ JUGE", on_click=lambda: simulate("judge")).props('small outline color=blue')
                
                msg_input = ui.input(placeholder="Parlez à Kareem...").props('dark outlined color=emerald').classes('flex-grow')
                
                async def send_msg():
                    txt = msg_input.value
                    if not txt: return
                    msg_input.value = ""
                    with chat_container: message_bubble("user", txt)
                    
                    with sqlite3.connect(DB) as conn:
                        conn.execute("INSERT INTO messages (dossier_id, role, content) VALUES (?,?,?)", (d_id, "user", txt))
                    
                    res = await call_kareem(txt, STEPS[step_idx], hist, docs_text)
                    with chat_container: message_bubble("assistant", res)
                    
                    with sqlite3.connect(DB) as conn:
                        conn.execute("INSERT INTO messages (dossier_id, role, content) VALUES (?,?,?)", (d_id, "assistant", res))
                    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

                async def simulate(mode):
                    res = await call_kareem("Analyse critique immédiate.", STEPS[step_idx], hist, docs_text, mode=mode)
                    with ui.dialog().open(), ui.card().classes('bg-slate-900 text-white p-6 max-w-xl'):
                        ui.label(f"SIMULATION : {mode.upper()}").classes('text-emerald-500 font-bold mb-4')
                        ui.markdown(res)

                ui.button(icon='send', on_click=send_msg).props('round color=emerald')
                ui.upload(on_upload=lambda e: handle_upload(d_id, e), auto_upload=True).props('flat icon=attach_file color=slate-400').classes('w-12')

async def handle_upload(d_id, e):
    text = read_pdf(e.content.read())
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO docs (dossier_id, name, content) VALUES (?,?,?)", (d_id, e.name, text))
    ui.notify(f"Document {e.name} indexé", color='emerald')
    ui.navigate.to(f"/d/{d_id}")

def read_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join([p.extract_text() for p in reader.pages])[:8000]

def set_step(d_id, i):
    app.storage.user.update({f"s_{d_id}": i})
    ui.navigate.to(f"/d/{d_id}")

ui.run(storage_secret="LEGAL_OS_SECRET_2026", port=8080)
