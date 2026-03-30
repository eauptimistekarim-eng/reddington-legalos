from nicegui import ui

# --- CONFIGURATION ---
class LegalOS:
    def __init__(self):
        self.user_auth = False
        self.user_name = "Karim Mabrouki"
        self.etape_actuelle = 0
        self.etapes = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

    def login(self, e, p):
        # On force l'entrée pour le test : admin / 123
        if e == "admin@legalos.fr" and p == "123":
            self.user_auth = True
            ui.notify('Accès Système Freeman Activé', color='positive')
            ui.navigate.to('/') # On force la redirection pour rafraîchir proprement
        else:
            ui.notify('Erreur d\'identification', color='negative')

    def logout(self):
        self.user_auth = False
        ui.navigate.to('/')

# Instance unique
legal = LegalOS()

@ui.page('/')
def main_page():
    ui.colors(primary='#1a237e', secondary='#42a5f5', accent='#00c853')

    if not legal.user_auth:
        # --- ÉCRAN DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-6')
                email = ui.input('Email (admin@legalos.fr)').classes('w-full')
                pwd = ui.input('Mot de passe (123)', password=True).classes('w-full')
                ui.button('ACCÉDER', on_click=lambda: legal.login(email.value, pwd.value)).classes('w-full mt-6 py-4')
    
    else:
        # --- TABLEAU DE BORD (LE VRAI OUTIL) ---
        # 1. HEADER
        with ui.header().classes('items-center justify-between bg-slate-900 text-white p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('text-xl font-bold tracking-tight')
            ui.button(icon='logout', on_click=legal.logout, color='white').props('flat round')

        # 2. CONTENU PRINCIPAL
        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            
            # SIDEBAR STEPPER
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                with ui.stepper().props('vertical animated gray') as stepper:
                    # On force la valeur sur l'étape actuelle
                    stepper.value = legal.etapes[legal.etape_actuelle]
                    for nom in legal.etapes:
                        ui.step(nom)

            # ZONE DE TRAVAIL
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {legal.etape_actuelle + 1}').classes('text-xs font-bold text-primary tracking-widest')
                ui.label(legal.etapes[legal.etape_actuelle]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 shadow-xl bg-white border-t-4 border-primary'):
                    if legal.etape_actuelle == 0:
                        ui.label('Analyse factuelle du litige').classes('text-h6 mb-2 text-slate-700')
                        ui.textarea(label="Décrivez les faits ici...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label(f"Module {legal.etapes[legal.etape_actuelle]} prêt.").classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-32')

                # BOUTONS NAVIGATION
                with ui.row().classes('w-full mt-12 justify-between items-center'):
                    def move(step):
                        legal.etape_actuelle += step
                        ui.navigate.to('/') # Rafraîchit la vue
                    
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: move(-1)).props('flat').visible(legal.etape_actuelle > 0)
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: move(1)).props('elevated color=primary').visible(legal.etape_actuelle < 10)

# Lancement
ui.run(title='LegalOS - Karim Mabrouki', port=8080, reload=True)
