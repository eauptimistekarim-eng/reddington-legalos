from nicegui import ui
import asyncio
# On importe tes fonctions de base de données existantes
from database import init_db, add_user, login_user, charger_dossier, sauvegarder_dossier

# --- INITIALISATION ---
init_db()

# --- CONFIGURATION DU DESIGN (Look Banque/SaaS) ---
ui.colors(primary='#1a237e', secondary='#42a5f5', accent='#00c853')

class LegalOS:
    def __init__(self):
        self.user_auth = False
        self.user_email = ""
        self.user_name = ""
        self.etape_actuelle = 1
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
            self.etape_actuelle = (d[0] if d else 1) - 1 # NiceGUI utilise des index 0
            ui.notify(f'Bienvenue {self.user_name}', color='positive')
            self.render_main_interface.refresh()
        else:
            ui.notify('Identifiants incorrects', color='negative')

    def logout(self):
        self.user_auth = False
        self.render_main_interface.refresh()

    @ui.refreshable
    def render_main_interface(self):
        if not self.user_auth:
            self.render_login_screen()
        else:
            self.render_dashboard()

    def render_login_screen(self):
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-4')
                with ui.tabs().classes('w-full') as tabs:
                    t1 = ui.tab('Connexion')
                    t2 = ui.tab('Inscription')
                with ui.tab_panels(tabs, value=t1).classes('w-full'):
                    with ui.tab_panel(t1):
                        e = ui.input('Email').classes('w-full')
                        p = ui.input('Mot de passe', password=True).classes('w-full')
                        ui.button('ACCÉDER', on_click=lambda: self.login(e.value, p.value)).classes('w-full mt-4')
                    with ui.tab_panel(t2):
                        n = ui.input('Nom').classes('w-full')
                        em = ui.input('Email').classes('w-full')
                        pw = ui.input('Mot de passe', password=True).classes('w-full')
                        ui.button('CRÉER COMPTE', on_click=lambda: ui.notify('Compte créé !')).classes('w-full mt-4')

    def render_dashboard(self):
        # HEADER
        with ui.header().classes('items-center justify-between bg-primary text-white p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('text-xl font-bold tracking-tight')
            with ui.row().classes('items-center'):
                ui.label(f'👤 {self.user_name}').classes('mr-4')
                ui.button(icon='logout', on_click=self.logout, color='white').props('flat rounded')

        # MAIN CONTENT
        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            
            # SIDEBAR (Le Stepper interactif)
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE DE RÉSOLUTON').classes('text-xs font-black text-slate-400 mb-4')
                with ui.stepper().props('vertical animated') as stepper:
                    stepper.value = self.etapes[self.etape_actuelle]
                    for i, nom in enumerate(self.etapes):
                        with ui.step(nom):
                            ui.label(f"Phase {i+1} en cours").classes('text-xs italic text-primary')
                
                ui.button('SAUVEGARDER DOSSIER', icon='save', on_click=lambda: ui.notify('Dossier sécurisé')).classes('w-full mt-10').props('outline')

            # ZONE DE TRAVAIL
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'Étape {self.etape_actuelle + 1} : {self.etapes[self.etape_actuelle]}').classes('text-3xl font-light mb-6 text-slate-800')
                
                with ui.card().classes('w-full p-8 shadow-sm bg-white'):
                    # Ici on simule le contenu des vues (view/etape_x.py)
                    if self.etape_actuelle == 0:
                        ui.markdown("### Analyse de Qualification")
                        ui.textarea(label="Décrivez les faits bruts").classes('w-full h-64')
                    elif self.etape_actuelle == 1:
                        ui.markdown("### Définition de l'Objectif")
                        ui.select(['Recouvrement', 'Dommages-Intérêts', 'Annulation de contrat'], label='Objectif visé').classes('w-full')
                    else:
                        ui.label('Module expert en cours de chargement...').classes('italic text-grey-6')

                # NAVIGATION BAS DE PAGE
                with ui.row().classes('w-full mt-8 justify-between'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', 
                              on_click=lambda: self.change_step(-1)).props('flat')
                    ui.button('SUIVANT', icon='arrow_forward', 
                              on_click=lambda: self.change_step(1)).props('elevated')

    def change_step(self, direction):
        new_step = self.etape_actuelle + direction
        if 0 <= new_step < len(self.etapes):
            self.etape_actuelle = new_step
            # Sauvegarde automatique en BDD
            sauvegarder_dossier(self.user_email, self.etape_actuelle + 1, "", "")
            self.render_main_interface.refresh()

# --- LANCEMENT DE L'APPLICATION ---
app_logic = LegalOS()

@ui.page('/')
def main_page():
    app_logic.render_main_interface()

ui.run(title='LegalOS - Infrastructure Juridique', port=8080)
