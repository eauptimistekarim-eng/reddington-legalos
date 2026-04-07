import os
import sqlite3
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- 1. CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

# --- 2. BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('legalos_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, trial_active INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS dossiers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, nom TEXT, 
                  date_crea TEXT, statut TEXT DEFAULT 'actif')''')
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (dossier_id INTEGER, step_idx INTEGER, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. MOTEUR KAREEM (LOGIQUE FREEMAN SPÉCIFIQUE) ---
class KareemEngine:
    def __init__(self):
        self.steps = [
            "Qualification", "Objectif", "Base Légale", "Inventaire", 
            "Risques", "Amiable", "Attaque", "Rédaction", 
            "Audience", "Jugement", "Recours"
        ]

    def get_step_instructions(self, step_idx):
        instructions = [
            "Étape 1 (Qualification): Pose des questions pertinentes une par une. Transforme le récit de l'utilisateur en faits juridiques précis.",
            "Étape 2 (Objectif): Utilise l'art du questionnement pour définir le but ultime (Gain financier, justice symbolique, rapidité ?).",
            "Étape 3 (Base Légale): Tu DOIS fournir des articles de loi officiels et des jurisprudences vérifiables (Légifrance). Sois précis.",
            "Étape 4 (Inventaire): Analyse le document fourni par l'utilisateur. Explique sa valeur juridique et comment il renforce le dossier.",
            "Étape 5 (Risques): Détermine les chances de succès. Propose des solutions de protection (administratives ou légales) pour l'utilisateur.",
            "Étape 6 (Amiable): Explique la procédure de mise en demeure. Génère un mail de diplomatie stratégique pour l'adversaire.",
            "Étape 7 (Attaque): Mode Machiavel / Avocat du diable. Anticipe les attaques adverses. Propose des ordonnances, requêtes ou plaintes.",
            "Étape 8 (Rédaction): Récapitule les données et demande si l'utilisateur veut générer des modèles d'actes modifiables.",
            "Étape 9 (Audience): Deviens le JUGE. Lance un débat contradictoire (ping-pong) pour tester les arguments de l'utilisateur.",
            "Étape 10 (Jugement): Analyse le PDF du jugement fourni. Identifie les failles pour préparer la suite.",
            "Étape 11 (Recours): Fais le point complet. Propose les solutions de recours (Appel, etc.) les plus viables."
        ]
        return instructions[step_idx]

engine = KareemEngine()

# --- 4. UI HELPERS ---
async def typewriter_effect(container, text):
    content = ""
    msg = ui.markdown().classes('text-slate-300 text-lg')
    container.append(msg)
    for char in text:
        content += char
        msg.set_content(content)
        await asyncio.sleep(0.005)

# --- 5. PAGES ---

@ui.page('/')
def home():
    if app.storage.user.get('auth'): return ui.navigate.to('/dossiers')
    
    with ui.column().classes('absolute-center items-center w-full'):
        ui.label('LEGAL OS').classes('text-6xl font-black text-emerald-500 mb-2')
        ui.label('LA MÉTHODE FREEMAN PAR KAREEM').classes('text-xs tracking-[0.4em] text-slate-500 mb-12')
        
        with ui.card().classes('p-8 w-96 bg-slate-900 border border-emerald-500/20 shadow-2xl'):
            ui.label('Inscription / Connexion').classes('text-xl text-white mb-6 font-bold')
            email = ui.input('Email').props('dark outlined color=emerald').classes('w-full mb-4')
            
            def start_trial():
                if not email.value: return ui.notify('Email requis')
                app.storage.user.update({'auth': True, 'email': email.value})
                ui.navigate.to('/dossiers')
                
            ui.button('COMMENCER L\'ESSAI GRATUIT', on_click=start_trial).classes('w-full bg-emerald-600 font-bold py-4')
            ui.label('Paiement via Stripe désactivé pour l\'essai').classes('text-[10px] text-slate-500 mt-4 text-center w-full')

@ui.page('/dossiers')
def list_dossiers():
    if not app.storage.user.get('auth'): return ui.navigate.to('/')
    user_email = app.storage.user['email']
    ui.query('body').style('background-color: #020617;')

    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-6 justify-between items-center'):
        ui.label('MES DOSSIERS EN COURS').classes('text-xl font-bold text-emerald-500')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))).props('flat color=slate-500')

    with ui.column().classes('w-full p-8 max-w-5xl mx-auto'):
        # Nouveau dossier
        with ui.row().classes('w-full mb-12 gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800'):
            nom = ui.input(placeholder='Nommer le dossier juridique...').props('dark borderless').classes('flex-grow text-xl')
            def create():
                if not nom.value: return
                conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
                c.execute("INSERT INTO dossiers (user_email, nom, date_crea) VALUES (?, ?, ?)", 
                          (user_email, nom.value, datetime.now().strftime("%d/%m/%Y")))
                conn.commit(); conn.close(); ui.navigate.to('/dossiers')
            ui.button('OUVRIR LE DOSSIER', on_click=create).classes('bg-emerald-600 font-bold px-8 rounded-lg')

        # Liste
        conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor()
        c.execute("SELECT id, nom, date_crea FROM dossiers WHERE user_email=? AND statut='actif' ORDER BY id DESC", (user_email,))
        for d_id, d_nom, d_date in c.fetchall():
            with ui.card().classes('w-full bg-slate-900 border border-slate-800 mb-3 hover:border-emerald-500/40 transition-all'):
                with ui.row().classes('w-full items-center p-2'):
                    with ui.column().classes('flex-grow cursor-pointer').on('click', lambda d=d_id: ui.navigate.to(f'/workspace/{d}')):
                        ui.label(d_nom).classes('text-xl font-bold text-slate-100')
                        ui.label(f"Créé le {d_date}").classes('text-xs text-slate-500 uppercase')
                    
                    with ui.row().classes('gap-2'):
                        ui.button(icon='email', on_click=lambda: ui.notify('Dossier envoyé par mail')).props('flat color=slate-400')
                        ui.button(icon='archive', on_click=lambda d=d_id: archive_d(d)).props('flat color=orange-400')
                        ui.button(icon='delete', on_click=lambda d=d_id: delete_d(d)).props('flat color=red-400')
        conn.close()

def archive_d(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor(); c.execute("UPDATE dossiers SET statut='archive' WHERE id=?", (id,)); conn.commit(); conn.close(); ui.navigate.to('/dossiers')
def delete_d(id):
    conn = sqlite3.connect('legalos_v2.db'); c = conn.cursor(); c.execute("DELETE FROM dossiers WHERE id=?", (id,)); conn.commit(); conn.close(); ui.navigate.to('/dossiers')

@ui.page('/workspace/{d_id}')
async def workspace(d_id: int):
    if not app.storage.user.get('auth'): return ui.navigate.to('/')
    
    if 's_idx' not in app.storage.user: app.storage.user['s_idx'] = 0
    step_idx = app.storage.user['s_idx']
    
    ui.query('body').style('background-color: #020617;')

    with ui.header().classes('bg-slate-950/90 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dossiers')).props('flat color=slate-400')
        ui.label(f"ESPACE DE TRAVAIL - DOSSIER #{d_id}").classes('text-emerald-500 font-black')
        ui.button(icon='more_vert').props('flat color=slate-500')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Stepper Freeman
        with ui.column().classes('w-72 bg-slate-950 border-r border-slate-900 p-4 h-full'):
            for i, name in enumerate(engine.steps):
                active = (i == step_idx)
                with ui.row().classes(f'w-full p-3 rounded-xl cursor-pointer mb-1 {"bg-emerald-500/10 border border-emerald-500/20" if active else ""}') as r:
                    ui.label(f"{i+1}").classes(f'text-xs {"text-emerald-500 font-bold" if active else "text-slate-700"}')
                    ui.label(name).classes(f'text-xs uppercase font-bold {"text-emerald-400" if active else "text-slate-500"}')
                    r.on('click', lambda i=i: (app.storage.user.update({'s_idx': i}), ui.navigate.to(f'/workspace/{d_id}')))

        # Chat
        with ui.column().classes('flex-grow p-12 overflow-y-auto pb-64'):
            ui.label(engine.steps[step_idx]).classes('text-5xl font-black text-white mb-8 tracking-tighter')
            chat_container = ui.column().classes('w-full max-w-4xl gap-4')
            
            # Message initial automatique de Kareem pour l'étape
            with chat_container:
                ui.label(f"Kareem : {engine.get_step_instructions(step_idx)}").classes('text-emerald-500 text-xs italic mb-4')

    # Footer Input
    with ui.footer().classes('bg-transparent p-8'):
        with ui.card().classes('max-w-4xl mx-auto w-full bg-slate-900 border border-emerald-500/20 p-4 shadow-2xl rounded-2xl'):
            with ui.row().classes('w-full items-center gap-4'):
                # Upload pour Inventaire (3) et Jugement (9)
                if step_idx in [3, 9]:
                    ui.upload(label="ANALYSER DOCUMENT").props('flat color=emerald').classes('w-32')
                
                user_msg = ui.input(placeholder='Décrivez la situation ou posez une question...').props('dark borderless').classes('flex-grow text-white px-2')
                
                async def send():
                    val = user_msg.value
                    if not val: return
                    user_msg.value = ""
                    
                    # Bulle Utilisateur
                    with chat_container:
                        ui.label(f"VOUS : {val}").classes('text-slate-400 text-sm mb-2 self-end bg-slate-800 p-4 rounded-xl')
                    
                    # Réponse Kareem
                    if client:
                        instr = engine.get_step_instructions(step_idx)
                        prompt = f"Tu es Kareem. Voici ta mission pour cette étape : {instr}. Réponds à l'utilisateur : {val}"
                        res = await asyncio.to_thread(client.chat.completions.create, 
                                                       model="llama-3.3-70b-versatile",
                                                       messages=[{"role": "system", "content": prompt}])
                        await typewriter_effect(chat_container, res.choices[0].message.content)

                ui.button(icon='send', on_click=send).props('round color=emerald')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='FREEMAN_PRO_2026', dark=True, reload=False, title="LegalOS v2")
