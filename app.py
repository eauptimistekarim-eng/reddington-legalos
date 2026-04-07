import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

# --- DATABASE ---
def init_db():
    with sqlite3.connect('legalos_v3.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS dossiers (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, nom TEXT, date_crea TEXT)')

init_db()

# --- LOGIQUE KAREEM ---
STEPS = ["Qualification", "Objectif", "Base Légale", "Inventaire", "Risques", "Amiable", "Attaque", "Rédaction", "Audience", "Jugement", "Recours"]

# --- PAGES ---

@ui.page('/')
def login():
    ui.query('body').style('background-color: #020617;')
    with ui.column().classes('absolute-center items-center w-full'):
        ui.label('LEGAL OS').classes('text-6xl font-black text-emerald-500 mb-2')
        ui.label('MÉTHODE FREEMAN PAR KAREEM').classes('text-xs tracking-[0.4em] text-slate-500 mb-12')
        
        with ui.card().classes('p-8 w-96 bg-slate-900 border border-emerald-500/20 shadow-2xl rounded-2xl'):
            ui.label('Connexion').classes('text-xl text-white mb-6 font-bold')
            email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
            pwd = ui.input('Mot de passe', password=True).props('dark outlined color=emerald').classes('w-full mb-6')
            
            def do_login():
                if email.value and pwd.value:
                    app.storage.user.update({'auth': True, 'email': email.value})
                    ui.navigate.to('/workspace')
            
            ui.button('COMMENCER L\'ESSAI GRATUIT', on_click=do_login).classes('w-full bg-emerald-600 font-bold py-4 rounded-lg')

@ui.page('/workspace')
async def workspace():
    if not app.storage.user.get('auth'): return ui.navigate.to('/')
    if 'step' not in app.storage.user: app.storage.user['step'] = 0
    s_idx = app.storage.user['step']
    
    ui.query('body').style('background-color: #020617;')

    # 1. SIDEBAR (Drawer)
    with ui.left_drawer().classes('bg-slate-950 border-r border-slate-900 p-4'):
        for i, name in enumerate(STEPS):
            active = (i == s_idx)
            with ui.row().classes(f'w-full p-3 rounded-xl cursor-pointer mb-1 {"bg-emerald-500/10 border border-emerald-500/20" if active else "hover:bg-slate-900"}') as r:
                ui.label(f"{i+1}. {name}").classes(f'text-xs uppercase font-bold {"text-emerald-400" if active else "text-slate-500"}')
                r.on('click', lambda i=i: (app.storage.user.update({'step': i}), ui.navigate.to('/workspace')))

    # 2. ZONE DE CHAT (Main)
    # On définit le container de messages ici
    with ui.column().classes('w-full max-w-4xl mx-auto p-12 pb-40'):
        ui.label(STEPS[s_idx]).classes('text-5xl font-black text-white mb-8')
        message_container = ui.column().classes('w-full gap-4')

    # 3. FOOTER (Hors de toute Column/Row - Correction de l'erreur Runtime)
    with ui.footer().classes('bg-transparent p-6 border-none'):
        with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-emerald-500/20 p-4 shadow-2xl rounded-2xl'):
            with ui.row().classes('w-full items-center gap-4 no-wrap'):
                # Upload universel
                ui.upload(on_upload=lambda e: ui.notify(f'Fichier {e.name} reçu'), multiple=True, label="DOCS").props('flat color=emerald small').classes('w-24')
                
                user_input = ui.input(placeholder='Parlez à Kareem...').props('dark borderless').classes('flex-grow text-white px-4')
                
                async def send():
                    msg = user_input.value
                    if not msg or not client: return
                    user_input.value = ""
                    
                    with message_container:
                        ui.label(f"VOUS : {msg}").classes('self-end bg-emerald-900/10 text-emerald-400 p-4 rounded-xl border border-emerald-500/10')
                        
                        # Appel IA (Instructions invisibles)
                        system_instr = f"Tu es Kareem. Étape : {STEPS[s_idx]}. Sois un expert juridique incisif. Pas de phrases inutiles."
                        response = await asyncio.to_thread(client.chat.completions.create, 
                                                           model="llama-3.3-70b-versatile",
                                                           messages=[{"role": "system", "content": system_instr}, {"role": "user", "content": msg}])
                        
                        # Réponse Kareem
                        with ui.card().classes('w-full bg-slate-800/50 p-4 border-none shadow-none'):
                            ui.markdown(response.choices[0].message.content).classes('text-slate-200')
                    
                    # Scroll auto
                    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

                ui.button(icon='send', on_click=send).props('round flat color=emerald')

ui.run(storage_secret='FREEMAN_FINAL', dark=True)
