from nicegui import ui
import asyncio
# Assure-toi que database.py est dans le même dossier
from database import init_db, add_user, login_user, charger_dossier, sauvegarder_dossier

# --- INITIALISATION HORS UI ---
init_db()

class LegalOS:
    def __init__(self):
        self.user_auth = False
        self.user_email = ""
        self.user_name = ""
        self.etape_actuelle = 0
        self.etapes = [
            "Qualification", "Objectif", "Base légale", "Preuves", 
            "Stratégie", "Amiable", "Procédure", "Rédaction", 
            "Audience", "Jugement", "Exécution"
        ]

    def login(self, email, password):
        user = login_user(email, password)
        if user:
            self.user_auth = True
            self.user_email = email
            self.user_name = user[0]
            d = charger_dossier(email)
            self.etape_actuelle = (d[0] if d else 1) - 1
            ui.notify(f'Bienvenue {self.user_name}', color='positive')
            self.main_container.refresh()
        else:
            ui.notify('Identifiants incorrects', color='negative')

    @ui.refreshable
    def main_container(self):
        # Cette fonction gère l'affichage dynamique
        if not self.user_auth:
            self.render_login_screen()
        else:
            self.render_dashboard()

    def render_login_screen(self):
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-4 text-slate-800')
                with ui.tabs().classes('w-full') as tabs:
                    t1 = ui.tab('Connexion')
                    t2 = ui.tab('Inscription')
                with ui.tab_panels(tabs, value=t1).classes('w-full'):
                    with ui.tab_panel(t1):
                        e = ui.input('Email').classes('w-full')
                        p = ui.input('Mot de passe', password=True).classes('w-full')
                        ui.button('ACCÉDER', on_click=lambda: self.login(e.value, p.value)).classes('w-full mt-4')
                    with ui.tab_panel(t2):
                        ui.label('Contactez l\'administrateur pour un accès.')

    def render_dashboard(self):
        with ui.header().classes('items-center justify-between bg-slate-900 text-white p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('text-xl font-bold tracking-tight')
            ui.button(icon='logout', on_click=lambda: setattr(self, 'user_auth', False) or self.main_container.refresh(), color='white').props('flat rounded')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE DE RÉSOLUTION').classes('text-xs font-black text-slate-400 mb-4 tracking-widest')
                with ui.stepper().props('vertical animated') as stepper:
                    # On définit la valeur actuelle du stepper
                    stepper.value = self.etapes[self.etape_actuelle]
                    for nom in self.etapes:
                        ui.step(nom)
            
            # ZONE DE TRAVAIL
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'Étape {self.etape_actuelle + 1} : {self.etapes[self.etape_actuelle]}').classes('text-3xl font-light mb-6 text-slate-800')
                with ui.card().classes('w-full p-8 shadow-sm bg-white'):
                    ui.label('Instruction du Dossier').classes('text-h6 mb-4')
                    ui.textarea(label="Décrivez les faits ici...").classes('w-full h-64')
                
                with ui.row().classes('w-full mt-8 justify-between'):
                    ui.button('PRÉCÉDENT', on_click=lambda: self.change_step(-1)).props('flat')
                    ui.button('SUIVANT', on_click=lambda: self.change_step(1)).props('elevated')

    def change_step(self, direction):
        new_step = self.etape_actuelle + direction
        if 0 <= new_step < len(self.etapes):
            self.etape_actuelle = new_step
            self.main_container.refresh()

# --- INSTANCE UNIQUE ---
app_logic = LegalOS()

# --- DÉFINITION DE LA PAGE ---
@ui.page('/')
def index():
    # On définit les couleurs ici pour éviter le scope global
    ui.colors(primary='#1a237e', secondary='#42a5f5', accent='#00c853')
    app_logic.main_container()

# --- LANCEMENT ---
ui.run(title='LegalOS - Infrastructure Juridique', port=8080)
