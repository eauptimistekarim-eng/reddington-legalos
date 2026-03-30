from nicegui import ui

# --- 1. MOTEUR DE L'APPLICATION ---
class KareemIALegalOS:
    def __init__(self):
        self.is_authenticated = False
        self.step_index = 0
        # Tes 11 étapes de la méthode Reddington
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]
        # Dictionnaire pour stocker les données saisies par l'utilisateur
        self.data = {i: "" for i in range(11)}

# Instance globale
moteur = KareemIALegalOS()

# --- 2. ACTIONS DE NAVIGATION ---
def login_handler(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.is_authenticated = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé : Identifiants incorrects', color='negative')

def logout_handler():
    moteur.is_authenticated = False
    ui.navigate.to('/')

def nav_to(delta):
    moteur.step_index += delta
    ui.navigate.to('/')

# --- 3. INTERFACE UTILISATEUR ---
@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#42a5f5')

    if not moteur.is_authenticated:
        # --- ÉCRAN DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-2 text-slate-800')
                ui.label('Bienvenue sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 italic text-slate-500')
                
                email = ui.input('Email').classes('w-full')
                password = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER AU SYSTÈME', on_click=lambda: login_handler(email.value, password.value)).classes('w-full mt-6 py-4 font-bold')
    
    else:
        # --- TABLEAU DE BORD (L'OUTIL FINAL) ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white tracking-tight')
            with ui.row().classes('items-center'):
                ui.label('Expert : Karim Mabrouki').classes('text-xs text-slate-400 mr-4 uppercase tracking-widest')
                ui.button(icon='logout', on_click=logout_handler).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR : La Progression Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                
                for i, name in enumerate(moteur.steps):
                    is_active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if is_active else 'text-slate-300'
                    with ui.row().classes(f'w-full p-3 rounded-l-md transition-all {style}'):
                        ui.label(f"{'➔' if is_active else '○'} {name}").classes('text-sm')

            # ZONE DE TRAVAIL CENTRALE
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.label(f'PHASE {moteur.step_index + 1} / 11').classes('text-primary font-bold text-xs tracking-widest uppercase')
                ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-light mb-10 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    # LOGIQUE D'AFFICHAGE SELON L'ÉTAPE
                    current_title = moteur.steps[moteur.step_index]
                    ui.label(f"Instruction : {current_title}").classes('text-xl mb-4 text-slate-700 font-medium')
                    
                    # On crée un champ de saisie qui garde les données en mémoire
                    placeholder_text = f"Saisissez les éléments relatifs à la phase {current_title}..."
                    area = ui.textarea(label="Données du dossier", placeholder=placeholder_text).classes('w-full h-80').props('outlined')
                    area.bind_value(moteur.data, moteur.step_index) # Sauvegarde automatique pendant la navigation

                # BARRE DE NAVIGATION BASSE
                with ui.row().classes('w-full mt-12 justify-between items-center'):
                    if moteur.step_index > 0:
                        ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: nav_to(-1)).props('flat color=primary')
                    else:
                        ui.label('') # Espaceur

                    ui.label(f'Progression : {int((moteur.step_index + 1)/11*100)}%').classes('text-slate-400 font-mono text-xs')

                    if moteur.step_index < 10:
                        ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: nav_to(1)).props('elevated color=primary').classes('px-8')
                    else:
                        ui.button('FINALISER LE DOSSIER', icon='check_circle', on_click=lambda: ui.notify('Dossier prêt pour extraction !', color='positive')).props('elevated color=green').classes('px-8')

# LANCEMENT
ui.run(title='Kareem IA LegalOS', port=8088, reload=False)
