import os, sqlite3, asyncio, bcrypt
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- CONFIG ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DB = "legalos_v3.db"

# --- DB INITIALIZATION ---
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS dossiers(id INTEGER PRIMARY KEY, user_id INTEGER, nom TEXT, archive INTEGER DEFAULT 0, date TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, dossier_id INTEGER, role TEXT, content TEXT)")
init_db()

STEPS = ["Qualification","Objectif","Base légale","Inventaire","Risques","Amiable","Attaque","Rédaction","Audience","Jugement","Recours"]

# --- LOGIQUE IA KAREEM ---
async def call_kareem(msg, step, history):
    system = f"Tu es Kareem. Style: précis, stratégique, froid. Méthode Freeman. Étape: {step}. Pose des questions chirurgicales."
    messages = [{"role": "system", "content": system}]
    for h in history[-6:]:
        messages.append({"role": h[0], "content": h[1]})
    messages.append({"role": "user", "content": msg})

    response = await asyncio.to_thread(client.chat.completions.create, model="llama-3.3-70b-versatile", messages=messages, temperature=0.3)
    return response.choices[0].message.content

# --- AUTH UTILS ---
def hash_pwd(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt())
def check_pwd(p,h): return bcrypt.checkpw(p.encode(), h)

# --- UI PAGES ---

@ui.page('/')
def login():
    ui.query('body').style('background-color: #020617; color: white;')
    with ui.card().classes('absolute-center p-10 bg-slate-900 border border-emerald-500/20 shadow-2xl rounded-2xl w-96'):
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 text-center mb-6')
        email = ui.input("Email").props('dark outlined color=emerald').classes('w-full mb-4')
        pwd = ui.input("Mot de passe", password=True).props('dark outlined color=emerald').classes('w-full mb-6')

        def connect():
            with sqlite3.connect(DB) as conn:
                u = conn.execute("SELECT id, password FROM users WHERE email=?", (email.value,)).fetchone()
            if u and check_pwd(pwd.value, u[1]):
                app.storage.user.update({"id": u[0], "email": email.value})
                ui.navigate.to('/dashboard')
            else: ui.notify('Identifiants invalides', color='red')

        def register():
            try:
                with sqlite3.connect(DB) as conn:
                    conn.execute("INSERT INTO users VALUES(NULL,?,?)", (email.value, hash_pwd(pwd.value)))
                ui.notify('Compte créé, connectez-vous')
            except: ui.notify('Erreur lors de la création')

        ui.button("CONNEXION", on_click=connect).classes('w-full bg-emerald-600 font-bold mb-2')
        ui.button("CRÉER COMPTE", on_click=register).props('flat color=slate-400').classes('w-full text-xs')

@ui.page('/dashboard')
def dashboard():
    if not app.storage.user.get("id"): return ui.navigate.to('/')
    ui.query('body').style('background-color: #020617;')
    uid = app.storage.user.get("id")

    with ui.column().classes('w-full max-w-4xl mx-auto p-8'):
        ui.label(f"DOSSIERS : {app.storage.user.get('email')}").classes('text-2xl font-black text-emerald-500 mb-8')
        
        with ui.row().classes('w-full gap-4 mb-12 items-center bg-slate-900 p-4 rounded-xl border border-slate-800'):
            nom = ui.input(placeholder="Nom du nouveau dossier...").props('dark borderless').classes('flex-grow px-4')
            ui.button('CRÉER', on_click=lambda: create_dossier(uid, nom.value)).classes('bg-emerald-600 px-8')

        with sqlite3.connect(DB) as conn:
            dossiers = conn.execute("SELECT id, nom, date FROM dossiers WHERE user_id=? AND archive=0", (uid,)).fetchall()
        
        for d in dossiers:
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 mb-2 hover:border-emerald-500/30 transition-all'):
                with ui.row().classes('w-full items-center p-2'):
                    ui.label(d[1]).classes('text-lg font-bold flex-grow cursor-pointer').on('click', lambda d=d: ui.navigate.to(f"/d/{d[0]}"))
                    ui.button(icon='archive', on_click=lambda d=d: archive_dossier(d[0])).props('flat color=slate-500')
                    ui.button(icon='delete', on_click=lambda d=d: delete_dossier(d[0])).props('flat color=red-800')

