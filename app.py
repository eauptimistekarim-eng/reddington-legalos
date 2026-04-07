import os
import sqlite3
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- CONFIG ---
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

def init_db():
    conn = sqlite3.connect('legalos_v3.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, nom TEXT, date_crea TEXT, statut TEXT DEFAULT "actif")')
    conn.commit()
    conn.close()

init_db()

# --- LOGIQUE KAREEM ---
STEPS = ["Qualification", "Objectif", "Base Légale", "Inventaire", "Risques", "Amiable", "Attaque", "Rédaction", "Audience", "Jugement", "Recours"]

def get_system_prompt(step_idx):
    prompts = [
        "Tu es Kareem. Étape 1: Qualification. Pose des questions précises pour transformer le récit en faits juridiques. Une question à la fois.",
        "Étape 2: Objectif. Questionne l'utilisateur sur ses priorités réelles (argent, temps, principes).",
        "Étape 3: Base Légale. TU DOIS citer des articles de loi et des jurisprudences réelles et vérifiables (Légifrance).",
        "Étape 4: Inventaire. Analyse les documents fournis. Explique leur valeur juridique ajoutée.",
        "Étape 5: Risques. Détermine le % de réussite et propose des solutions de protection (administratives/légales).",
        "Étape 6: Amiable. Explique la mise en demeure et propose un mail de diplomatie stratégique.",
        "Étape 7: Attaque. Mode Machiavel. Anticipe les coups de l'adversaire. Propose des requêtes, plaintes ou ordonnances.",
        "Étape 8: Rédaction. Propose de générer des modèles de documents modifiables basés sur les données du dossier.",
        "Étape 9: Audience. Tu es le JUGE. Lance un débat contradictoire (ping-pong) pour tester les arguments.",
        "Étape 10: Jugement. Analyse le résultat (ou le PDF) et détermine les failles pour le recours.",
        "Étape 11: Recours. Fais le point final et propose les solutions (Appel, etc.)."
    ]
    return f"{prompts[step_idx]} Parle comme un humain, sois percutant et utilise l'art du questionnement."

# --- UI HELPERS ---
async def typewriter(container, text):
    msg_card = ui.card().classes('w-full bg-slate-800/50 p-4 rounded-xl mb-2')
    with msg_card:
        label = ui.markdown().classes('text-slate-200')
    content = ""
    for char in text:
        content += char
        label.set_content(content)
        await asyncio.sleep(0.01)

# --- PAGES ---

@ui.page('/')
def login():
    if app.storage.user.get('auth'): return ui.navigate.to('/dossiers')
    ui.query('body').style('background-color: #020617;')
    
    with ui.column().classes('absolute-center items-center w-full'):
        ui.label('LEGAL OS').classes('text-6xl font-black text-emerald-500 mb-2')
        ui.label('SYSTÈME FREEMAN').classes('text-xs tracking-[0.4em] text-slate-500 mb-12')
        
        with ui.card().classes('p-8 w-96 bg-slate-900 border border-emerald-500/20 shadow-2xl rounded-2xl'):
            ui.label('Connexion / Essai Gratuit').classes('text-xl text-white mb-6 font-bold')
            email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
            pwd = ui.input('Mot de passe', password=True).props('dark outlined color=emerald').classes('w-full mb-6')
            
            def do_login():
                if not email.value or not pwd.value:
                    return ui.notify('Veuillez remplir tous les champs', color='red')
                app.storage.user.update({'auth': True, 'email': email.value})
                ui.navigate.to('/dossiers')
                
            ui.button('COMMENCER L\'ESSAI GRATUIT', on_click=do_login).classes('w-full bg-emerald-600 font-bold py-4 rounded-lg')

