import os
import sqlite3
import asyncio
import json
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app
from datetime import datetime

# --- 1. CONFIGURATION & IA ---
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

# --- 2. BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('legalos_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dossiers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, nom TEXT, 
                  date_crea TEXT, statut TEXT DEFAULT 'actif')''')
    c.execute('''CREATE TABLE IF NOT EXISTS steps_v2 
                 (dossier_id INTEGER, step_idx INTEGER, contenu TEXT, 
                  PRIMARY KEY(dossier_id, step_idx))''')
    conn.commit()
    conn.close()

init_db()

class LegalExpert:
    def __init__(self):
        self.steps = [
            "Qualification", "Objectif", "Base Légale", "Inventaire", 
            "Risques", "Amiable", "Attaque", "Rédaction", 
            "Audience", "Jugement", "Recours"
        ]

    def get_system_prompt(self, step_idx):
        prompts = [
            "Tu es Kareem. Utilise l'art du questionnement pour qualifier l'affaire. Pose des questions une par une pour guider l'utilisateur.",
            "Détermine l'objectif réel. Pose des questions sur les priorités (argent, justice, rapidité ?).",
            "Base Légale : Donne obligatoirement des articles de loi et des jurisprudences réelles et vérifiables.",
            "Inventaire : Analyse les documents. Explique leur force probante et leur valeur juridique.",
            "Risques : Analyse le % de réussite. Propose des mesures de protection personnelle (administratives/légales).",
            "Amiable : Expert en négo. Explique la mise en demeure et propose un mail de diplomatie stratégique.",
            "Attaque : Sois l'avocat du diable et Machiavel. Anticipe les coups de l'adversaire. Propose des requêtes et plaintes.",
            "Rédaction : Propose de générer des modèles de documents modifiables basés sur les données récoltées.",
            "Audience : Incarne le Juge. Fais un ping-pong conversationnel pour tester la solidité de l'argumentation.",
            "Jugement : Analyse le PDF du jugement (si fourni) et critique les points de droit pour le recours.",
            "Recours : Fais le bilan final et propose les solutions de sortie ou d'appel."
        ]
        return f"{prompts[step_idx]} Ton style est percutant, intelligent, et empathique. Ne fais pas de longs blocs, privilégie le dialogue."

expert = LegalExpert()

# --- 3. UI HELPERS ---
async def typewriter_effect(label, text):
    full_text = ""
    for char in text:
        full_text += char
        label.set_content(full_text)
        await asyncio.sleep(0.01)

# --- 4. PAGES ---

@ui.page('/')
def index():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    ui.navigate.to('/dossiers')

@ui.page('/login')
def login():
    with ui.card().classes('absolute-center p-8 w-96 bg-slate-900 border border-emerald-500/20 shadow-2xl'):
        ui.label('LEGAL OS').classes('text-3xl font-black text-emerald-500 text-center w-full')
        email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
        def do_login():
            if not email.value: return
            app.storage.user.update({'email': email.value, 'auth': True})
            ui.navigate.to('/dossiers')
        ui.button('ACCÉDER', on_click=do_login).classes('w-full bg-emerald-600 font-bold')

@ui.page('/dossiers')
def list_dossiers():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    user_email = app.storage.user['email']
    ui.query('body').style('background-color: #020617;')

    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.label('MES DOSSIERS').classes('text-xl font-bold text-emerald-500')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    with ui.column().classes('w-full p-8 max-w-4xl mx-auto'):
        with ui.row().classes('w-full mb-8 gap-4 items-center'):
            nom = ui.input(placeholder='Nom du dossier...').props('dark outlined').classes('flex-grow')
            def create():
                if not nom.value: return
                conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
                c.execute("INSERT INTO dossiers (user_email, nom, date_crea) VALUES (?, ?, ?)", (user_email, nom.value, datetime.now().strftime("%d/%m/%Y")))
                conn.commit(); conn.close(); ui.navigate.to('/dossiers')
            ui.button('CRÉER', on_click=create, icon='add').classes('bg-emerald-600')

        conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
        c.execute("SELECT id, nom, date_crea FROM dossiers WHERE user_email=? AND statut='actif' ORDER BY id DESC", (user_email,))
        rows = c.fetchall(); conn.close()
        for d_id, d_nom, d_date in rows:
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 mb-2'):
                with ui.row().classes('w-full items-center p-2'):
                    ui.label(d_nom).classes('font-bold text-lg text-white flex-grow cursor-pointer').on('click', lambda d=d_id: ui.navigate.to(f'/workspace/{d}'))
                    ui.button(icon='delete', on_click=lambda d=d_id: delete_d(d)).props('flat color=red')

def delete_d(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor(); c.execute("DELETE FROM dossiers WHERE id=?", (id,)); conn.commit(); conn.close(); ui.navigate.to('/dossiers')

@ui.page('/workspace/{d_id}')
async def workspace(d_id: int):
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    
    if 'current_step' not in app.storage.user: app.storage.user['current_step'] = 0
    step_idx = app.storage.user['current_step']

    ui.query('body').style('background-color: #020617;')

    # HEADER
    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dossiers')).props('flat color=slate-400')
        ui.label(f'DOSSIER #{d_id}').classes('text-emerald-500 font-black')
        ui.button(icon='email', on_click=lambda: ui.notify('Envoi du dossier par mail...')).props('flat color=emerald')

    # BARRE LATÉRALE ET ZONE CENTRALE
    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        with ui.column().classes('w-64 bg-slate-950 border-r border-slate-900 p-4'):
            for i, name in enumerate(expert.steps):
                active = (i == step_idx)
                with ui.row().classes(f'w-full p-2 rounded cursor-pointer {"bg-emerald-500/10 border-l-2 border-emerald-500" if active else ""}') as r:
                    ui.label(f"{i+1}. {name}").classes(f'text-[10px] uppercase {"text-emerald-400 font-bold" if active else "text-slate-600"}')
                    r.on('click', lambda i=i: (app.storage.user.update({'current_step': i}), ui.navigate.to(f'/workspace/{d_id}')))

        with ui.column().classes('flex-grow p-12 overflow-y-auto pb-40'):
            ui.label(expert.steps[step_idx]).classes('text-4xl font-black text-white mb-8')
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 p-6 rounded-xl mb-10'):
                ia_out = ui.markdown('Bonjour, je suis Kareem. Posez-moi vos questions pour cette étape.').classes('text-slate-300 text-lg')

    # FOOTER (CORRIGÉ : Enfant direct de la page)
    with ui.footer().classes('bg-slate-950 p-6 border-t border-slate-900'):
        with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-emerald-500/20 p-4 shadow-2xl'):
            with ui.row().classes('w-full items-center gap-4'):
                if step_idx in [3, 9]:
                    ui.upload(label="DOC").props('flat color=emerald').classes('w-24')
                
                user_msg = ui.input(placeholder='Parlez à Kareem...').props('dark borderless').classes('flex-grow text-white')
                
                async def talk():
                    if not user_msg.value: return
                    txt = user_msg.value
                    user_msg.value = ""
                    if client:
                        prompt_sys = expert.get_system_prompt(step_idx)
                        res = await asyncio.to_thread(client.chat.completions.create,
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": prompt_sys}, {"role": "user", "content": txt}]
                        )
                        await typewriter_effect(ia_out, res.choices[0].message.content)
                
                ui.button(icon='send', on_click=talk).props('round color=emerald')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='LEGAL_OS_2026', dark=True, reload=False)
