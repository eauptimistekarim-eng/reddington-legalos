from nicegui import ui
import asyncio
# On garde tes imports de base de données
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
        # Logique de connexion (Vérifie tes identifiants BDD ou utilise admin/123 pour test)
        user = login_user(email, password)
        if user or (email == "admin@legalos.fr" and password == "123"):
            self.user_auth = True
            self.user_email = email
            self.user_name = user[0] if user else "Karim Mabrouki"
            
            # Récupération des données précédentes
            d = charger_dossier(email)
            if d:
                self.etape_actuelle = d[0] - 1
                self.faits_bruts = d[2] if len(d) > 2 else ""
                
            ui.notify(f'Système Freeman activé. Bienvenue {self.user_name}', color='positive')
            self.main_container.refresh()
        else:
            ui.notify('Accès refusé : Identifiants invalides', color='negative')

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
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2 text-slate-800')
                ui.label('Infrastructure Juridique').classes('text-xs text-center w-full mb-6 text-slate-400 uppercase tracking-widest')
                
                with ui.tabs().classes('w-full') as tabs:
                    t1 = ui.tab('Connexion')
                    t2 = ui.tab('Inscription')
                
                with ui.tab_panels(tabs, value=t1).classes('w-full bg-transparent'):
                    with ui.tab_panel(t1):
                        e = ui.input('Email').classes('w-full').on('keydown.enter', lambda: self.login(e.value, p.value))
                        p = ui.input('Mot de passe', password=True).classes('w-full').on('keydown.enter', lambda: self.login(e.value, p.value))
                        ui.button('ACCÉDER AU SYSTÈME', on_click=lambda: self.login(e.value, p.value)).classes('w-full mt-6 py-4 font-bold')
                    with ui.tab_panel(t2):
                        ui.label('Accès restreint. Contactez l\'administrateur.').classes('text-center italic text-slate-500')

    def render_dashboard(self):
        # HEADER PRO
        with ui.header().classes('items-center justify-between bg-slate-900 text-white p-4 shadow-lg'):
            with ui.row().classes('items-center'):
                ui.icon('security', size='sm').classes('mr-2 text-primary')
                ui.label('LEGALOS | Système Freeman v1.0').classes('text-xl font-bold tracking-tighter')
            
            with ui.row().classes('items-center'):
                ui.badge(self.user_name, color='primary').classes('mr-4 px-3')
                ui.button(icon='power_settings_new', on_click=self.logout, color='white').props('flat round')

        # LAYOUT PRINCIPAL
        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            
            # SIDEBAR : STEPPER (Preuve de rigueur juridique)
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE DE RÉSOLUTION').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                with ui.stepper().props('vertical animated gray') as stepper:
                    stepper.value = self.etapes[self.etape_actuelle]
                    for nom in self.etapes:
                        ui.step(nom)
                
                ui.separator().classes('my-6')
                ui.button('SAUVEGARDER', icon='save', on_click=self.save_data).classes('w-full').props('outline')

            # ZONE DE TRAVAIL DYNAMIQUE
            with ui.column().classes('w-2/4 p-10 overflow-auto'):
                ui.label(f'PHASE {self.etape_actuelle + 1}').classes('text-xs font-bold text-primary tracking-widest')
                ui.label(self.etapes[self.etape_actuelle]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 shadow-xl bg-white border-t-4 border-primary'):
                    self.render_step_content()
                
                # NAVIGATION
                with ui.row().classes('w-full mt-12 justify-between items-center'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: self.change_step(-1)).props('flat').visible(self.etape_actuelle > 0)
                    ui.label(f'{self.etape_actuelle + 1} / 11').classes('text-slate-400 font-mono')
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: self.change_step(1)).props('elevated color=primary').visible(self.etape_actuelle < 10)

            # PANEL KAREEM IA (L'assistant omniprésent)
            with ui.column().classes('w-1/4 bg-blue-50 p-6 border-l shadow-inner'):
                ui.label('ASSISTANT KAREEM').classes('text-xs font-black text-blue-900 mb-4 tracking-widest')
                with ui.scroll_area().classes('h-5/6 w-full'):
                    self.chat_container = ui.column().classes('w-full')
                    with self.chat_container:
                        ui.chat_message(f"Bonjour {self.user_name}. Je suis prêt pour l'étape : {self.etapes[self.etape_actuelle]}.", name='Kareem', avatar='https://robohash.org/kareem')
                
                with ui.row().classes('w-full items-center mt-4'):
                    msg_input = ui.input(placeholder='Demander à Kareem...').classes('flex-grow')
                    ui.button(icon='send', on_click=lambda: self.send_to_kareem(msg_input.value)).props('round flat')

    def render_step_content(self):
        """Injecte le contenu spécifique à chaque étape"""
        if self.etape_actuelle == 0: # Qualification
            ui.label('Analyse factuelle du litige').classes('text-h6 mb-2')
            self.txt_faits = ui.textarea(label="Récit des faits", value=self.faits_bruts).classes('w-full h-64')
        
        elif self.etape_actuelle == 7: # Rédaction
            ui.label('Génération de l\'acte juridique').classes('text-h6 mb-2')
            ui.markdown("Kareem va rédiger votre mise en demeure basée sur les étapes précédentes.")
            ui.button('GÉNÉRER LE PDF', icon='description', color='accent').classes('w-full py-4')
        
        else:
            ui.label(f"Module d'instruction pour {self.etapes[self.etape_actuelle]}").classes('italic text-slate-400