def create_dossier(uid, nom):
    if not nom: return
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO dossiers (user_id, nom, archive, date) VALUES(?,?,0,?)", (uid, nom, datetime.now().strftime("%d/%m/%Y")))
    ui.navigate.to('/dashboard')

def archive_dossier(id):
    with sqlite3.connect(DB) as conn: conn.execute("UPDATE dossiers SET archive=1 WHERE id=?", (id,))
    ui.navigate.to('/dashboard')

def delete_dossier(id):
    with sqlite3.connect(DB) as conn: conn.execute("DELETE FROM dossiers WHERE id=?", (id,)); conn.execute("DELETE FROM messages WHERE dossier_id=?", (id,))
    ui.navigate.to('/dashboard')

@ui.page('/d/{d_id}')
async def dossier_page(d_id: int):
    if not app.storage.user.get("id"): return ui.navigate.to('/')
    ui.query('body').style('background-color: #020617;')
    
    current_step_idx = app.storage.user.get(f"s_{d_id}", 0)

    # HEADER & NAV
    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')).props('flat color=emerald')
        ui.label(f'ETAPE : {STEPS[current_step_idx]}').classes('font-black text-emerald-500 uppercase tracking-widest')
        ui.button(icon='menu', on_click=lambda: drawer.toggle()).props('flat color=emerald')

    with ui.left_drawer().classes('bg-slate-950 border-r border-slate-900') as drawer:
        ui.label('NAVIGATION').classes('p-4 text-xs font-bold text-slate-500')
        for i, s in enumerate(STEPS):
            active = (i == current_step_idx)
            with ui.row().classes(f'w-full p-4 cursor-pointer {"bg-emerald-500/10" if active else ""}') as r:
                ui.label(s).classes(f'text-xs font-bold {"text-emerald-400" if active else "text-slate-500"}')
                r.on('click', lambda i=i: set_step(d_id, i))

    # CHAT AREA
    chat_box = ui.column().classes('w-full max-w-3xl mx-auto p-6 pb-40 gap-4')
    
    with sqlite3.connect(DB) as conn:
        hist = conn.execute("SELECT role, content FROM messages WHERE dossier_id=?", (d_id,)).fetchall()
    
    for h in hist:
        is_user = h[0] == "user"
        with ui.column().classes(f'w-full {"items-end" if is_user else "items-start"}'):
            ui.label(h[1]).classes(f'p-4 rounded-xl max-w-[80%] {"bg-emerald-700 text-white" if is_user else "bg-slate-800 text-slate-200"}')

    # FOOTER INPUT
    with ui.footer().classes('bg-transparent p-6'):
        with ui.card().classes('w-full max-w-3xl mx-auto bg-slate-900 border border-slate-700 p-4 shadow-2xl rounded-2xl'):
            with ui.row().classes('w-full items-center no-wrap'):
                ui.upload(label="DOCS").props('flat color=emerald').classes('w-20')
                msg_input = ui.input(placeholder="Parlez à Kareem...").props('dark borderless').classes('flex-grow px-4 text-white')
                
                async def send():
                    txt = msg_input.value
                    if not txt: return
                    msg_input.value = ""
                    
                    with chat_box:
                        ui.label(txt).classes('self-end p-4 rounded-xl bg-emerald-700 text-white mb-4')
                        # Kareem typing effect
                        response_label = ui.label("").classes('self-start p-4 rounded-xl bg-slate-800 text-slate-200 mb-4')
                    
                    with sqlite3.connect(DB) as conn:
                        conn.execute("INSERT INTO messages (dossier_id, role, content) VALUES(?,?,?)", (d_id, "user", txt))
                    
                    reply = await call_kareem(txt, STEPS[current_step_idx], hist)
                    
                    for char in reply:
                        response_label.text += char
                        await asyncio.sleep(0.005)
                    
                    with sqlite3.connect(DB) as conn:
                        conn.execute("INSERT INTO messages (dossier_id, role, content) VALUES(?,?,?)", (d_id, "assistant", reply))

                ui.button(icon='send', on_click=send).props('round color=emerald')

def set_step(d_id, i):
    app.storage.user.update({f"s_{d_id}": i})
    ui.navigate.to(f"/d/{d_id}")

# --- RUN ---
ui.run(storage_secret='SECRET_KEY_2026', dark=True)
