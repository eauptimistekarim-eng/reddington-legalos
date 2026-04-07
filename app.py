C'est noté. Pour éviter toute confusion entre les versions, voici le code **complet, corrigé et sécurisé**. 

Ce code règle l'erreur `sqlite3.OperationalError` en s'assurant que la structure de la base de données (4 colonnes) correspond parfaitement aux données envoyées (4 valeurs).

### ⚠️ IMPORTANT AVANT DE LANCER :
**Supprime le fichier `legalos_prod.db`** dans ton dossier pour que le script puisse recréer la table avec la bonne structure.

```python
import os
import sqlite3
import asyncio
import json
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui, app

# --- 1. CHARGEMENT SÉCURISÉ ---
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print(f"✅ Fichier .env détecté à : {env_path}")
else:
    print(f"❌ ERREUR : Le fichier .env est introuvable à : {env_path}")

GROQ_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_KEY:
    print("❌ LA CLÉ GROQ_API_KEY EST VIDE. Vérifie ton .env")
    client = None
else:
    print(f"🚀 KAREEM OPÉRAȚIONNEL (Clé : {GROQ_KEY[:10]}...)")
    client = Groq(api_key=GROQ_KEY)

# --- 2. BASE DE DONNÉES (STRUCTURE FIXE : 4 COLONNES) ---
def init_db():
    conn = sqlite3.connect('legalos_prod.db', check_same_thread=False)
    c = conn.cursor()
    # On crée une table propre avec exactement 4 colonnes
    c.execute('''CREATE TABLE IF NOT EXISTS steps 
                 (user_email TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, 
                 PRIMARY KEY(user_email, step_idx))''')
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
        if not client:
            ui.notify("Erreur : Clé API manquante", color='red')
            return None
            
        prompt = f"""
        Tu es Kareem, IA experte en droit français (Méthode Freeman). 
        Analyse les faits suivants : {user_input}
        Génère une stratégie complète en 11 étapes détaillées.
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "steps": [ {{"idx": 0, "content": "..."}}, ... ] }}
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
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 mx-auto mb-2 text-center tracking-tighter')
        email = ui.input('Email professionnel').props('dark outlined color=emerald').classes('w-full mb-4')
        
        def auth():
            if not email.value: return ui.notify("Email requis")
            app.storage.user.update({'auth': True, 'email': email.value})
            ui.navigate.to('/')
        ui.button('ACCÉDER AU CABINET', on_click=auth).classes('w-full bg-emerald-600 font-bold py-3 rounded-xl')

@ui.page('/')
def main():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    
    user_email = app.storage.user.get('email')
    if 'step_idx' not in app.storage.user: app.storage.user['step_idx'] = 0
    current_idx = app.storage.user['step_idx']

    ui.query('body').style('background-color: #020617; color: #f8fafc;')

    with ui.header().classes('bg-slate-950/80 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.label('LEGAL OS').classes('text-xl font-black text-emerald-500')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Sidebar
        with ui.column().classes('w-64 bg-slate-950 p-4 border-r border-slate-900 h-full'):
            for i, t in enumerate(engine.titles):
                is_active = (i == current_idx)
                with ui.row().classes(f'w-full p-3 mb-1 rounded-lg cursor-pointer { "bg-emerald-500/10 border-l-2 border-emerald-500" if is_active else "" }') as r:
                    ui.label(t).classes(f'text-[10px] uppercase { "text-emerald-400 font-bold" if is_active else "text-slate-500" }')
                    r.on('click', lambda i=i: (app.storage.user.update({'step_idx': i}), ui.navigate.to('/')))

        # Main Area
        with ui.column().classes('flex-grow p-12 overflow-y-auto'):
            ui.label(engine.titles[current_idx]).classes('text-4xl font-black mb-8')
            
            conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
            c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND step_idx=?", (user_email, current_idx))
            res = c.fetchone(); conn.close()
            s_faits, s_analyse = res if res else ("", "")

            with ui.card().classes('bg-slate-900 border border-slate-800 p-8 w-full rounded-2xl shadow-xl'):
                input_area = ui.textarea(value=s_faits, placeholder='Décrivez votre affaire ici...').classes('w-full text-lg').props('dark borderless autogrow')
                
                async def run_analysis():
                    if not input_area.value: return ui.notify("Veuillez saisir des faits.")
                    
                    spinner.set_visibility(True)
                    btn_gen.set_visibility(False)
                    
                    data = await engine.generate_full_strategy(input_area.value)
                    
                    if data:
                        conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
                        for s in data['steps']:
                            # INSERTION DES 4 VALEURS CORRESPONDANTES AUX 4 COLONNES
                            c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?)", 
                                      (user_email, s['idx'], input_area.value if s['idx']==0 else "Analyse Freeman", s['content']))
                        conn.commit(); conn.close()
                        ui.notify("Analyse terminée !", color='emerald')
                        ui.navigate.to('/')
                    
                    spinner.set_visibility(False)
                    btn_gen.set_visibility(True)

                if current_idx == 0:
                    btn_gen = ui.button('LANCER L\'ANALYSE FREEMAN', on_click=run_analysis).classes('w-full mt-4 bg-emerald-600 py-3 rounded-xl')
                    spinner = ui.spinner(color='emerald', size='lg').classes('mx-auto mt-4'); spinner.set_visibility(False)

            if s_analyse:
                with ui.card().classes('w-full mt-6 bg-slate-900/50 p-8 border border-slate-800 rounded-2xl'):
                    ui.label('RÉSULTAT KAREEM').classes('text-[10px] text-emerald-500 font-bold mb-4 tracking-widest')
                    ui.markdown(s_analyse).classes('text-slate-300 leading-relaxed')

# --- 5. LANCEMENT ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='SECRET_KEY_2026', dark=True, reload=False, title="LegalOS")
```
