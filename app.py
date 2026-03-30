from nicegui import ui

# --- 1. L'ÉTAT DU SYSTÈME (Simple et robuste) ---
class GlobalState:
    def __init__(self):
        self.is_connected = False
        self.current_step = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

state = GlobalState()

# --- 2. LES ACTIONS ---
def login_action(email, password):
    # Test simple : admin / 123
    if email == "admin@legalos.fr" and password == "123":
        state.is_connected = True
        ui.navigate.to('/')
    else:
        ui.notify('Email ou mot de passe incorrect', color='negative')

def logout_action():
    state.is_connected = False
    ui.navigate.to('/')

def move_to(delta):
    state.current_step += delta
    ui.navigate.to('/')

# --- 3. L'INTERFACE ---
@ui.page('/')
def main_page():
    ui.colors(primary='#1a237e')

    # CONDITION DE CONNEXION (SANS PARENTHÈSES)
    if state.is_connected == False:
        # --- ÉCRAN DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2')
                ui.label('Bienvenue sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 italic text-slate-500')
                
                email_input = ui.input('Email').classes('w-full')
                pass_input = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER', on_click=lambda: login_action(email_input.value, pass_input.value)).classes('w-full mt-6 py-4')
    
    else:
        # --- L'OUTIL (TABLEAU DE BORD) ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=logout_action).props('flat color=white text-xs')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Menu de gauche
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(state.steps):
                    is_active = (i == state.current_step)
                    color = 'text-primary font-bold' if is_active else 'text-slate-400'
                    ui.label(f"{'➔' if is_active else '○'} {name}").classes(f'py-1 {color}')

            # Zone de travail
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {state.current_step + 1}').classes('text-primary font-bold text-xs')
                ui.label(state.steps[state.current_step]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if state.current_step == 0:
                        ui.label('Analyse factuelle du litige').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Racontez les faits...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label(f'Module {state.steps[state.current_step]} prêt.').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-32')

                # Boutons de navigation
                with ui.row().classes('w-full mt-12 justify-between'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: move_to(-1)).props('flat').visible(state.current_step > 0)
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: move_to(1)).props('elevated color=primary').visible(state.current_step < 10)

# DÉMARRAGE
ui.run(title='LegalOS', port=8080)
