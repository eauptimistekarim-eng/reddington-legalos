import os
import sqlite3
import asyncio
import json
import resend
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- 1. CHARGEMENT SÉCURISÉ DES VARIABLES ---
# On force Python à trouver le .env dans le dossier du script
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

GROQ_KEY = os.getenv("GROQ_API_KEY")

# Petit diagnostic au lancement dans le terminal
if not GROQ_KEY:
    print("❌ ERREUR : La clé GROQ_API_KEY est introuvable. Vérifie ton fichier .env")
else:
    print(f"✅ CONFIGURATION : Clé chargée ({GROQ_KEY[:10]}...)")

client = Groq(api_key=GROQ_KEY)
resend.api_key = os.getenv("RESEND_API_KEY")

# --- 2. BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('legalos_prod.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, is_pro INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS steps 
                 (user_email TEXT, dossier_id TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, 
                 PRIMARY KEY(user_email, dossier_id, step_idx))''')
    conn.commit()
    conn.close()

init_db()

# --- 3. MOTEUR KAREEM (MÉTHODE FREEMAN) ---
class KareemEngine:
    def __init__(self):
        self.titles = [
            "1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", 
            "5. Risques", "6. Amiable", "7. Attaque", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Recours"
        ]

    async def generate_full_strategy(self, user_input):
        prompt = f"""
        Tu es Kareem, IA experte en droit français (Méthode Freeman). 
        Analyse les faits suivants : {user_input}
        
        Génère une stratégie complète en 11 étapes.
        RÉPOND UNIQUEMENT en JSON sous ce format :
        {{
          "steps": [
            {{"idx": 0, "content": "..."}},
            ... jusqu'à l'index 10
          ]
        }}
        """
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            ui.notify(f"Erreur IA : {e}", color='red')
            return None

engine = KareemEngine()

# --- 4. INTERFACE ---

@ui.page('/login')
def login_page():
    with ui.card().classes('absolute-center p-12 w-96 bg-slate-950 border border-emerald-500/30 shadow-2xl rounded-2xl'):
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 mx-auto mb-2 tracking-tighter text-center')
        ui.label('SYSTÈME FREEMAN').classes('text-[10px] text-emerald-500/50 mx-auto mb-8 tracking-[.3em] text-center')
        
        email = ui.input('Email professionnel').props('dark outlined color=emerald').classes('w-full mb-4')
        
        async def auth():
            if not email.value: return ui.notify("Email requis")
            app.storage.user.update({'auth': True, 'email': email.value})
            conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email.value,))
            conn.commit(); conn.close()
            ui.navigate.to('/')

        ui.button('ACCÉDER AU CABINET', on_click=auth).classes('w-full bg-emerald-600 font-bold py-3 rounded-xl')

@ui.page('/')
def main():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    
    user_email = app.storage.user.get('email')
    state = app.storage.user.get('state', {'idx': 0})

    ui.query('body').style('background-color: #020617;')

    with ui.header().classes('bg-slate-950/80 border-b border-emerald-500/10 p-6 justify-between items-center'):
        ui.label('LEGAL OS').classes('text-2xl font-black text-emerald-500')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Sidebar
        with ui.column().classes('w-72 bg-slate-950 p-6 border-r border-slate-900 h-full'):
            for i, t in enumerate(engine.titles):
                is_active = (i == state['idx'])
                with ui.row().classes(f'w-full p-3 mb-1 rounded-lg cursor-pointer { "bg-emerald-500/10" if is_active else "" }') as r:
                    ui.label(t).classes(f'text-xs { "text-emerald-400 font-bold" if is_active else "text-slate-500" }')
                    r.on('click', lambda i=i: (state.update({'idx': i}), app.storage.user.update({'state': state}), ui.navigate.to('/')))

        # Zone de travail
        with ui.column().classes('flex-grow p-12 overflow-y-auto'):
            ui.label(engine.titles[state['idx']]).classes('text-4xl font-black mb-8 text-slate-100')
            
            # Récupération données sauvegardées
            conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
            c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND step_idx=?", (user_email, state['idx']))
            res = c.fetchone(); conn.close()
            s_faits, s_analyse = res if res else ("", "")

            with ui.card().classes('bg-slate-900 border border-slate-800 p-8 w-full rounded-2xl shadow-xl'):
                input_area = ui.textarea(value=s_faits, placeholder='Décrivez les faits ici...').classes('w-full text-lg').props('dark borderless autogrow')
                
                async def run_analysis():
                    if not input_area.value: return ui.notify("Veuillez saisir des faits.")
                    
                    spinner.set_visibility(True)
                    btn_gen.set_visibility(False)
                    
                    data = await engine.generate_full_strategy(input_area.value)
                    
                    if data:
                        conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
                        for s in data['steps']:
                            c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?)", 
                                      (user_email, "DOSSIER_1", s['idx'], input_area.value if s['idx']==0 else "Auto-Freeman", s['content']))
                        conn.commit(); conn.close()
                        ui.notify("Analyse Freeman terminée !", color='emerald')
                        ui.navigate.to('/') # Rafraîchir
                    
                    spinner.set_visibility(False)
                    btn_gen.set_visibility(True)

                if state['idx'] == 0:
                    btn_gen = ui.button('LANCER L\'ANALYSE FREEMAN', on_click=run_analysis).classes('w-full mt-6 bg-emerald-600 font-bold py-4 rounded-xl')
                    spinner = ui.spinner(color='emerald', size='lg').classes('mx-auto mt-6')
                    spinner.set_visibility(False)

            if s_analyse:
                with ui.card().classes('w-full mt-8 bg-slate-900/50 p-8 border border-slate-800 rounded-2xl'):
                    ui.label('RÉSULTAT KAREEM').classes('text-[10px] text-emerald-500 font-bold mb-4 tracking-widest')
                    ui.markdown(s_analyse).classes('text-slate-300 leading-relaxed')

# --- 5. LANCEMENT ---
if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get('PORT', 8080))
    ui.run(
        host='0.0.0.0', 
        port=port, 
        storage_secret='FREEMAN_2026_SECRET', 
        dark=True, 
        reload=False,
        title="LegalOS"
    )
