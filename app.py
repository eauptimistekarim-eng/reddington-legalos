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

# --- 2. BASE DE DONNÉES ÉVOLUÉE ---
def init_db():
    conn = sqlite3.connect('legalos_v2.db', check_same_thread=False)
    c = conn.cursor()
    # Table Dossiers
    c.execute('''CREATE TABLE IF NOT EXISTS dossiers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, nom TEXT, 
                  date_crea TEXT, statut TEXT DEFAULT 'actif')''')
    # Table Étapes liée au dossier
    c.execute('''CREATE TABLE IF NOT EXISTS steps_v2 
                 (dossier_id INTEGER, step_idx INTEGER, contenu TEXT, 
                  PRIMARY KEY(dossier_id, step_idx))''')
    conn.commit()
    conn.close()

init_db()

# --- 3. LOGIQUE MÉTIER & PROMPTS ---
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
            "Sois l'avocat du diable et Machiavel. Anticipe les coups bas et prépare la riposte (plaintes, requêtes).",
            "Génère des modèles de documents juridiques modifiables basés sur l'analyse.",
            "Incarne le Juge. Simule un débat contradictoire (ping-pong) avec l'utilisateur.",
            "Analyse le jugement rendu (PDF) et critique les points de droit.",
            "Fais le point final et propose les voies de recours stratégiques."
        ]
        return f"{prompts[step_idx]} Parle de manière fluide, comme un humain. Pose des questions pertinentes une par une."

# --- 4. COMPOSANTS UI RÉUTILISABLES ---
async def typewriter_effect(label, text, speed=0.02):
    """Simule l'écriture d'une machine à écrire"""
    full_text = ""
    for char in text:
        full_text += char
        label.set_content(full_text)
        await asyncio.sleep(speed)

# --- 5. PAGES ---

@ui.page('/login')
def login():
    with ui.card().classes('absolute-center p-8 w-96 bg-slate-900 border border-emerald-500/20 shadow-2xl'):
        ui.label('LEGAL OS').classes('text-3xl font-black text-emerald-500 text-center w-full')
        ui.label('SYSTÈME FREEMAN').classes('text-[10px] text-center w-full mb-6 tracking-widest text-emerald-400/50')
        email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
        
        def do_login():
            app.storage.user['email'] = email.value
            app.storage.user['auth'] = True
            ui.navigate.to('/dossiers')
            
        ui.button('ACCÉDER (Essai Gratuit)', on_click=do_login).classes('w-full bg-emerald-600 font-bold')

@ui.page('/dossiers')
def list_dossiers():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    user_email = app.storage.user['email']

    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-4 justify-between'):
        ui.label('MES DOSSIERS').classes('text-xl font-bold text-emerald-500')
        ui.button(icon='logout', on_click=lambda: ui.navigate.to('/login')).props('flat color=slate-500')

    with ui.column().classes('w-full p-8 max-w-4xl mx-auto'):
        # Création de dossier
        with ui.row().classes('w-full mb-8 gap-4'):
            nom = ui.input(placeholder='Nom du nouveau dossier...').props('dark outlined').classes('flex-grow')
            def create():
                conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
                c.execute("INSERT INTO dossiers (user_email, nom, date_crea) VALUES (?, ?, ?)", 
                          (user_email, nom.value, datetime.now().strftime("%d/%m/%Y")))
                conn.commit(); conn.close()
                ui.navigate.to('/dossiers')
            ui.button('NOUVEAU DOSSIER', on_click=create, icon='add').classes('bg-emerald-600 font-bold')

        # Liste des dossiers
        conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
        c.execute("SELECT id, nom, date_crea, statut FROM dossiers WHERE user_email=? AND statut='actif' ORDER BY id DESC", (user_email,))
        rows = c.fetchall(); conn.close()

        for d_id, d_nom, d_date, d_statut in rows:
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 mb-2 hover:border-emerald-500/40 transition-all'):
                with ui.row().classes('w-full items-center p-2'):
                    ui.icon('folder', color='emerald').classes('text-2xl')
                    with ui.column().classes('flex-grow'):
                        ui.label(d_nom).classes('font-bold text-lg')
                        ui.label(f"Créé le {d_date}").classes('text-xs text-slate-500')
                    
                    with ui.row():
                        ui.button(icon='play_arrow', on_click=lambda d=d_id: ui.navigate.to(f'/workspace/{d}')).props('flat color=emerald')
                        ui.button(icon='archive', on_click=lambda d=d_id: archive_dossier(d)).props('flat color=orange')
                        ui.button(icon='delete', on_click=lambda d=d_id: delete_dossier(d)).props('flat color=red')

