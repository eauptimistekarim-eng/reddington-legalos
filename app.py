import os
import sqlite3
import asyncio
import json
from groq import Groq
from nicegui import ui, app

# =========================================================
# 1. TA CLÉ GROQ (COLLE TA CLÉ ENTRE LES GUILLEMETS)
# =========================================================
GROQ_KEY = "COLLE_TA_CLE_GSK_ICI" 

# Vérification immédiate
if "COLLE_TA_CLE" in GROQ_KEY:
    print("⚠️ ATTENTION : Tu n'as pas encore collé ta clé dans le code !")
else:
    print(f"✅ KAREEM INITIALISÉ (Clé : {GROQ_KEY[:10]}...)")

client = Groq(api_key=GROQ_KEY)

# =========================================================
# 2. BASE DE DONNÉES (MÉMOIRE DU CABINET)
# =========================================================
def init_db():
    conn = sqlite3.connect('legalos_prod.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS steps 
                 (user_email TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, 
                 PRIMARY KEY(user_email, step_idx))''')
    conn.commit()
    conn.close()

init_db()

# =========================================================
# 3. MOTEUR KAREEM (MÉTHODE FREEMAN)
# =========================================================
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
        
        Génère une stratégie complète en 11 étapes détaillées.
        RÉPONDS UNIQUEMENT EN JSON AVEC CETTE STRUCTURE :
        {{
          "steps": [
            {{"idx": 0, "content": "Analyse de qualification..."}},
            ... (jusqu'à l'index 10)
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

# =========================================================
# 4. INTERFACE UTILISATEUR (NICEGUI)
# =========================================================

@ui.page('/login')
def login_page():
    with ui.card().classes('absolute-center p-12 w-96 bg-slate-950 border border-emerald-500/30 shadow-2xl rounded-2xl'):
        ui.label('LEGAL OS').classes('text-4xl font-black text-emerald-500 mx-auto mb-2 tracking-tighter text-center')
        ui.label('SYSTÈME FREEMAN').classes('text-[10px] text-emerald-500/50 mx-auto mb-8 tracking-[0.3em] text-center')
        
        email = ui.input('Email professionnel').props('dark outlined color=emerald').classes('w-full mb-4')
        
        def auth():
            if not email.value: return ui.notify("Email requis")
            app.storage.user.update({'auth': True, 'email': email.value})
            ui.navigate.to('/')

        ui.button('ACCÉDER AU CABINET', on_click=auth).classes('w-full bg-emerald-600 font-bold py-3 rounded-xl shadow-lg shadow-emerald-900/20')

@ui.page('/')
def main():
    if not app.storage.user.get('auth'): return ui.navigate.to('/login')
    
    user_email = app.storage.user.get('email')
    # On initialise l'index de l'étape si non présent
    if 'step_idx' not in app.storage.user:
        app.storage.user['step_idx'] = 0
    
    current_idx = app.storage.user['step_idx']

    ui.query('body').style('background-color: #020617; color: #f8fafc; font-family: sans-serif;')

    # Header
    with ui.header().classes('bg-slate-950/80 border-b border-emerald-500/10 p-4 justify-between items-center'):
        ui.label('LEGAL OS').classes('text-xl font-black text-emerald-500 tracking-tighter')
        ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).props('flat color=slate-500')

    with ui.row().classes('w-full no-wrap h-screen gap-0'):
        # Barre Latérale (Menu des 11 étapes)
        with ui.column().classes('w-64 bg-slate-950 p-4 border-r border-slate-900 h-full'):
            for i, t in enumerate(engine.titles):
                is_active = (i == current_idx)
                with ui.row().classes(f'w-full p-3 mb-1 rounded-lg cursor-pointer transition-all { "bg-emerald-500/10 border-l-4 border-emerald-500" if is_active else "hover:bg-slate-900" }') as r:
                    ui.label(t).classes(f'text-[11px] uppercase tracking-wider { "text-emerald-400 font-bold" if is_active else "text-slate-500" }')
                    r.on('click', lambda i=i: (app.storage.user.update({'step_idx': i}), ui.navigate.to('/')))

        # Zone Centrale de Travail
        with ui.column().classes('flex-grow p-12 overflow-y-auto bg-slate-950'):
            ui.label(engine.titles[current_idx]).classes('text-5xl font-black mb-8 text-white tracking-tight')
            
            # Récupération de l'analyse dans la DB
            conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
            c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND step_idx=?", (user_email, current_idx))
            res = c.fetchone(); conn.close()
            s_faits, s_analyse = res if res else ("", "")

            # Carte d'entrée de texte (uniquement sur l'étape 1)
            with ui.card().classes('bg-slate-900 border border-slate-800 p-8 w-full rounded-3xl shadow-2xl'):
                input_area = ui.textarea(value=s_faits, placeholder='Saisissez ici les détails de l\'affaire...').classes('w-full text-lg text-slate-200').props('dark borderless autogrow')
                
                async def run_analysis():
                    if not input_area.value: 
                        ui.notify("Veuillez d'abord décrire l'affaire.", color='warning')
                        return
                    
                    spinner.set_visibility(True)
                    btn_gen.set_visibility(False)
                    
                    data = await engine.generate_full_strategy(input_area.value)
                    
                    if data:
                        conn = sqlite3.connect('legalos_prod.db'); c = conn.cursor()
                        for s in data['steps']:
                            c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?)", 
                                      (user_email, s['idx'], input_area.value if s['idx']==0 else "Analyse Freeman", s['content']))
                        conn.commit(); conn.close()
                        ui.notify("Cabinet mis à jour avec les 11 étapes !", color='emerald')
                        ui.navigate.to('/')
                    
                    spinner.set_visibility(False)
                    btn_gen.set_visibility(True)

                if current_idx == 0:
                    btn_gen = ui.button('GÉNÉRER LA STRATÉGIE COMPLÈTE', on_click=run_analysis).classes('w-full mt-6 bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 rounded-2xl shadow-lg')
                    spinner = ui.spinner(color='emerald', size='lg').classes('mx-auto mt-6')
                    spinner.set_visibility(False)

            # Affichage du résultat de l'IA
            if s_analyse:
                with ui.card().classes('w-full mt-8 bg-slate-900/30 p-10 border border-emerald-500/10 rounded-3xl'):
                    ui.label('ANALYSE KAREEM').classes('text-[10px] text-emerald-500 font-bold mb-6 tracking-[0.4em]')
                    ui.markdown(s_analyse).classes('text-slate-300 text-lg leading-relaxed')

# =========================================================
# 5. EXECUTION
# =========================================================
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        port=8080, 
        storage_secret='FREEMAN_SUPER_SECRET_2026', # Garde tes sessions privées
        dark=True, 
        title="LegalOS - Freeman Method",
        reload=False
    )
