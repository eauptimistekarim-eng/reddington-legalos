import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- CONFIGURATION & SÉCURITÉ ---
load_dotenv()
# Si le .env échoue encore, on utilise la clé en dur pour cette session (à sécuriser plus tard)
GROQ_KEY = os.getenv("GROQ_API_KEY") or GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('legalos_v11.db')
    c = conn.cursor()
    # Table des utilisateurs et leurs clés d'accès
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, access_key TEXT, paid INTEGER DEFAULT 0)''')
    # Table des étapes du dossier
    c.execute('''CREATE TABLE IF NOT EXISTS steps 
                 (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, 
                 PRIMARY KEY(user_email, dossier_nom, step_idx))''')
    conn.commit()
    conn.close()

init_db()

# --- LOGIQUE MÉTIER (KAREEM) ---
class LegalEngine:
    def __init__(self):
        self.steps_titles = [
            "1. Qualification (Diagnostic)", "2. Objectif (Le Gain)", 
            "3. Base Légale (Loi/Juris)", "4. Inventaire (Preuves)", 
            "5. Analyse des Risques", "6. Stratégie Amiable",
            "7. Plan d'Attaque (Tactique)", "8. Rédaction (Actes)", 
            "9. Audience (Préparation)", "10. Jugement (Analyse)", 
            "11. Recours (Suites)"
        ]

    async def ask_kareem(self, step_idx, user_input, history=""):
        prompt = f"""
        Tu es Kareem, IA d'élite en Droit des Contrats et Obligations (Méthode Freeman).
        Étape actuelle : {self.steps_titles[step_idx]}
        Historique dossier : {history}
        Nouveaux faits : {user_input}
        
        RÈGLES : 
        - Cite le Code Civil (réforme 2016).
        - Sois sec, précis et stratégique.
        - Structure : '📜 ANALYSE JURIDIQUE' puis '💡 CONSEIL STRATÉGIQUE'.
        """
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

engine = LegalEngine()

# --- INTERFACE UTILISATEUR (UI) ---

@ui.page('/login')
def login_page():
    with ui.card().classes('absolute-center p-12 w-96 shadow-2xl bg-slate-900 border border-emerald-500/30'):
        ui.label('LEGAL OS').classes('text-3xl font-black text-emerald-500 mx-auto mb-4')
        ui.label('Entrez votre clé d\'accès Freeman').classes('text-slate-400 text-center mb-6')
        
        key_input = ui.input('Clé d\'accès').props('dark outlined').classes('w-full')
        
        def try_login():
            # Simplicité pour le test : n'importe quelle clé > 5 caractères passe
            if len(key_input.value) > 5:
                app.storage.user.update({'authenticated': True, 'email': 'user@example.com'})
                ui.navigate.to('/')
            else:
                ui.notify('Clé invalide ou abonnement expiré', color='red')

        ui.button('ACTIVER L\'ACCÈS', on_click=try_login).classes('w-full bg-emerald-600 mt-4 py-3')
        ui.link('Obtenir une clé (40€)', 'https://buy.stripe.com/test_votre_lien').classes('mx-auto mt-4 text-xs text-slate-500')

@ui.page('/')
def main_page():
    if not app.storage.user.get('authenticated', False):
        return ui.navigate.to('/login')

    # État de la page
    state = {'step': 0, 'dossier': 'Dossier_Principal'}
    user_email = app.storage.user.get('email')

    ui.query('body').style('background-color: #020617; color: #f8fafc;')

    # --- HEADER ---
    with ui.header().classes('bg-slate-950 border-b border-emerald-500/20 p-6 justify-between items-center'):
        ui.label('LEGAL OS | FREEMAN').classes('text-2xl font-black text-emerald-500')
        with ui.row().classes('items-center gap-4'):
            ui.label(user_email).classes('text-xs text-slate-500')
            ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    # --- LAYOUT ---
    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        
        # Sidebar
        with ui.column().classes('w-72 bg-slate-950 p-6 border-r border-slate-900'):
            ui.label('VOTRE STRATÉGIE').classes('text-[10px] font-bold text-slate-600 mb-6 tracking-widest')
            nav_containers = []
            for i, title in enumerate(engine.steps_titles):
                is_active = (i == state['step'])
                with ui.row().classes(f'w-full p-3 mb-1 rounded-lg cursor-pointer {"bg-emerald-500/10 border border-emerald-500/20" if is_active else "hover:bg-slate-900/50"}') as r:
                    ui.label(f"{i+1}").classes('font-black text-emerald-500' if is_active else 'text-slate-700')
                    ui.label(title.split('(')[0]).classes('text-xs' + (' text-white font-bold' if is_active else ' text-slate-500'))
                    r.on('click', lambda i=i: (state.update({'step': i}), ui.navigate.to('/')))

        # Zone de travail
        with ui.column().classes('flex-grow p-12 max-w-5xl overflow-y-auto'):
            ui.label(f"ÉTAPE {state['step'] + 1}").classes('text-emerald-500 font-bold text-xs tracking-widest mb-2')
            ui.label(engine.steps_titles[state['step']]).classes('text-5xl font-black mb-10 tracking-tighter')

            # Chargement data
            conn = sqlite3.connect('legalos_v11.db'); c = conn.cursor()
            c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND step_idx=?", (user_email, state['step']))
            res = c.fetchone(); conn.close()
            saved_faits, saved_analyse = res if res else ("", "")

            with ui.card().classes('bg-slate-900/40 border border-slate-800 p-8 w-full rounded-2xl'):
                input_area = ui.textarea(value=saved_faits, placeholder='Saisissez les faits ou éléments de cette étape...').classes('w-full text-lg bg-transparent').props('borderless dark')
                
                async def process():
                    output_card.clear()
                    with output_card: ui.spinner(color='emerald').classes('mx-auto')
                    
                    try:
                        ans = await engine.ask_kareem(state['step'], input_area.value)
                        # Save
                        conn = sqlite3.connect('legalos_v11.db'); c = conn.cursor()
                        c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?)", (user_email, state['dossier'], state['step'], input_area.value, ans))
                        conn.commit(); conn.close()
                        
                        output_card.clear()
                        with output_card:
                            ui.markdown(ans).classes('p-6 text-slate-200 leading-relaxed')
                    except Exception as e:
                        ui.notify(f"Erreur : {e}", color='red')

                ui.button('ANALYSE KAREEM', on_click=process).classes('w-full mt-6 bg-emerald-600 font-black py-4 rounded-xl shadow-lg')

            output_card = ui.column().classes('w-full mt-8 bg-slate-900 border-l-4 border-emerald-500 rounded-r-xl')
            if saved_analyse:
                with output_card: ui.markdown(saved_analyse).classes('p-6 text-slate-200')

# --- LANCEMENT ---
if __name__ in {"__main__", "__mp_main__"}:
    # 'storage_secret' est requis pour les sessions (login)
    ui.run(title="LegalOS Freeman", dark=True, port=8080, reload=False, storage_secret='freeman_secret_key_2026')
