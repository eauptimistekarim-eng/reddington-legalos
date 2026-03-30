from nicegui import ui

# --- ÉTAT DE L'APPLICATION (Mécanique interne) ---
class ApplicationState:
    def __init__(self):
        self.is_authenticated = False
        self.current_step = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

# Instance unique pour garder les données en mémoire
state = ApplicationState()

# --- LOGIQUE DE NAVIGATION ---
def attempt_login(email, password):
    # Identifiants propres
    if email == "admin@legalos.fr" and password == "123":
        state.is_authenticated = True
        ui.navigate.to('/') # On recharge pour afficher le dashboard
    else:
        ui.notify('Accès refusé : Identifiants invalides', color='negative')

def handle_logout():
    state.is_authenticated = False
    ui.navigate.to('/')

def change_page(delta):
    state.current_step += delta
    ui.navigate.to('/')

# --- CONSTRUCTION DE L'INTERFACE ---
@ui.page('/')
def main_entry():
    # Couleurs institutionnelles (Banque/Droit)
    ui.colors(primary='#1a237e', secondary='#42a5f5')

    if not state.is_authenticated:
        # --- ÉCRAN DE CONNEXION (PROPRE) ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-6 text-slate-800')
                
                # Champs sans parenthèses pour un look propre
                user_input = ui.input('Email').classes('w-full')
                pass_input = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER', on_click=lambda: attempt_login(user_input.value, pass_input.value)).classes('w-full mt-6 py-4 font-bold')
    
    else:
        # --- TABLEAU DE BORD (SYSTÈME FREEMAN) ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=handle_logout).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Barre latérale : Méthode Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                
                # Liste visuelle des étapes
                for index, name in enumerate(state.steps):
                    is_active = (index == state.current_step)
                    color = 'text-primary font-bold' if is_active else 'text-slate-400'
                    icon = '➔ ' if is_active else '○ '
                    ui.label(f'{icon} {name}').classes(f'py-1 {color}')

            # Zone de travail centrale
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'ÉTAPE {state.current_step + 1}').classes('text-primary font-bold tracking-widest text-xs')
                ui.label(state.steps[state.current_step]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if state.current_step == 0:
                        ui.label('Instruction du Litige').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Décrivez ici la situation de manière chronologique...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label('Module en attente d\'instruction...').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-32')

                # Navigation entre les phases
                with ui.row().classes('w-full mt-12 justify-between'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: change_page(-1)).props('flat').visible(state.current_step > 0)
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: change_page(1)).props('elevated color=primary').visible(state.current_step < 10)

# Lancement du serveur
ui.run(title='LegalOS - Infrastructure', port=8080, reload=True)