@ui.page('/dossiers')
def list_dossiers():
    if not app.storage.user.get('auth'): return ui.navigate.to('/')
    ui.query('body').style('background-color: #020617;')
    
    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-6 justify-between items-center'):
        ui.label('DOSSIERS EN COURS').classes('text-xl font-bold text-emerald-500')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))).props('flat color=slate-500')

    with ui.column().classes('w-full p-8 max-w-5xl mx-auto'):
        with ui.row().classes('w-full mb-12 gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800 items-center'):
            nom = ui.input(placeholder='Nom du nouveau dossier...').props('dark borderless').classes('flex-grow text-xl px-4')
            def create():
                if not nom.value: return
                conn = sqlite3.connect('legalos_v3.db'); c = conn.cursor()
                c.execute("INSERT INTO dossiers (user_email, nom, date_crea) VALUES (?, ?, ?)", (app.storage.user['email'], nom.value, datetime.now().strftime("%d/%m/%Y")))
                conn.commit(); conn.close(); ui.navigate.to('/dossiers')
            ui.button('OUVRIR', on_click=create).classes('bg-emerald-600 font-bold px-8 py-2 rounded-lg')

        conn = sqlite3.connect('legalos_v3.db'); c = conn.cursor()
        c.execute("SELECT id, nom, date_crea FROM dossiers WHERE user_email=? ORDER BY id DESC", (app.storage.user['email'],))
        for d_id, d_nom, d_date in c.fetchall():
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 mb-3 hover:border-emerald-500/40 transition-all'):
                with ui.row().classes('w-full items-center p-3'):
                    with ui.column().classes('flex-grow cursor-pointer').on('click', lambda d=d_id: ui.navigate.to(f'/workspace/{d}')):
                        ui.label(d_nom).classes('text-xl font-bold text-slate-100')
                        ui.label(f"Créé le {d_date}").classes('text-xs text-slate-500 uppercase')
                    with ui.row().classes('gap-2'):
                        ui.button(icon='email', on_click=lambda: ui.notify('Dossier envoyé')).props('flat color=slate-400')
                        ui.button(icon='delete', on_click=lambda d=d_id: (sqlite3.connect('legalos_v3.db').cursor().execute("DELETE FROM dossiers WHERE id=?", (d,)).connection.commit(), ui.navigate.to('/dossiers'))).props('flat color=red-400')
        conn.close()

@ui.page('/workspace/{d_id}')
async def workspace(d_id: int):
    if not app.storage.user.get('auth'): return ui.navigate.to('/')
    if 'step' not in app.storage.user: app.storage.user['step'] = 0
    s_idx = app.storage.user['step']
    ui.query('body').style('background-color: #020617;')

    with ui.header().classes('bg-slate-950/90 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dossiers')).props('flat color=slate-400')
        ui.label(f"CABINET KAREEM - DOSSIER #{d_id}").classes('text-emerald-500 font-black')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Sidebar
        with ui.column().classes('w-64 bg-slate-950 border-r border-slate-900 p-4 h-full'):
            for i, name in enumerate(STEPS):
                active = (i == s_idx)
                with ui.row().classes(f'w-full p-3 rounded-xl cursor-pointer mb-1 {"bg-emerald-500/10 border border-emerald-500/20" if active else "hover:bg-slate-900"}') as r:
                    ui.label(name).classes(f'text-xs uppercase font-bold {"text-emerald-400" if active else "text-slate-500"}')
                    r.on('click', lambda i=i: (app.storage.user.update({'step': i}), ui.navigate.to(f'/workspace/{d_id}')))

        # Main Chat
        with ui.column().classes('flex-grow p-12 overflow-y-auto pb-64 items-center'):
            ui.label(STEPS[s_idx]).classes('text-5xl font-black text-white mb-12 tracking-tighter w-full max-w-4xl')
            chat_box = ui.column().classes('w-full max-w-4xl gap-4')

    # Footer
    with ui.footer().classes('bg-transparent p-8'):
        with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-emerald-500/20 p-4 shadow-2xl rounded-2xl'):
            with ui.row().classes('w-full items-center gap-4'):
                # Upload universel
                ui.upload(on_upload=lambda e: ui.notify(f'Fichier {e.name} reçu'), multiple=True, label="DOCS").props('flat color=emerald').classes('w-24')
                
                input_field = ui.input(placeholder='Parlez à Kareem...').props('dark borderless').classes('flex-grow text-white px-4')
                
                async def send_to_ia():
                    msg = input_field.value
                    if not msg or not client: return
                    input_field.value = ""
                    
                    # Bulle Utilisateur
                    with chat_box:
                        ui.label(f"VOUS : {msg}").classes('self-end bg-emerald-900/20 text-emerald-400 p-4 rounded-2xl mb-4 border border-emerald-500/10')
                    
                    # Réponse Kareem
                    prompt = get_system_prompt(s_idx)
                    response = await asyncio.to_thread(client.chat.completions.create, model="llama-3.3-70b-versatile",
                                                       messages=[{"role": "system", "content": prompt}, {"role": "user", "content": msg}])
                    await typewriter(chat_box, response.choices[0].message.content)

                ui.button(icon='send', on_click=send_to_ia).props('round color=emerald')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='FREEMAN_FINAL_2026', dark=True, reload=False)
