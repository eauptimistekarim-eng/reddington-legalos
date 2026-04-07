import os
import sqlite3
import asyncio
import json
import resend
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- 1. CONFIGURATION RÉELLE ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
resend.api_key = os.getenv("RESEND_API_KEY")

# --- 2. BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('legalos_prod.db', check_same_thread=False)
    c = conn.cursor()
    # Table Utilisateurs : gère les accès et le statut Pro
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, is_pro INTEGER DEFAULT 0, dossiers_count INTEGER DEFAULT 0)''')
    # Table Étapes : Stocke les analyses de la méthode Freeman
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
            "Qualification", "Objectif", "Base Légale", "Inventaire", 
            "Risques", "Amiable", "Attaque", "Rédaction", "Audience", "Jugement", "Recours"
        ]

    async def generate_full_strategy(self, user_input):
        """L'IA pré-analyse les 11 étapes d'un coup"""
        prompt = f"""
        Tu es Kareem, expert en Droit (Méthode Freeman). Analyse : {user_input}
        Réponds UNIQUEMENT en JSON avec cette structure précise :
        {{"steps": [
            {{"idx": 0, "content": "Analyse de qualification..."}},
            ... (jusqu'à l'index 10)
        ]}}
        Utilise le droit français. Sois technique et stratégique.
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
            print(f"Erreur IA : {e}")
            return None

engine = KareemEngine()

# --- 4. SERVICES (EMAIL) ---
async def send_magic_link(email):
    """Envoie un vrai mail via Resend (si l'API KEY est présente)"""
    if not resend.api_key:
        ui.notify("Mode simulation : Email non envoyé (Clé API manquante)", color='warning')
        return True
    
    try:
        resend.Emails.send({
            "from": "Kareem <onboarding@resend.dev>",
            "to": [email],
            "subject": "Accès à votre Cabinet LegalOS",
            "html": f"<strong>Bienvenue.</strong> Connectez-vous ici : <a href='#'>Lien d'accès</a>"
        })
        return True
    except Exception as e:
        ui.notify(f"Erreur mail : {e}", color='red')
        return False

# --- 5. PAGES UI ---

@ui.page('/login')
def login_page():
    with ui.card().classes('absolute-center p-12 w-96 bg-slate-950 border border-emerald-500/30 shadow-2xl rounded-2xl'):
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 mx-auto mb-2 tracking-tighter')
        ui.label('FREEMAN METHOD').classes('text-[10px] text-emerald-500/50 mx-auto mb-8 tracking-[0.3em]')
        
        email = ui.input('Email du Cabinet').props('dark outlined color=emerald').classes('w-full mb-4')
        
        async def auth(mode):
            if not email.value: return ui.notify("Email requis")
            success = await send_magic_link(email.value)
            if success:
                app.storage.user.update({'auth': True, 'email': email.value})
                conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email.value,))
                conn.commit(); conn.close()
                ui.navigate.to('/')

        ui.button('SE CONNECTER', on_click=lambda: auth("login")).classes('w-full bg-emerald-600 font-bold py-3 rounded-xl mb-3')
        ui.button('INSCRIPTION (1er Essai Offert)', on_click=lambda: auth("reg")).props('outline color=emerald').classes('w-full font-bold py-3 rounded-xl')

@ui.page('/')
def main():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    
    user_email = app.storage.user.get('email')
    state = app.storage.user.get('state', {'idx': 0})

    # Header
    with ui.header().classes('bg-slate-950 border-b border-emerald-500/10 p-6 justify-between items-center'):
        ui.label('LEGAL OS').classes('text-2xl font-black text-emerald-500')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Sidebar
        with ui.column().classes('w-72 bg-slate-950 p-6 border-r border-slate-900 h-full'):
            for i, t in enumerate(engine.titles):
                active = i == state['idx']
                with ui.row().classes(f'w-full p-3 mb-1 rounded-lg cursor-pointer { "bg-emerald-500/10" if active else "" }') as r:
                    ui.label(t).classes(f'text-xs { "text-emerald-500 font-bold" if active else "text-slate-500" }')
                    r.on('click', lambda i=i: (state.update({'idx': i}), app.storage.user.update({'state': state}), ui.navigate.to('/')))

        # Espace Travail
        with ui.column().classes('flex-grow p-12 overflow-y-auto'):
            ui.label(engine.titles[state['idx']]).classes('text-4xl font-black mb-8 text-slate-100')
            
            # DB Load
            conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
            c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND step_idx=?", (user_email, state['idx']))
            row = c.fetchone(); conn.close()
            s_faits, s_analyse = row if row else ("", "")

            with ui.card().classes('bg-slate-900 border border-slate-800 p-8 w-full rounded-2xl'):
                input_txt = ui.textarea(value=s_faits, placeholder='Qualification brute...').classes('w-full text-lg').props('dark borderless')
                
                async def process():
                    # Vérification quota (à lier à Stripe plus tard)
                    loading.set_visibility(True)
                    data = await engine.generate_full_strategy(input_txt.value)
                    if data:
                        conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
                        for s in data['steps']:
                            c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?)", 
                                      (user_email, "Dossier_1", s['idx'], input_txt.value if s['idx']==0 else "Auto", s['content']))
                        conn.commit(); conn.close()
                        ui.notify("Stratégie Freeman générée !", color='emerald')
                        ui.navigate.to('/')
                    loading.set_visibility(False)

                if state['idx'] == 0:
                    ui.button('GÉNÉRER TOUTE LA STRATÉGIE', on_click=process).classes('w-full mt-4 bg-emerald-600 font-bold py-4')
                
                loading = ui.spinner(color='emerald').classes('mx-auto mt-4')
                loading.set_visibility(False)

            if s_analyse:
                with ui.card().classes('w-full mt-6 bg-slate-900/50 p-8'):
                    ui.markdown(s_analyse)

# --- 6. RUN (CONFIG CLOUD) ---
if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get('PORT', 8080))
    ui.run(host='0.0.0.0', port=port, storage_secret='FREEMAN_SECRET_KEY_2026', dark=True, reload=False)