def archive_dossier(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
    c.execute("UPDATE dossiers SET statut='archive' WHERE id=?", (id,))
    conn.commit(); conn.close(); ui.navigate.to('/dossiers')

def delete_dossier(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
    c.execute("DELETE FROM dossiers WHERE id=?", (id,))
    conn.commit(); conn.close(); ui.navigate.to('/dossiers')

@ui.page('/workspace/{d_id}')
async def workspace(d_id: int):
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    
    expert = LegalExpert()
    state = app.storage.user.get('ws_state', {'step': 0})
    
    # Header du dossier
    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dossiers')).props('flat color=slate-400')
        ui.label(f'CABINET : {d_id}').classes('text-emerald-500 font-black')
        ui.button('Envoyer par Mail', icon='email').props('outline color=emerald')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Stepper Latéral
        with ui.column().classes('w-64 bg-slate-950 border-r border-slate-900 p-4'):
            for i, name in enumerate(expert.steps):
                active = i == state['step']
                with ui.row().classes(f'w-full p-3 rounded-lg cursor-pointer {"bg-emerald-500/10" if active else ""}') as r:
                    ui.label(f"{i+1}. {name}").classes(f'text-xs {"text-emerald-400 font-bold" if active else "text-slate-500"}')
                    r.on('click', lambda i=i: (state.update({'step': i}), ui.navigate.to(f'/workspace/{d_id}')))

        # Zone Conversationnelle
        with ui.column().classes('flex-grow p-8 bg-slate-950 overflow-y-auto pb-32'):
            ui.label(expert.steps[state['step']]).classes('text-4xl font-black mb-8 text-white')
            
            # Zone d'affichage des messages
            message_container = ui.column().classes('w-full gap-4')
            
            # Affichage de l'historique ou du début
            with message_container:
                response_label = ui.markdown().classes('text-slate-300 text-lg leading-relaxed')

            # Zone de saisie flottante
            with ui.footer().classes('bg-transparent p-6'):
                with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-slate-800 p-4 shadow-2xl'):
                    with ui.row().classes('w-full items-center gap-4'):
                        # Option Upload pour "Inventaire" ou "Jugement"
                        if state['step'] in [3, 9]:
                            ui.upload(on_upload=lambda e: ui.notify(f'Analyse de {e.name}...'), 
                                      label="Joindre PDF").props('flat color=emerald').classes('w-32')
                        
                        user_input = ui.input(placeholder='Parlez à Kareem...').props('dark borderless').classes('flex-grow text-white')
                        
                        async def send():
                            txt = user_input.value
                            user_input.value = ""
                            # Logic IA avec prompt système spécifique à l'étape
                            if client:
                                prompt_sys = expert.get_system_prompt(state['step'])
                                response = await asyncio.to_thread(
                                    client.chat.completions.create,
                                    model="llama-3.3-70b-versatile",
                                    messages=[
                                        {"role": "system", "content": prompt_sys},
                                        {"role": "user", "content": txt}
                                    ]
                                )
                                answer = response.choices[0].message.content
                                await typewriter_effect(response_label, answer)
                            else:
                                ui.notify("Clé API manquante", color='red')

                        ui.button(icon='send', on_click=send).props('round color=emerald')

# --- 6. LANCEMENT ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='FREEMAN_PRO_2026', dark=True, reload=False)
