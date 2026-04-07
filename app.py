import os
import sqlite3
import asyncio
import json
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app
from datetime import datetime

# --- 1. SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

# --- 2. DB ROBUSTE ---
def init_db():
    conn = sqlite3.connect('legalos_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, nom TEXT, date_crea TEXT, statut TEXT DEFAULT "actif")')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history (dossier_id INTEGER, step_idx INTEGER, role TEXT, content TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- 3. MOTEUR KAREEM (LOGIQUE MÉTIER PAR ÉTAPE) ---
class FreemanEngine:
    def __init__(self):
        self.steps = ["Qualification", "Objectif", "Base Légale", "Inventaire", "Risques", "Amiable", "Attaque", "Rédaction", "Audience", "Jugement", "Recours"]

    def get_persona_prompt(self, step_idx):
        prompts = [
            "Étape 1: Qualification. Pose des questions chirurgicales pour transformer le récit en faits juridiques.",
            "Étape 2: Objectif. Questionne sur les priorités : Temps vs Argent vs Principe.",
            "Étape 3: Base Légale. TU DOIS citer des articles du Code Civil/Pénal et des jurisprudences réelles (Légifrance).",
            "Étape 4: Inventaire. Tu analyses les preuves. Demande à voir les documents et explique leur force probante.",
            "Étape 5: Risques. Calcule le % de succès. Propose des mesures de protection (ex: constat d'huissier, sauvegarde de preuve).",
            "Étape 6: Amiable. Rédige une mise en demeure formelle et un mail de diplomatie 'main tendue'.",
            "Étape 7: Attaque. Mode Machiavel. Anticipe les défenses adverses. Propose : Injonction, Saisie-conservatoire, Plainte.",
            "Étape 8: Rédaction. Propose de remplir des modèles de conclusions ou d'actes basés sur nos échanges.",
            "Étape 9: Audience. Tu es le JUGE. Challenge l'utilisateur en ping-pong : 'Que répondez-vous à l'argument X ?'.",
            "Étape 10: Jugement. Analyse le verdict. Relève les erreurs de droit ou les manques de motivation.",
            "Étape 11: Recours. Bilan stratégique : Appel, Cassation ou exécution forcée."
        ]
        return f"Tu es Kareem (IA Freeman). {prompts[step_idx]} Style : Concis, percutant, machine à écrire. Pose TOUJOURS une question pour avancer."

engine = FreemanEngine()

# --- 4. UI COMPONENTS ---
async def typewriter(label, text):
    full = ""
    for char in text:
        full += char
        label.set_content(full)
        await asyncio.sleep(0.005)

# --- 5. PAGES ---
@ui.page('/')
def main_entry():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    ui.navigate.to('/dossiers')

@ui.page('/login')
def login_page():
    with ui.card().classes('absolute-center p-12 w-96 bg-slate-900 border border-emerald-500/30 shadow-2xl rounded-2xl'):
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 mx-auto text-center tracking-tighter')
        ui.label('SYSTÈME FREEMAN').classes('text-[10px] text-center w-full mb-8 text-emerald-400/40 tracking-[0.3em]')
        email = ui.input('Identifiant pro').props('dark outlined color=emerald').classes('w-full mb-4')
        ui.button('ESSAI GRATUIT', on_click=lambda: (app.storage.user.update({'email': email.value, 'auth': True}), ui.navigate.to('/dossiers'))).classes('w-full bg-emerald-600 font-bold py-4 rounded-xl shadow-lg shadow-emerald-900/20')

@ui.page('/dossiers')
def dashboard():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    user_email = app.storage.user['email']
    ui.query('body').style('background-color: #020617;')

    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-6 justify-between items-center'):
        ui.label('CABINET VIRTUEL').classes('text-xl font-bold text-emerald-500 tracking-tight')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    with ui.column().classes('w-full p-8 max-w-5xl mx-auto'):
        # Barre d'action
        with ui.row().classes('w-full mb-12 gap-4 bg-slate-900/50 p-6 rounded-2xl border border-slate-800'):
            new_nom = ui.input(placeholder='Nommer le nouveau dossier...').props('dark borderless').classes('flex-grow text-xl')
            def create():
                if not new_nom.value: return
                conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
                c.execute("INSERT INTO dossiers (user_email, nom, date_crea) VALUES (?, ?, ?)", (user_email, new_nom.value, datetime.now().strftime("%d/%m/%Y")))
                conn.commit(); conn.close(); ui.navigate.to('/dossiers')
            ui.button('OUVRIR DOSSIER', on_click=create, icon='add').classes('bg-emerald-600 px-6 py-2 rounded-lg font-bold')

        # Liste
        ui.label('DOSSIERS EN COURS').classes('text-[10px] text-slate-500 font-bold mb-4 tracking-widest')
        conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
        c.execute("SELECT id, nom, date_crea FROM dossiers WHERE user_email=? AND statut='actif' ORDER BY id DESC", (user_email,))
        for d_id, d_nom, d_date in c.fetchall():
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 mb-3 hover:border-emerald-500/50 transition-all group'):
                with ui.row().classes('w-full items-center p-3'):
                    with ui.column().classes('flex-grow cursor-pointer').on('click', lambda d=d_id: ui.navigate.to(f'/workspace/{d}')):
                        ui.label(d_nom).classes('text-lg font-bold text-slate-200 group-hover:text-emerald-400')
                        ui.label(f"Ouvert le {d_date}").classes('text-xs text-slate-500 uppercase tracking-tighter')
                    with ui.row().classes('gap-2'):
                        ui.button(icon='email', on_click=lambda: ui.notify('Dossier envoyé par mail')).props('flat color=slate-500')
                        ui.button(icon='archive', on_click=lambda d=d_id: archive_d(d)).props('flat color=orange-500')
                        ui.button(icon='delete', on_click=lambda d=d_id: delete_d(d)).props('flat color=red-400')
        conn.close()

def archive_d(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor(); c.execute("UPDATE dossiers SET statut='archive' WHERE id=?", (id,)); conn.commit(); conn.close(); ui.navigate.to('/dossiers')
def delete_d(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor(); c.execute("DELETE FROM dossiers WHERE id=?", (id,)); conn.commit(); conn.close(); ui.navigate.to('/dossiers')

@ui.page('/workspace/{d_id}')
async def workspace(d_id: int):
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    if 'cur_step' not in app.storage.user: app.storage.user['cur_step'] = 0
    s_idx = app.storage.user['cur_step']
    ui.query('body').style('background-color: #020617;')

    # HEADER FIXE
    with ui.header().classes('bg-slate-950/90 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dossiers')).props('flat color=slate-400')
        ui.label(f"STRATÉGIE FREEMAN - DOSSIER {d_id}").classes('text-emerald-500 font-black tracking-tighter')
        ui.button(icon='more_vert').props('flat color=slate-500')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # BARRE ÉTAPES
        with ui.column().classes('w-72 bg-slate-950 border-r border-slate-900 p-4 h-full'):
            for i, name in enumerate(engine.steps):
                active = (i == s_idx)
                with ui.row().classes(f'w-full p-3 rounded-xl cursor-pointer mb-1 {"bg-emerald-500/10 border border-emerald-500/20 shadow-lg shadow-emerald-900/10" if active else "hover:bg-slate-900"}') as r:
                    ui.label(f"{i+1:02}").classes(f'text-[10px] font-black {"text-emerald-500" if active else "text-slate-700"}')
                    ui.label(name).classes(f'text-xs uppercase font-bold {"text-emerald-400" if active else "text-slate-500"}')
                    r.on('click', lambda i=i: (app.storage.user.update({'cur_step': i}), ui.navigate.to(f'/workspace/{d_id}')))

        # ZONE CHAT
        with ui.column().classes('flex-grow p-12 overflow-y-auto pb-64 items-center'):
            with ui.column().classes('w-full max-w-3xl gap-6'):
                ui.label(engine.steps[s_idx]).classes('text-5xl font-black text-white mb-4 tracking-tighter')
                with ui.card().classes('w-full bg-slate-900/50 border border-slate-800 p-8 rounded-3xl'):
                    ia_msg = ui.markdown('Initialisation de Kareem...').classes('text-slate-300 text-lg leading-relaxed')

    # INPUT FIXE EN BAS
    with ui.footer().classes('bg-transparent p-8'):
        with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-emerald-500/20 p-4 shadow-2xl rounded-2xl'):
            with ui.row().classes('w-full items-center gap-4'):
                if s_idx in [3, 9]: # Inventaire ou Jugement
                    ui.upload(label="ANALYSE PDF").props('flat color=emerald').classes('w-32 text-xs')
                
                msg_in = ui.input(placeholder='Posez votre question ou soumettez vos faits...').props('dark borderless').classes('flex-grow text-white px-4')
                
                async def run_ia():
                    val = msg_in.value; msg_in.value = ""
                    if client and val:
                        prompt = engine.get_persona_prompt(s_idx)
                        resp = await asyncio.to_thread(client.chat.completions.create, model="llama-3.3-70b-versatile",
                                                       messages=[{"role": "system", "content": prompt}, {"role": "user", "content": val}])
                        await typewriter(ia_msg, resp.choices[0].message.content)
                
                ui.button(icon='send', on_click=run_ia).props('round color=emerald').classes('shadow-lg shadow-emerald-900/40')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='FREEMAN_KEY_2026', dark=True, reload=False, title="LegalOS v2")
