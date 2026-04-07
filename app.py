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

# --- DB INIT ---
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS dossiers(id INTEGER PRIMARY KEY, user_id INTEGER, nom TEXT, date TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, dossier_id INTEGER, role TEXT, content TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS docs(id INTEGER PRIMARY KEY, dossier_id INTEGER, name TEXT, content TEXT)")
init_db()

# --- STEPS ---
STEPS = ["Qualification","Stratégie","Base légale","Inventaire","Risques","Amiable","Action","Rédaction","Audience","Jugement","Recours"]

# --- IA MULTI ROLE ---
async def call_kareem(msg, step, history, docs="", mode="strategist"):
    roles = {
        "strategist": "Stratège juridique expert",
        "opponent": "Avocat adverse destructeur",
        "judge": "Juge impartial",
        "writer": "Juriste rédacteur"
    }

    system = f"""
    Tu es Kareem.

    Rôle : {roles.get(mode)}

    Style :
    - phrases courtes
    - logique froide
    - pas d'émotion

    Étape : {step}

    Méthode :
    1. Analyse
    2. Failles / forces
    3. Action

    Documents :
    {docs[:4000]}
    """

    messages = [{"role":"system","content":system}]
    for h in history[-6:]:
        messages.append({"role":h[0],"content":h[1]})
    messages.append({"role":"user","content":msg})

    res = await asyncio.to_thread(
        client.chat.completions.create,
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    return res.choices[0].message.content

# --- PDF READ ---
def read_pdf(file):
    reader = PdfReader(io.BytesIO(file))
    text = ""
    for p in reader.pages:
        text += p.extract_text() or ""
    return text[:8000]

# --- SCORE ---
def score_case(hist, docs):
    score = min(95, 50 + len(hist)*2 + len(docs)*5)
    return score

# --- ACTES ---
def generate_assignation(data):
    return f"""
TRIBUNAL JUDICIAIRE

EXPOSÉ DES FAITS :
{data}

MOYENS :
Articles + jurisprudence

PAR CES MOTIFS :
Condamnation demandée.

Fait le {datetime.now().strftime('%d/%m/%Y')}
"""

# --- AUTH ---
def hash_pwd(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt())
def check_pwd(p,h): return bcrypt.checkpw(p.encode(), h)

# --- LOGIN ---
@ui.page('/')
def login():
    ui.label("LEGAL OS V5").classes('text-2xl')
    email = ui.input("Email")
    pwd = ui.input("Mot de passe", password=True)

    def connect():
        with sqlite3.connect(DB) as conn:
            u = conn.execute("SELECT id,password FROM users WHERE email=?", (email.value,)).fetchone()
        if u and check_pwd(pwd.value, u[1]):
            app.storage.user.update({"id":u[0]})
            ui.navigate.to('/dashboard')

    def register():
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO users VALUES(NULL,?,?)",(email.value,hash_pwd(pwd.value)))

    ui.button("Connexion", on_click=connect)
    ui.button("Créer compte", on_click=register)

# --- DASHBOARD ---
@ui.page('/dashboard')
def dashboard():
    uid = app.storage.user.get("id")
    if not uid: return ui.navigate.to('/')

    ui.label("Dossiers")

    with sqlite3.connect(DB) as conn:
        dossiers = conn.execute("SELECT id,nom FROM dossiers WHERE user_id=?", (uid,)).fetchall()

    for d in dossiers:
        with ui.row():
            ui.button(d[1], on_click=lambda d=d: ui.navigate.to(f"/d/{d[0]}"))
            ui.button("Supprimer", on_click=lambda d=d: delete_d(d[0]))

    nom = ui.input("Nom dossier")

    def create():
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO dossiers VALUES(NULL,?,?,?)",(uid,nom.value,str(datetime.now())))
        ui.navigate.to('/dashboard')

    def delete_d(id):
        with sqlite3.connect(DB) as conn:
            conn.execute("DELETE FROM dossiers WHERE id=?", (id,))
        ui.navigate.to('/dashboard')

    ui.button("Créer dossier", on_click=create)

# --- DOSSIER ---
@ui.page('/d/{d_id}')
async def dossier(d_id:int):
    uid = app.storage.user.get("id")
    if not uid: return ui.navigate.to('/')

    step = app.storage.user.get(f"s_{d_id}",0)

    # STEPS
    with ui.row():
        for i,s in enumerate(STEPS):
            ui.button(s, on_click=lambda i=i: set_step(d_id,i))

    # DATA
    with sqlite3.connect(DB) as conn:
        hist = conn.execute("SELECT role,content FROM messages WHERE dossier_id=?", (d_id,)).fetchall()
        docs = conn.execute("SELECT content FROM docs WHERE dossier_id=?", (d_id,)).fetchall()

    docs_text = "\n".join([d[0] for d in docs])

    # SCORE
    ui.label(f"Score juridique : {score_case(hist, docs)}%")

    # CHAT
    for h in hist:
        ui.label(f"{h[0]} : {h[1]}")

    msg = ui.input("Message")

    async def send():
        txt = msg.value
        msg.value = ""

        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO messages VALUES(NULL,?,?,?)",(d_id,"user",txt))

        res = await call_kareem(txt, STEPS[step], hist, docs_text)

        label = ui.label("")
        for c in res:
            label.text += c
            await asyncio.sleep(0.005)

        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO messages VALUES(NULL,?,?,?)",(d_id,"assistant",res))

    ui.button("Envoyer", on_click=send)

    # UPLOAD
    def upload(e):
        text = read_pdf(e.content.read())
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO docs VALUES(NULL,?,?,?)",(d_id,e.name,text))
        ui.notify("Document analysé")

    ui.upload(on_upload=upload)

    # ACTIONS
    async def opponent():
        res = await call_kareem("Attaque ce dossier", STEPS[step], hist, docs_text, mode="opponent")
        ui.dialog().open().add(ui.markdown(res))

    async def judge():
        res = await call_kareem("Donne un avis de juge", STEPS[step], hist, docs_text, mode="judge")
        ui.dialog().open().add(ui.markdown(res))

    ui.button("⚔️ Adversaire", on_click=opponent)
    ui.button("⚖️ Juge", on_click=judge)

    # ACTES
    ui.button("📄 Assignation", on_click=lambda: ui.textarea(value=generate_assignation("faits à compléter")).classes('w-full'))

def set_step(d_id,i):
    app.storage.user.update({f"s_{d_id}":i})
    ui.navigate.to(f"/d/{d_id}")

# --- RUN ---
ui.run()
