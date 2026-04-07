import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# Configuration API
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

# --- SYSTÈME DE MÉMOIRE (Pour que Kareem "retienne") ---
def get_conversation_history(d_id):
    # Logique pour récupérer les échanges précédents et garder le fil
    return app.storage.user.get(f'history_{d_id}', [])

# --- INTERFACE ---
@ui.page('/')
def login_page():
    ui.query('body').style('background: #020617; color: white;')
    with ui.column().classes('absolute-center items-center w-full max-w-sm p-8 bg-slate-900 rounded-2xl border border-emerald-500/30'):
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 mb-2')
        ui.label('MÉTHODE FREEMAN').classes('text-xs tracking-[.3em] text-slate-400 mb-8')
        
        # Champs explicites : Email et Mot de Passe
        email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
        password = ui.input('Mot de passe', password=True).props('dark outlined color=emerald').classes('w-full mb-6')
        
        def attempt_login():
            if email.value and password.value:
                app.storage.user.update({'auth': True, 'email': email.value})
                ui.navigate.to('/workspace')
            else:
                ui.notify('Identifiants requis', color='red')

        ui.button('CONNEXION / INSCRIPTION', on_click=attempt_login).classes('w-full bg-emerald-600 py-4 font-bold')

@ui.page('/workspace')
async def workspace():
    if not app.storage.user.get('auth'): return ui.navigate.to('/')
    
    # State management
    if 'step' not in app.storage.user: app.storage.user['step'] = 0
    current_step = app.storage.user['step']
    steps = ["Qualification", "Objectif", "Base Légale", "Inventaire", "Risques", "Amiable", "Attaque", "Rédaction", "Audience", "Jugement", "Recours"]

    ui.query('body').style('background: #020617;')

    # Sidebar Pro
    with ui.left_drawer().classes('bg-slate-950 border-r border-slate-800 p-4'):
        ui.label('ÉTAPES').classes('text-slate-500 text-xs font-bold mb-4 tracking-widest')
        for i, name in enumerate(steps):
            active = (i == current_step)
            with ui.row().classes(f'w-full p-3 rounded-lg mb-1 cursor-pointer {"bg-emerald-500/10 border border-emerald-500/20" if active else "hover:bg-slate-900"}') as r:
                ui.label(f'{i+1}. {name}').classes(f'text-sm {"text-emerald-400 font-bold" if active else "text-slate-400"}')
                r.on('click', lambda i=i: (app.storage.user.update({'step': i}), ui.navigate.to('/workspace')))

    # Main Area
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 h-screen'):
        ui.label(steps[current_step]).classes('text-4xl font-black text-white mb-8 uppercase tracking-tighter')
        
        # Zone de messages (Scrollable)
        message_container = ui.column().classes('w-full flex-grow overflow-y-auto mb-32 pb-8 gap-4')

        # Footer fixe avec Upload et Input (L'expérience "tout-en-un")
        with ui.footer().classes('bg-transparent p-6'):
            with ui.card().classes('w-full max-w-4xl mx-auto bg-slate-900 border border-slate-700 p-2 shadow-2xl rounded-2xl'):
                with ui.row().classes('w-full items-center no-wrap'):
                    # Upload universel (prend tout)
                    ui.upload(on_upload=lambda e: ui.notify(f'Document {e.name} ajouté'), label="DOCS").props('flat color=emerald').classes('w-20')
                    
                    user_input = ui.input(placeholder='Décrivez la situation ou posez une question...').props('dark borderless').classes('flex-grow text-white px-4')
                    
                    async def process_msg():
                        val = user_input.value
                        if not val: return
                        user_input.value = ""
                        
                        # Affichage utilisateur
                        with message_container:
                            ui.label(f"VOUS : {val}").classes('self-end bg-slate-800 p-4 rounded-xl text-slate-200 border border-slate-700 max-w-[80%]')
                        
                        # Appel IA avec Instruction Invisible
                        system_instr = f"Tu es Kareem. Étape actuelle : {steps[current_step]}. Sois bref, incisif, ne t'excuse pas. Analyse et pose LA question qui fait avancer le dossier juridiquement."
                        
                        response = await asyncio.to_thread(client.chat.completions.create, 
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": system_instr}, {"role": "user", "content": val}]
                        )
                        
                        # Affichage Kareem (Sans texte vert système)
                        with message_container:
                            card = ui.card().classes('w-full bg-emerald-950/20 border border-emerald-500/20 p-4 rounded-xl')
                            with card:
                                ui.markdown(response.choices[0].message.content).classes('text-emerald-100')
                        
                        message_container.scroll_to(percent=1)

                    ui.button(icon='send', on_click=process_msg).props('round flat color=emerald').classes('p-4')

ui.run(storage_secret='FREEMAN_2026', title='Legal OS')
