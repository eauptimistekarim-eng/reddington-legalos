from nicegui import ui

# --- STRUCTURE DE L'OUTIL ---
class LegalOS_Engine:
    def __init__(self):
        self.connected = False  # Variable simple (pas une fonction)
        self.current_step = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

# Instance unique
engine = LegalOS_Engine()

# --- ACTIONS ---
def handle_login(e, p):
    if e == "admin@legalos.fr" and p == "123":
        engine.connected = True
        ui.navigate.to('/') # Redirection propre
    else:
        ui.notify('Accès refusé', color='negative')

def handle_logout():
    engine.connected = False
    ui.navigate.to('/')

def move(delta):
    engine.current_step += delta
    ui.navigate.to('/')

# --- INTERFACE ---
@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e')

    # VÉRIFICATION DE SÉCURITÉ (SANS PARENTHÈSES)
    if engine.connected == False:
        # --- PAGE DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2')
                ui.label('Bienvenue Sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 italic text-slate-500')
                
                user_mail = ui.input('Email').classes('w-full')
                user_pass = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER', on_click=lambda: handle_login(user_mail.value, user_pass.value)).classes('w-full mt-6 py-4')
    
    else:
        # --- TABLEAU DE BORD (LES 11 ÉTAPES) ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=handle_logout).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar : La Méthode Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(engine.steps):
                    is_active = (i == engine.current_step)
                    color = 'text-primary font-bold' if is_active else 'text-slate-300'
                    ui.label(f"{'➔' if is_active else '○'} {name}").classes(f'py-1 {color}')

            # Zone de travail centrale
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {engine.current_step + 1}').classes('text-primary font-bold text-xs tracking-widest')
                ui.label(engine.steps[engine.current_step]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if engine.current_step == 0:
                        ui.label('Analyse et Qualification').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Décrivez les faits ici...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label(f'Module {engine.steps[engine.current_step]} activé.').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-40 mt-4')

                # Boutons de navigation
                with ui.row().classes('w-full mt-12 justify-between'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: move(-1)).props('flat').visible(engine.current_step > 0)
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: move(1)).props('elevated color=primary').visible(engine.current_step < 10)

# LANCEMENT (Port 8081 pour éviter les conflits de cache)
ui.run(title='LegalOS', port=8081)
