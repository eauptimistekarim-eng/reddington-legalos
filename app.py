import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from groq import Groq
from nicegui import ui

# --- CHARGEMENT ---
load_dotenv()  # Va chercher le .env tout neuf que tu viens de créer
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

class LegalOS:
    def __init__(self):
        self.user_email = "contact@cabinet.fr"
        self.current_dossier = "Dossier_Alpha_2026"
        self.current_step_idx = 0
        self.steps_titles = [
            "1. Qualification (Diagnostic)", "2. Objectif (Le Gain)", 
            "3. Base Légale (Loi/Juris)", "4. Inventaire (Preuves)", 
            "5. Analyse des Risques", "6. Stratégie Amiable",
            "7. Plan d'Attaque (Tactique)", "8. Rédaction (Actes)", 
            "9. Audience (Préparation)", "10. Jugement (Analyse)", 
            "11. Recours (Suites)"
        ]
        self.setup_db()

    def setup_db(self):
        conn = sqlite3.connect('legalos_v11.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, PRIMARY KEY(user_email, dossier_nom, step_idx))')
        conn.commit()
        conn.close()

    async def run_kareem(self, u_input, output_container):
        if not u_input:
            ui.notify("Saisissez des faits", color='warning')
            return

        output_container.clear()
        with output_container:
            ui.spinner(size='lg', color='emerald').classes('mx-auto mt-4')

        prompt = f"""Tu es Kareem, expert en Droit des Contrats. 
        Analyse la situation suivante (Etape {self.current_step_idx + 1}): {u_input}.
        Donne les articles du Code Civil et la stratégie."""

        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            out = response.choices[0].message.content
            
            output_container.clear()
            with output_container:
                ui.markdown(out).classes('p-8 bg-slate-900 border-l-4 border-emerald-500 text-slate-100 rounded-r-xl shadow-2xl w-full')
            
        except Exception as e:
            ui.notify(f"Erreur : {e}", color='red')

    @ui.page('/')
    def main_ui(self):
        ui.query('body').style('background-color: #020617; color: #f8fafc;')
        
        with ui.header().classes('bg-slate-950 border-b border-emerald-500/20 p-6 justify-between items-center'):
            ui.label('LEGAL OS | FREEMAN').classes('text-2xl font-black text-emerald-500')
            ui.button('ACCÈS PRO (40€)').props('elevated color=emerald').classes('rounded-full font-bold')

        with ui.row().classes('w-full no-wrap h-screen gap-0'):
            # Sidebar
            with ui.column().classes('w-72 bg-slate-950 p-6 border-r border-slate-900'):
                for i, title in enumerate(self.steps_titles):
                    active = i == self.current_step_idx
                    with ui.row().classes(f'w-full p-3 mb-1 rounded-lg cursor-pointer {"bg-emerald-500/10 border border-emerald-500/20" if active else ""}') as r:
                        ui.label(title).classes(f'text-xs {"text-emerald-500 font-bold" if active else "text-slate-500"}')
                        r.on('click', lambda i=i: (setattr(self, 'current_step_idx', i), ui.navigate.to('/')))

            # Main Area
            with ui.column().classes('flex-grow p-12 max-w-4xl'):
                ui.label(self.steps_titles[self.current_step_idx]).classes('text-4xl font-black mb-8 text-slate-100')
                
                with ui.card().classes('bg-slate-900/40 border border-slate-800 p-6 w-full'):
                    u_input = ui.textarea(placeholder='Éléments du dossier...').classes('w-full text-lg bg-transparent text-slate-200').props('borderless dark')
                    ui.button('LANCER KAREEM', on_click=lambda: self.run_kareem(u_input.value, output_container)).classes('w-full mt-4 bg-emerald-600 font-bold py-3 rounded-lg')

                output_container = ui.column().classes('w-full mt-8')

app = LegalOS()
ui.run(title="LegalOS", dark=True, port=8080)
