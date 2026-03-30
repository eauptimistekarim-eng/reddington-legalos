from nicegui import ui

# --- 1. ÉTAT DE L'APPLICATION ---
class LegalState:
    def __init__(self):
        self.is_logged_in = False
        self.step_index = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

# Instance unique pour porter les données
state = LegalState()

# --- 2. LOGIQUE DE NAVIGATION ---
def login(email, password):
    # Identifiants simplifiés pour ton test
    if email == "admin@legalos.fr" and password == "123":
        state.is_logged_in = True
        ui.navigate.to('/') # Force le rafraîchissement propre
    else:
        ui.notify('Accès refusé : Identifiants incorrects', color='negative')

def logout():
    state.is_logged_in = False
    ui.navigate.to('/')

def change_step(delta):
    state.step_index += delta
    ui.navigate.to('/')

# --- 3. CONSTRUCTION DE LA PAGE ---
@ui.page('/')
def main_page():
    # Thème institutionnel
    ui.colors(primary='#1a237e', secondary='#42a5f5')

    if not state.is_logged_in:
        # --- ÉCRAN DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2 text-slate-800')
                ui.label('Bienvenue sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 text-slate-500 italic')
                
                email_input = ui.input('Email').classes('w-full')
                pass_input = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER AU SYSTÈME', on_click=lambda: login(email_input.value, pass_input.value)).classes('w-full mt-6 py-4 font-bold uppercase tracking-wide')
    
    else:
        # --- TABLEAU DE BORD (L'OUTIL RÉEL) ---
        # Header
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-md'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            with ui.row().classes('items-center'):
                ui.label('Mode Expert : Karim Mabrouki').classes('text-xs text-slate-400 mr-4')
                ui.button(icon='logout', on_click=logout).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar : La Méthode Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                
                for i, name in enumerate(state.steps):
                    active = (i == state.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if active else 'text-slate-400'
                    with ui.row().classes(f'w-full p-2 rounded-l-md {style}'):
                        ui.label(f"{'➔' if active else '○'} {name}")

            # Zone de travail centrale
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {state.step_index + 1}').classes('text-primary font-bold text-xs tracking-widest')
                ui.label(state.steps[state.step_index]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    # Contenu dynamique
                    if state.step_index == 0:
                        ui.label('Analyse factuelle et juridique').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Décrivez les faits ici de manière chronologique...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label(f'Le module {state.steps[state.step_index]} est prêt pour analyse.').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-32')

                # Navigation
                with ui.row().classes('w-full mt-12 justify-between items-center'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: change_step(-1)).props('flat').visible(state.step_index > 0)
                    ui.label(f'{state.step_index + 1} / 11').classes('text-slate-300 font-mono')
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: change_step(1)).props('elevated color=primary').visible(state.step_index < 10)

# Lancement du serveur
ui.run(title='LegalOS - Kareem IA', port=8080, reload=True)
