import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- 1. CONFIGURATION & SÉCURITÉ ---
load_dotenv() 
GROQ_KEY = os.getenv("GROQ_API_KEY")

# Initialisation du client Groq
# Note : S'assure que GROQ_API_KEY est bien dans ton fichier .env
client = Groq(api_key=GROQ_KEY)

# --- 2. GESTION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('legalos_v11.db')
    c = conn.cursor()
    # Table pour les 11 étapes par utilisateur et par dossier
    c.execute('''CREATE TABLE IF NOT EXISTS steps 
                 (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, 
                 PRIMARY KEY(user_email, dossier_nom, step_idx))''')
    conn.commit()
    conn.close()

init_db()

# --- 3. LOGIQUE MÉTIER (MÉTHODE FREEMAN) ---
class FreemanEngine:
    def __init__(self):
        self.steps_titles = [
            "1. Qualification (Diagnostic)", "2. Objectif (Le Gain)", 
            "3. Base Légale (Loi/Juris)", "4. Inventaire (Preuves)", 
            "5. Analyse des Risques", "6. Stratégie Amiable",
            "7. Plan d'Attaque (Tactique)", "8. Rédaction (Actes)", 
            "9. Audience (Préparation)", "10. Jugement (Analyse)", 
            "11. Recours (Suites)"
        ]

    async def get_kareem_analysis(self, step_idx, user_input):
        """Appel à l'IA Kareem pour l'analyse juridique"""
        prompt = f"""
        Tu es Kareem, IA d'élite spécialisée en Droit des Contrats et Obligations.
        Méthode Freeman - Étape {step_idx + 1}: {self.steps_titles[step_idx]}
        
        FAITS FOURNIS : {user_input}
        
        TON RÔLE :
        - Analyse stratégique rigoureuse.
        - Cite les articles du Code Civil (réforme 2016).
        - Formatage : Utilise '### 📜 ANALYSE' et '### 💡 STRATÉGIE'.
        """
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erreur de connexion à Kareem : {str(e)}"

engine = FreemanEngine()

# --- 4. INTERFACE UTILISATEUR (UI) ---

@ui.page('/login')
def login_page():
    with ui.card().classes('absolute-center p-12 w-96 bg-slate-950 border border-emerald-500/30 shadow-2xl rounded-2xl'):
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 mx-auto mb-2 tracking-tighter')
        ui.label('FREEMAN METHOD').classes('text-[10px] text-emerald-500/50 mx-auto mb-8 tracking-[0.3em] font-bold')
        
        email = ui.input('Email du Cabinet').props('dark outlined color=emerald').classes('w-full mb-4')
        
        def handle_login():
            if email.value:
                app.storage.user.update({'authenticated': True, 'email': email.value})
                ui.navigate.to('/')
            else:
                ui.notify('Veuillez entrer un email valide', color='warning')

        ui.button('ACCÉDER AU SYSTÈME', on_click=handle_login).classes('w-full bg-emerald-600 hover:bg-emerald-500 font-bold py-3 rounded-xl')
        ui.label('Paiement sécurisé par Stripe').classes('text-[10px] text-slate-600 mx-auto mt-6')

