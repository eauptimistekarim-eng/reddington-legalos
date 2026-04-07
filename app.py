import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui

# --- CHARGEMENT SÉCURISÉ ---
load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

class LegalOS:
    def __init__(self):
        self.user_email = "contact@cabinet.fr"
        self.current_dossier = "Dossier_Alpha_2026"  # Lié à ton projet Reddington
        self.current_step_idx = 0
        self.steps_titles = [
            "1. Qualification (Diagnostic)", "2. Objectif (Le Gain)", "3. Base Légale (Loi/Juris)",
            "4. Inventaire (Preuves)", "5. Analyse des Risques", "6. Stratégie Amiable",
            "7. Plan d'Attaque (Tactique)", "8. Rédaction (Actes)", "9. Audience (Préparation)",
            "10. Jugement (Analyse)", "11. Recours (Suites)"
        ] # Respect des 11 étapes de la méthode Reddington/Freeman
        self.setup_db()

    def setup_db(self):
        conn = sqlite3.connect('legalos_v11.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
        c.execute('''CREATE TABLE IF NOT EXISTS steps 
                    (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, 
                    validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))''')
        conn.commit()
        conn.close()

    def get_history(self):
        conn = sqlite3.connect('legalos_v11.db')
        c = conn.cursor()
        c.execute("SELECT step_idx, analyse FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx < ?", 
                  (self.user_email, self.current_dossier, self.current_step_idx + 1))
        rows = c.fetchall()
        conn.close()
        return "\n".join([f"E{r[0]}: {r[1][:200]}..." for r in rows])

    async def run_kareem(self, u_input, output_container):
        if not u_input:
            ui.notify("Saisissez des faits pour lancer Kareem", color='warning')
            return

        output_container.clear()
        with output_container:
            ui.spinner(size='lg', color='emerald').classes('mx-auto mt-4')

        history = self.get_history()
        
        # PROMPT EXPERT : CONTRATS / OBLIGATIONS / EXÉCUTIONS
        prompt = f"""
        Tu es Kareem, IA d'élite spécialisée en Droit des Contrats, Obligations et Exécutions.
        MÉTHODE FREEMAN - Étape {self.current_step_idx + 1}: {self.steps_titles[self.current_step_idx]}
        
        HISTORIQUE : {history}
        SAISIE ACTUELLE : {u_input}
        
        DIRECTIVES :
        1. Cite impérativement les articles du Code Civil (Réf. 2016).
        2. Analyse la force obligatoire, les manquements et les voies d'exécution.
        3. Format: 'ARTICLE: [Texte]' et 'DICO: [Vulgarisation]'.
        4. Ton ton est celui d'un Directeur Juridique : sec, précis, stratégique.
        """

        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            out = response.choices[0].message.content
            
            # Sauvegarde dans legalos_v11.db
            conn = sqlite3.connect('legalos_v11.db')
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO steps (user_email, dossier_nom, step_idx, faits, analyse) VALUES (?,?,?,?,?)", 
                      (self.user_email, self.current_dossier, self.current_step_idx + 1, u_input, out))
            conn.commit(); conn.close()

            output_container.clear()
            with output_container:
                res_box = ui.markdown('').classes('p-8 bg-slate-900 border-l-4 border-emerald-500 rounded-r-xl text-slate-100 shadow-2xl w-full leading-relaxed')
            
            typed = ""
            for char in out:
                typed += char
                fmt = typed.replace("ARTICLE:", "### 📜 FONDEMENT LÉGAL").replace("DICO:", "--- \n ### 📖 DICO")
                res_box.content = fmt + " ▌"
                await asyncio.sleep(0.002)
            res_box.content = fmt
            
        except Exception as e:
            ui.notify(f"Erreur API : {e}", color='red')

    @ui.page('/')
    def main_ui(self):
        ui.query('body').style('background-color: #020617; color: #f8fafc; font-family: "Inter", sans-serif;')
        
        # --- HEADER ---
        with ui.header().classes('bg-slate-950 border-b border-emerald-500/20 p-6 justify-between items-center'):
            with ui.row().classes('items-center gap-3'):
                ui.label('LEGAL OS').classes('text-2xl font-black text-emerald-500 tracking-tighter')
                ui.badge('FREEMAN METHOD', color='emerald').classes('text-[10px] px-2')
            
            with ui.row().classes('items-center gap-4'):
                ui.button('ACCÈS ILLIMITÉ (40€)', on_click=lambda: ui.open('https://buy.stripe.com/test_votre_lien')).props('elevated color=emerald').classes('font-bold rounded-full px-8 shadow-lg shadow-emerald-900/20')

        # --- CONTENU ---
        with ui.row().classes('w-full no-wrap h-screen gap-0'):
            # Sidebar
            with ui.column().classes('w-80 bg-slate-950 p-8 border-r border-slate-900 h-full overflow-y-auto'):
                ui.label('WORKFLOW').classes('text-[10px] font-bold text-slate-600 mb-8 tracking-[0.2em] uppercase')
                for i, title in enumerate(self.steps_titles):
                    active = i == self.current_step_idx
                    with ui.row().classes(f'w-full p-4 mb-2 rounded-xl cursor-pointer transition-all {"bg-emerald-500/10 border border-emerald-500/20" if active else "hover:bg-slate-900/50"}') as r:
                        ui.label(str(i+1)).classes(f'font-black {"text-emerald-500" if active else "text-slate-700"}')
                        ui.label(title.split('(')[0]).classes(f'text-xs font-bold {"text-slate-100" if active else "text-slate-500"}')
                        r.on('click', lambda i=i: (setattr(self, 'current_step_idx', i), ui.navigate.to('/')))

            # Main
            with ui.column().classes('flex-grow p-16 overflow-y-auto max-w-5xl'):
                ui.label(f"SÉQUENCE {self.current_step_idx + 1}").classes('text-emerald-500 font-bold text-xs tracking-widest mb-2')
                ui.label(self.steps_titles[self.current_step_idx]).classes('text-6xl font-black mb-12 tracking-tight text-slate-100')

                # Récupération données existantes
                conn = sqlite3.connect('legalos_v11.db'); c = conn.cursor()
                c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", 
                          (self.user_email, self.current_dossier, self.current_step_idx + 1))
                row = c.fetchone(); conn.close()
                f_db, a_db = row if row else ("", "")

                with ui.column().classes('w-full gap-8'):
                    with ui.card().classes('bg-slate-900/40 border border-slate-800 p-8 rounded-2xl shadow-inner w-full'):
                        ui.label('ÉLÉMENTS DU DOSSIER').classes('text-[10px] font-bold text-slate-500 mb-4 tracking-widest')
                        u_input = ui.textarea(value=f_db, placeholder='Saisissez les faits...').props('borderless dark').classes('w-full text-xl min-h-[250px] bg-transparent text-slate-200 focus:outline-none')
                        
                        with ui.row().classes('w-full justify-end mt-6 pt-6 border-t border-slate-800'):
                            ui.button('LANCER L\'ANALYSE KAREEM', on_click=lambda: self.run_kareem(u_input.value, output_container)).classes('px-12 py-4 bg-emerald-600 hover:bg-emerald-500 font-black rounded-xl shadow-xl shadow-emerald-900/40')

                    output_container = ui.column().classes('w-full mt-8')
                    if a_db:
                        with output_container:
                            ui.markdown(a_db.replace("ARTICLE:", "### 📜 FONDEMENT LÉGAL").replace("DICO:", "--- \n ### 📖 DICO")).classes('p-8 bg-slate-900 border-l-4 border-emerald-500 rounded-r-xl text-slate-100 shadow-2xl w-full')

app = LegalOS()
ui.run(title="LegalOS Freeman", dark=True, port=8080, reload=True)
