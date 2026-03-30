from nicegui import ui
import asyncio
# Assure-toi que database.py est présent
from database import init_db, add_user, login_user, charger_dossier, sauvegarder_dossier

# --- INITIALISATION ---
init_db()

class LegalOS:
    def __init__(self):
        self.user_auth = False
        self.user_email = ""
        self.user_name = ""
        self.etape_actuelle = 0
        self.faits_bruts = ""
        self.etapes = [
            "Qualification", "Objectif", "Base légale", "Preuves", 
            "Stratégie", "Amiable", "Procédure", "Rédaction", 
            "Audience", "Jugement", "Exécution"
        ]

    def login(self, email, password):
        user = login_user(email, password)
        if user or (email == "admin@legalos.fr" and password == "123"):
            self.user_auth = True
            self.user_email = email
            self.user_name = user[0] if user else "Karim Mabrouki"
            d = charger_dossier(email)
            if d:
                self.etape_actuelle = d[0] - 1
            ui.notify(f'Système Freeman activé. Bienvenue {self.user_name}', color='positive')
            self.main_container.refresh()
        else:
            ui.notify('Accès refusé', color='negative')

    @ui.refreshable
    def main_container(self):
        if not self.user_auth:
            self.render_login_screen()
        else:
            self.render_dashboard()

    def render_login_screen(self):
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-6 text-slate-800')
                e = ui.input('Email').classes('w-full')
                p = ui.input('Mot de passe', password=True).classes('w-full')
                ui.button('ACCÉDER', on_click=lambda: self.login(e.value, p.value)).classes('w-full mt-6 py-4')

    def render_dashboard(self):
        with ui.header().classes('items-center justify-between bg-slate-900 text-white p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('text-xl font-bold tracking-tight')
            ui.button(icon='logout', on_click=lambda: setattr(self, 'user_auth', False) or self.main_container.refresh(), color='white').props('flat round')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                with ui.stepper().props('vertical animated gray') as stepper:
                    stepper.value = self.etapes[self.etape_actuelle]
                    for nom in self.etapes:
                        ui.step(nom)

            # ZONE DE TRAVAIL
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {self.etape_actuelle + 1}').classes('text-xs font-bold text-primary')
                ui.label(self.etapes[self.etape_actuelle]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 shadow-xl bg-white border-t-4 border-primary'):
                    if self.etape_actuelle == 0:
                        ui.label('Analyse factuelle du litige').classes('text-h6 mb-2')
                        ui.textarea(label="Récit des faits").classes('w-full h-64')
                    else:
                        ui.label(f"Module d'instruction pour {self.etapes[self.etape_actuelle]}").classes('italic text-slate-400')
                
                with ui.row().classes('w-full mt-12 justify-between'):
                    ui.button('PRÉCÉDENT', on_click=lambda: self.change_step(-1)).props('flat').visible(self.etape_actuelle > 0)
                    ui.button('SUIVANT', on_click=lambda: self.change_step(1)).props('elevated color=primary').visible(self.etape_actuelle < 10)

    def change_step(self, direction):
        new_step = self.etape_actuelle + direction
        if 0 <= new_step < len(self.etapes):
            self.etape_actuelle = new_step
            self.main_container.refresh()

app_logic = LegalOS()

@ui.page('/')
def index():
    ui.colors(primary='#1a237e', secondary='#42a5f5', accent='#00c853')
    app_logic.main_container()

ui.run(title='LegalOS - Karim Mabrouki', port=8080)