@ui.page('/')
def main_page():
    # Redirection si non connecté
    if not app.storage.user.get('authenticated', False):
        return ui.navigate.to('/login')

    user_email = app.storage.user.get('email')
    state = {'step_idx': 0, 'dossier': 'Dossier_Standard'}

    ui.query('body').style('background-color: #020617; color: #f8fafc; font-family: "Inter", sans-serif;')

    # --- HEADER ---
    with ui.header().classes('bg-slate-950/80 backdrop-blur-md border-b border-emerald-500/10 p-6 justify-between items-center'):
        with ui.row().classes('items-center gap-3'):
            ui.label('LEGAL OS').classes('text-2xl font-black text-emerald-500 tracking-tighter')
            ui.badge('V11 PRO', color='emerald').classes('text-[8px] font-bold')
        
        with ui.row().classes('items-center gap-6'):
            ui.label(user_email).classes('text-xs text-slate-500 italic')
            ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    # --- LAYOUT PRINCIPAL ---
    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        
        # Sidebar Gauche (Navigation des 11 étapes)
        with ui.column().classes('w-80 bg-slate-950 p-6 border-r border-slate-900 h-full overflow-y-auto'):
            ui.label('NAVIGATION STRATÉGIQUE').classes('text-[10px] font-bold text-slate-700 mb-8 tracking-widest uppercase')
            for i, title in enumerate(engine.steps_titles):
                is_active = (i == state['step_idx'])
                with ui.row().classes(f'''w-full p-4 mb-2 rounded-xl cursor-pointer transition-all 
                    {"bg-emerald-500/10 border border-emerald-500/20 shadow-lg" if is_active else "hover:bg-slate-900/50"}''') as r:
                    ui.label(str(i+1)).classes(f'font-black {"text-emerald-500" if is_active else "text-slate-800"}')
                    ui.label(title.split('(')[0]).classes(f'text-xs {"text-slate-100 font-bold" if is_active else "text-slate-500"}')
                    r.on('click', lambda i=i: (state.update({'step_idx': i}), ui.navigate.to('/')))

        # Zone de Travail Centrale
        with ui.column().classes('flex-grow p-12 overflow-y-auto max-w-5xl'):
            ui.label(f"SEQUENCE {state['step_idx'] + 1}").classes('text-emerald-500 font-bold text-[10px] tracking-[0.4em] mb-2')
            ui.label(engine.steps_titles[state['step_idx']]).classes('text-5xl font-black mb-12 tracking-tight text-slate-100')

            # Chargement des données sauvegardées
            conn = sqlite3.connect('legalos_v11.db'); c = conn.cursor()
            c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND step_idx=?", (user_email, state['step_idx']))
            row = c.fetchone(); conn.close()
            saved_faits, saved_analyse = row if row else ("", "")

            with ui.card().classes('bg-slate-900/40 border border-slate-800 p-8 w-full rounded-2xl shadow-inner'):
                ui.label('SAISIE DES FAITS ET PIÈCES').classes('text-[10px] font-bold text-slate-600 mb-4 tracking-widest')
                input_area = ui.textarea(value=saved_faits, placeholder='Décrivez ici les éléments contractuels...').classes('w-full text-lg bg-transparent text-slate-200').props('borderless dark')
                
                async def run_kareem_flow():
                    if not input_area.value:
                        ui.notify('Veuillez saisir des faits', color='warning')
                        return
                    
                    output_container.clear()
                    with output_container:
                        ui.spinner(size='lg', color='emerald').classes('mx-auto mt-4')
                    
                    analysis = await engine.get_kareem_analysis(state['step_idx'], input_area.value)
                    
                    # Sauvegarde en base
                    conn = sqlite3.connect('legalos_v11.db'); c = conn.cursor()
                    c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?)", 
                              (user_email, state['dossier'], state['step_idx'], input_area.value, analysis))
                    conn.commit(); conn.close()

                    output_container.clear()
                    with output_container:
                        ui.markdown(analysis).classes('p-8 bg-slate-900 border-l-4 border-emerald-500 rounded-r-xl text-slate-100 shadow-2xl w-full leading-relaxed')

                ui.button('LANCER L\'ANALYSE KAREEM', on_click=run_kareem_flow).classes('w-full mt-8 bg-emerald-600 hover:bg-emerald-500 font-black py-4 rounded-xl shadow-xl shadow-emerald-900/20 transition-transform active:scale-95')

            # Container pour le résultat
            output_container = ui.column().classes('w-full mt-8')
            if saved_analyse:
                with output_container:
                    ui.markdown(saved_analyse).classes('p-8 bg-slate-900 border-l-4 border-emerald-500 rounded-r-xl text-slate-100 shadow-2xl w-full')

# --- 5. LANCEMENT SÉCURISÉ (Fix pour Windows & Python 3.14) ---
if __name__ in {"__main__", "__mp_main__"}:
    # Note : storage_secret est indispensable pour garder la session de login
    ui.run(
        title="LegalOS - Freeman Method", 
        dark=True, 
        port=8080, 
        reload=False, 
        storage_secret='freeman_ultra_secret_2026'
    )
