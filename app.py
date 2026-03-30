from nicegui import ui
# Import de tes fonctions de base de données
try:
    from database import init_db, add_user, login_user, charger_dossier, sauvegarder_dossier
    init_db()
except ImportError:
    # Au cas où database.py n'est pas trouvé pour le test
    def login_user(e, p): return None
    def charger_dossier(e): return None
    def sauvegarder_dossier(e, et, f, b): pass

class LegalOS:
    def __init__(self):
        self.user_auth = False
        self.user_name = ""
        self.user_email = ""
        self.etape_actuelle = 0
        self.etapes = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

    def login(self, email, password):
        # TEST PRIORITAIRE : admin / 123
        if email == "admin@legalos.fr" and password == "123":
            self.user_auth = True
            self.user_name = "Karim Mabrouki (Admin)"
            self.user_email = email
            ui.notify('Accès Admin accordé', color='positive')
            self.container.refresh() # C'est ICI que la magie opère
            return

        # VRAIE BDD
        user = login_user(email, password)
        if user:
            self.user_auth = True
            self.user_name = user[0]
            self.user_email = email
            d = charger_dossier(email)
            if d: self.etape_actuelle = d[0] - 1
            self.container.refresh()
        else:
            ui.notify('Identifiants incorrects', color='negative')

    @ui.refreshable
    def container(self):
        """Cette fonction décide quoi afficher"""
        if not self.user_auth:
            self.render_login()
        else:
            self.render_app()

    def render_login(self):
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-indigo-900'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-4')
                ui.label('SYSTÈME FREEMAN').classes('text-xs text-center w-full mb-6 text-slate-400 tracking-widest')
                
                e = ui.input('Email').classes('w-full')
                p = ui.input('Mot de passe', password=True).classes('w-full').on('keydown.enter', lambda: self.login(e.value, p.value))
                
                ui.button('ACCÉDER', on_click=lambda: self.login(e.value, p.value)).classes('w-full mt-6 py-4 bg-indigo-900 text-white')

    def render_app(self):
        # HEADER
        with ui.header().classes('items-center justify-between bg-indigo-950 text-white p-4'):
            ui.label('LEGALOS | Tableau de bord').classes('font-bold')
            ui.button(icon='logout', on_click=lambda: setattr(self, 'user_auth', False) or self.container.refresh(), color='white').props('flat round')

        # MAIN CONTENT
        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('PROGRESSION').classes('text-xs font-black text-slate-400 mb-4')
                with ui.stepper().props('vertical animated') as stepper:
                    stepper.value = self.etapes[self.etape_actuelle]
                    for nom in self.etapes:
                        ui.step(nom)
            
            # WORKZONE
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'ÉTAPE {self.etape_actuelle + 1}').classes('text-xs font-bold text-indigo-800')
                ui.label(self.etapes[self.etape_actuelle]).classes('text-4xl font-light mb-6')
                
                with ui.card().classes('w-full p-8 shadow-sm bg-white'):
                    ui.textarea(label="Instruction du dossier...").classes('w-full h-64')

                with ui.row().classes('w-full mt-8 justify-between'):
                    ui.button('PRÉCÉDENT', on_click=lambda: self.move(-1)).props('flat').visible(self.etape_actuelle > 0)
                    ui.button('SUIVANT', on_click=lambda: self.move(1)).props('elevated').visible(self.etape_actuelle < 10)

    def move(self, d):
        self.etape_actuelle += d
        self.container.refresh()

# Lancement
legal = LegalOS()

@ui.page('/')
def index():
    ui.colors(primary='#1a237e')
    legal.container()

ui.run(port=8080, title='LegalOS')
