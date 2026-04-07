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
            "Tu es Kareem. Utilise l'art du questionnement pour qualifier l'affaire.",
            "Détermine l'objectif final réel de l'utilisateur. Pose des questions sur ses priorités.",
            "Donne des articles de loi précis et des jurisprudences vérifiables (Légifrance).",
            "Analyse le document fourni. Explique sa valeur juridique ajoutée.",
            "Analyse les risques. Détermine le % de réussite et propose des solutions de protection.",
            "Expert en conciliation. Rédige une mise en demeure ou un mail diplomatique.",
            "Sois l'avocat du diable et Machiavel. Anticipe les coups bas et prépare la riposte.",
            "Génère des modèles de documents juridiques modifiables basés sur l'analyse.",
            "Incarne le Juge. Simule un débat contradictoire (ping-pong) avec l'utilisateur.",
            "Analyse le jugement rendu (PDF) et critique les points de droit.",
            "Fais le point final et propose les voies de recours stratégiques."
        ]
        return f"{prompts[step_idx]} Parle de manière fluide. Pose des questions pertinentes une par une."

expert = LegalExpert()

# --- 3. FONCTIONS UTILES ---
async def typewriter_effect(label, text, speed=0.01):
    full_text = ""
    for char in text:
        full_text += char
        label.set_content(full_text)
        await asyncio.sleep(speed)

# --- 4. PAGES & NAVIGATION ---

@ui.page('/')
def index():
    # Redirection automatique vers login ou dossiers
    if not app.storage.user.get('auth'):
        return ui.navigate.to('/login')
    ui.navigate.to('/dossiers')

@ui.page('/login')
def login():
    with ui.card().classes('absolute-center p-8 w-96 bg-slate-900 border border-emerald-500/20 shadow-2xl'):
        ui.label('LEGAL OS').classes('text-3xl font-black text-emerald-500 text-center w-full')
        email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
        def do_login():
            if not email.value: return ui.notify("Email requis")
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
                c.execute("INSERT INTO dossiers (user_email, nom, date_crea) VALUES (?, ?, ?)", 
                          (user_email, nom.value, datetime.now().strftime("%d/%m/%Y")))
                conn.commit(); conn.close()
                ui.navigate.to('/dossiers')
            ui.button('CRÉER', on_click=create, icon='add').classes('bg-emerald-600')

        conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
        c.execute("SELECT id, nom, date_crea FROM dossiers WHERE user_email=? AND statut='actif' ORDER BY id DESC", (user_email,))
        rows = c.fetchall(); conn.close()

        for d_id, d_nom, d_date in rows:
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 mb-2 hover:border-emerald-500/40 cursor-pointer'):
                with ui.row().classes('w-full items-center p-2'):
                    with ui.column().classes('flex-grow').on('click', lambda d=d_id: ui.navigate.to(f'/workspace/{d}')):
                        ui.label(d_nom).classes('font-bold text-lg text-white')
                        ui.label(f"Créé le {d_date}").classes('text-xs text-slate-500')
                    ui.button(icon='delete', on_click=lambda d=d_id: delete_dossier(d)).props('flat color=red')

def delete_dossier(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
    c.execute("DELETE FROM dossiers WHERE id=?", (id,))
    conn.commit(); conn.close(); ui.navigate.to('/dossiers')

@ui.page('/workspace/{d_id}')
async def workspace(d_id: int):
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    
    # Gestion de l'étape courante
    if 'current_step' not in app.storage.user: app.storage.user['current_step'] = 0
    step_idx = app.storage.user['current_step']

    ui.query('body').style('background-color: #020617;')

    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dossiers')).props('flat color=slate-400')
        ui.label(f'DOSSIER #{d_id}').classes('text-emerald-500 font-black')
        ui.button('MAIL', icon='email').props('flat color=emerald')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Sidebar
        with ui.column().classes('w-64 bg-slate-950 border-r border-slate-900 p-4'):
            for i, name in enumerate(expert.steps):
                is_active = (i == step_idx)
                with ui.row().classes(f'w-full p-2 rounded cursor-pointer {"bg-emerald-500/10 border-l-2 border-emerald-500" if is_active else ""}') as r:
                    ui.label(f"{i+1}. {name}").classes(f'text-[10px] uppercase {"text-emerald-400 font-bold" if is_active else "text-slate-600"}')
                    r.on('click', lambda i=i: (app.storage.user.update({'current_step': i}), ui.navigate.to(f'/workspace/{d_id}')))

        # Chat Area
        with ui.column().classes('flex-grow p-12 overflow-y-auto pb-40'):
            ui.label(expert.steps[step_idx]).classes('text-4xl font-black text-white mb-8')
            
            # Affichage réponse IA
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 p-6 rounded-xl'):
                ia_output = ui.markdown('Bonjour, je suis Kareem. Comment puis-je vous aider sur ce point ?').classes('text-slate-300 text-lg')

            # Input flottant
            with ui.footer().classes('bg-transparent p-6'):
                with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-slate-700 p-4 shadow-2xl'):
                    with ui.row().classes('w-full items-center gap-4'):
                        if step_idx in [3, 9]:
                            ui.upload(label="DOC").props('flat color=emerald').classes('w-24')
                        
                        user_msg = ui.input(placeholder='Votre message...').props('dark borderless').classes('flex-grow text-white')
                        
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
                                await typewriter_effect(ia_output, res.choices[0].message.content)
                        
                        ui.button(icon='send', on_click=talk).props('round color=emerald')

# --- 5. RUN ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='LEGAL_OS_SECURE_2026', dark=True, reload=False)
