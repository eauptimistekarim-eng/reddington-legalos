import os
import sqlite3
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- CONFIGURATION & ENV ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

# --- BASE DE DONNÉES (Mémoire des projets Reddington / Petit Sentier) ---
def init_db():
    with sqlite3.connect('legalos_core.db') as conn:
        # Table des dossiers pour ne rien oublier
        conn.execute('''CREATE TABLE IF NOT EXISTS dossiers 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         user_email TEXT, 
                         nom TEXT, 
                         type TEXT, 
                         date_crea TEXT)''')
        # Table de l'historique des conversations par dossier
        conn.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         dossier_id INTEGER, 
                         role TEXT, 
                         content TEXT)''')

init_db()

# --- CONSTANTES MÉTHODE ---
STEPS = [
    "Qualification", "Objectif", "Base Légale", "Inventaire", 
    "Risques", "Amiable", "Attaque", "Rédaction", 
    "Audience", "Jugement", "Recours"
]

# --- LOGIQUE KAREEM ---
async def call_kareem(message, step_name, history):
    if not client:
        return "Erreur : Clé API Groq manquante."
    
    # Instruction système invisible pour l'utilisateur
    system_prompt = (
        f"Tu es Kareem, l'IA de Legal OS. Tu appliques la Méthode Freeman. "
        f"Étape actuelle : {step_name}. "
        "Ton style : Froid, chirurgical, expert, sans empathie inutile. "
        "Ne t'excuse jamais. Ne dis pas 'Je comprends'. Analyse les faits et "
        "pose LA question qui fait basculer le dossier juridiquement."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    # Ajout de l'historique pour la "mémoire"
    for h in history[-5:]: # On garde les 5 derniers échanges pour le contexte
        messages.append({"role": h[0], "content": h[1]})
    messages.append({"role": "user", "content": message})

    completion = await asyncio.to_thread(
        client.chat.completions.create,
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.2
    )
    return completion.choices[0].message.content

# --- INTERFACE UTILISATEUR (UX) ---

@ui.page('/')
def login_page():
    ui.query('body').style('background-color: #020617;')
    if app.storage.user.get('auth'): ui.navigate.to('/dashboard')

    with ui.column().classes('absolute-center items-center w-full'):
        ui.label('LEGAL OS').classes('text-7xl font-black text-emerald-500 mb-2 tracking-tighter')
        ui.label('SYSTÈME FREEMAN').classes('text-xs tracking-[0.5em] text-slate-500 mb-12')
        
        with ui.card().classes('p-10 w-full max-w-md bg-slate-900 border border-emerald-500/20 shadow-2xl rounded-3xl'):
            ui.label('Accès Système').classes('text-2xl text-white mb-8 font-bold text-center')
            email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
            pwd = ui.input('Mot de passe', password=True).props('dark outlined color=emerald').classes('w-full mb-8')
            
            def handle_login():
                if email.value and pwd.value:
                    app.storage.user.update({'auth': True, 'email': email.value})
                    ui.navigate.to('/dashboard')
            
            ui.button('COMMENCER L\'ESSAI GRATUIT', on_click=handle_login).classes('w-full bg-emerald-600 hover:bg-emerald-500 py-4 font-bold rounded-xl transition-all')

@ui.page('/dashboard')
def dashboard():
    if not app.storage.user.get('auth'): ui.navigate.to('/')
    ui.query('body').style('background-color: #020617;')

    with ui.column().classes('w-full max-w-6xl mx-auto p-12 text-white'):
        with ui.row().classes('w-full justify-between items-end mb-12'):
            ui.label('MES DOSSIERS').classes('text-4xl font-black text-emerald-500')
            ui.button('NOUVEAU DOSSIER', icon='add', on_click=lambda: new_dialog.open()).classes('bg-emerald-600')

        # Liste des dossiers (Reddington, Petit Sentier, etc.)
        with ui.grid(columns=3).classes('w-full gap-6'):
            conn = sqlite3.connect('legalos_core.db')
            cursor = conn.execute("SELECT id, nom, date_crea FROM dossiers WHERE user_email=?", (app.storage.user['email'],))
            for d_id, d_nom, d_date in cursor.fetchall():
                with ui.card().classes('bg-slate-900 border border-slate-800 p-6 hover:border-emerald-500/50 cursor-pointer transition-all').on('click', lambda d_id=d_id: ui.navigate.to(f'/workspace/{d_id}')):
                    ui.label(d_nom).classes('text-xl font-bold text-white mb-2')
                    ui.label(f"Créé le {d_date}").classes('text-xs text-slate-500')
            conn.close()

    # Dialogue Nouveau Dossier
    with ui.dialog() as new_dialog, ui.card().classes('bg-slate-900 p-8 border border-emerald-500/20'):
        ui.label('Nommer le projet').classes('text-xl text-white mb-4')
        nom_dossier = ui.input(placeholder='ex: Reddington').props('dark outlined color=emerald').classes('w-full mb-6')
        def create():
            if not nom_dossier.value: return
            with sqlite3.connect('legalos_core.db') as conn:
                conn.execute("INSERT INTO dossiers (user_email, nom, date_crea) VALUES (?, ?, ?)", 
                             (app.storage.user['email'], nom_dossier.value, datetime.now().strftime("%d/%m/%Y")))
            new_dialog.close()
            ui.navigate.to('/dashboard')
        ui.button('CRÉER', on_click=create).classes('w-full bg-emerald-600')

@ui.page('/workspace/{d_id}')
async def workspace(d_id: int):
    if not app.storage.user.get('auth'): ui.navigate.to('/')
    ui.query('body').style('background-color: #020617;')
    
    # State management
    if f'step_{d_id}' not in app.storage.user: app.storage.user[f'step_{d_id}'] = 0
    s_idx = app.storage.user[f'step_{d_id}']

    with ui.header().classes('bg-slate-950/80 backdrop-blur-md border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')).props('flat color=slate-400')
        ui.label(f'CABINET KAREEM | DOSSIER #{d_id}').classes('font-black text-emerald-500')
        ui.label(app.storage.user['email']).classes('text-xs text-slate-600')

    with ui.left_drawer().classes('bg-slate-950 border-r border-slate-900 p-4'):
        for i, name in enumerate(STEPS):
            active = (i == s_idx)
            with ui.row().classes(f'w-full p-4 rounded-xl cursor-pointer mb-1 {"bg-emerald-500/10 border border-emerald-500/30" if active else "hover:bg-slate-900"}') as r:
                ui.label(f"{i+1}").classes(f'mr-3 font-black {"text-emerald-500" if active else "text-slate-800"}')
                ui.label(name).classes(f'text-xs uppercase font-bold {"text-emerald-400" if active else "text-slate-500"}')
                r.on('click', lambda i=i: (app.storage.user.update({f'step_{d_id}': i}), ui.navigate.to(f'/workspace/{d_id}')))

    # CHAT AREA
    chat_container = ui.column().classes('w-full max-w-4xl mx-auto p-12 pb-48')
    with chat_container:
        ui.label(STEPS[s_idx]).classes('text-5xl font-black text-white mb-12 tracking-tighter')
        
        # Chargement historique
        conn = sqlite3.connect('legalos_core.db')
        hist = conn.execute("SELECT role, content FROM chat_history WHERE dossier_id=? ORDER BY id", (d_id,)).fetchall()
        for role, content in hist:
            is_user = (role == 'user')
            with ui.column().classes(f'w-full {"items-end" if is_user else "items-start"} mb-4'):
                bg = 'bg-emerald-900/20' if is_user else 'bg-slate-900'
                border = 'border-emerald-500/20' if is_user else 'border-slate-800'
                color = 'text-emerald-400' if is_user else 'text-slate-200'
                with ui.card().classes(f'{bg} {border} border p-4 rounded-2xl max-w-[80%] shadow-none'):
                    ui.markdown(content).classes(f'text-sm {color}')
        conn.close()

    # FOOTER INPUT (Correction structurelle)
    with ui.footer().classes('bg-transparent p-8'):
        with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-emerald-500/20 p-4 rounded-2xl shadow-2xl'):
            with ui.row().classes('w-full items-center no-wrap gap-4'):
                ui.upload(on_upload=lambda e: ui.notify(f'Doc: {e.name}'), multiple=True).props('flat color=emerald').classes('w-20')
                msg_input = ui.input(placeholder='Parlez à Kareem...').props('dark borderless').classes('flex-grow text-white px-4')
                
                async def send():
                    val = msg_input.value
                    if not val: return
                    msg_input.value = ""
                    
                    # 1. Sauvegarde & Affichage User
                    with chat_container:
                        with ui.column().classes('w-full items-end mb-4'):
                            with ui.card().classes('bg-emerald-900/20 border border-emerald-500/20 p-4 rounded-2xl'):
                                ui.markdown(val).classes('text-sm text-emerald-400')
                    
                    with sqlite3.connect('legalos_core.db') as conn:
                        conn.execute("INSERT INTO chat_history (dossier_id, role, content) VALUES (?, ?, ?)", (d_id, 'user', val))
                        history = conn.execute("SELECT role, content FROM chat_history WHERE dossier_id=?", (d_id,)).fetchall()

                    # 2. Appel Kareem
                    response = await call_kareem(val, STEPS[s_idx], history)
                    
                    # 3. Sauvegarde & Affichage Kareem
                    with chat_container:
                        with ui.column().classes('w-full items-start mb-4'):
                            with ui.card().classes('bg-slate-900 border border-slate-800 p-4 rounded-2xl'):
                                ui.markdown(response).classes('text-sm text-slate-200')
                    
                    with sqlite3.connect('legalos_core.db') as conn:
                        conn.execute("INSERT INTO chat_history (dossier_id, role, content) VALUES (?, ?, ?)", (d_id, 'assistant', response))
                    
                    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

                ui.button(icon='send', on_click=send).props('round color=emerald')

ui.run(storage_secret='KAREEM_SECRET_2026', dark=True, title='Legal OS - Freeman')
