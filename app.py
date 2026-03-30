from nicegui import ui
import asyncio
# On garde tes connexions à la base de données
from database import init_db, add_user, login_user, charger_dossier, sauvegarder_dossier

# --- INITIALISATION ---
init_db()

class LegalOS:
    def __init__(self):
        self.user_auth = False
        self.user_email = ""
        self.user_name = ""
        self.etape_actuelle = 0
        self.etapes = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

    def login(self, email, password):
        # Simulation pour test (admin/123) ou vraie BDD
        user = login_user(email, password)
        if user or (email == "admin@legalos.fr" and password == "123"):
            self.user_auth = True
            self.user_email = email
            self.user_name = user[0] if user else "Karim Mabrouki"
            
            # On charge l'avancement
            d = charger_dossier(email)
            if d:
                self.etape_actuelle = d[0] - 1
                
            ui.notify(f'Système Freeman activé. Bienvenue {self.user_name}', color='positive')
            self.main_container.refresh()
        else:
            ui.notify('Accès refusé : Vérifiez vos identifiants', color='negative')

    def logout(self):
        self.user_auth = False
        self.main_container.refresh()

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
                p = ui.input('Mot de passe', password=True).classes('w-full').on('keydown.enter', lambda: self.login(e.value, p.value))
                ui.button('ACCÉDER AU SYSTÈME', on_click=lambda: self.login(e.value, p.value)).classes('w-full mt-6 py-4 font-bold')

    def render_dashboard(self):
        # BARRE DE NAVIGATION HAUTE
        with ui.header().classes('items-center justify-between bg-slate-900 text-white p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('text-xl font-bold tracking-tight')
            with ui.row().classes('items-center'):
                ui.label(self.user_name).classes('mr-4 text-xs uppercase tracking-widest text-slate-400')
                ui.button(icon='logout', on_click=self.logout, color='white').props('flat round')

        # CONTENU PRINCIPAL
        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            
            # MENU GAUCHE (Le Stepper)
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                with ui.stepper().props('vertical animated gray') as stepper:
                    stepper.value = self.etapes[self.etape_actuelle]
                    for nom in self.etapes:
                        ui.step(nom)

            # ZONE DE TRAVAIL CENTRALE
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {self.etape_actuelle + 1}').classes('text-xs font-bold text-primary tracking-widest')
                ui.label(self.etapes[self.etape_actuelle]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 shadow-xl bg-white border-t-4 border-primary'):
                    # CONTENU DYNAMIQUE SELON L'ÉTAPE
                    if self.etape_actuelle == 0:
                        ui.label('Instruction Initiale').classes('text-h6 mb-2 text-slate-700')
                        ui.textarea(label="Décrivez les faits du litige ici...").classes('w-full h-64')
                    else:
                        ui.label(f"Chargement du module {self.etapes[self.etape_actuelle]}...").classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-32')

                # BOUTONS DE NAVIGATION
                with ui.row().classes('w-full mt-12 justify-between items-center'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: self.change_step(-1)).props('flat').visible(self.etape_actuelle > 0)
                    ui.label(f'{self.etape_actuelle + 1} / 11').classes('text-slate-400 font-mono')
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: self.change_step(1)).props('elevated color=primary').visible(self.etape_actuelle < 10)

    def change_step(self, direction):
        new_step = self.etape_actuelle + direction
        if 0 <= new_step < len(self.etapes):
            self.etape_actuelle = new_step
            # On sauvegarde l'avancement dans la BDD
            try:
                sauvegarder_dossier(self.user_email, self.etape_actuelle + 1, "", "")
            except:
                pass
            self.main_container.refresh()

# --- POINT D'ENTRÉE ---
app_logic = LegalOS()

@ui.page('/')
def index():
    ui.colors(primary='#1a237e', secondary='#42a5f5', accent='#00c853')
    app_logic.main_container()

ui.run(title='LegalOS - Karim Mabrouki', port=8080, reload=True)
