from nicegui import ui
import json

# --- 1. MOTEUR DE L'APPLICATION ---
class KareemIALegalOS:
    def __init__(self):
        self.is_authenticated = False
        self.step_index = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]
        # Stockage des données (Persistance locale pendant la session)
        self.data = {i: "" for i in range(11)}

    def export_dossier(self):
        # Simulation d'exportation (Peut être lié à un PDF plus tard)
        print("Exportation du dossier Reddington...")
        ui.notify('Dossier compilé avec succès ! Téléchargement prêt.', color='positive', icon='download')

moteur = KareemIALegalOS()

# --- 2. ACTIONS ---
def login_handler(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.is_authenticated = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé', color='negative', icon='warning')

def nav_to(delta):
    # Sauvegarde visuelle avant de changer
    moteur.step_index += delta
    ui.navigate.to('/')

# --- 3. INTERFACE ---
@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#42a5f5', accent='#00c853')

    if not moteur.is_authenticated:
        # --- ÉCRAN DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-2 text-slate-800')
                ui.label('Bienvenue sur Kareem IA').classes('text-sm text-center w-full mb-8 text-slate-500 italic')
                
                email = ui.input('Identifiant').classes('w-full').props('outlined')
                password = ui.input('Code Accès', password=True).classes('w-full').props('outlined')
                
                ui.button('ACTIVER SYSTÈME FREEMAN', on_click=lambda: login_handler(email.value, password.value)).classes('w-full mt-6 py-4 font-bold shadow-lg')
    
    else:
        # --- TABLEAU DE BORD FINAL ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            with ui.row().classes('items-center'):
                ui.icon('balance', color='white').classes('text-2xl mr-2')
                ui.label('LEGALOS | SYSTÈME FREEMAN').classes('font-bold text-xl text-white tracking-tighter')
            
            with ui.row().classes('items-center gap-4'):
                ui.badge(f'Phase {moteur.step_index + 1}/11', color='primary').classes('p-2 text-xs')
                ui.button(icon='logout', on_click=lambda: setattr(moteur, 'is_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR : Méthode Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                
                for i, name in enumerate(moteur.steps):
                    is_active = (i == moteur.step_index)
                    is_done = (moteur.data[i] != "")
                    
                    with ui.row().classes(f'w-full p-3 rounded-md mb-1 transition-all {"bg-blue-50 border-l-4 border-primary text-primary" if is_active else "text-slate-400"}'):
                        ui.icon('check_circle' if is_done else 'radio_button_unchecked').classes('mr-2')
                        ui.label(name).classes('text-sm font-medium')

            # ZONE DE TRAVAIL
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                # Barre de progression en haut
                progress = (moteur.step_index + 1) / 11
                ui.linear_progress(value=progress, show_value=False).classes('mb-6 rounded-full h-2 shadow-sm')

                with ui.row().classes('justify-between items-end w-full mb-8'):
                    with ui.column():
                        ui.label(f'Dossier en cours : Reddington-2026').classes('text-xs font-bold text-primary uppercase')
                        ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-light text-slate-800')
                    
                    # Bouton d'exportation visible partout mais mis en avant à la fin
                    ui.button('EXPORT PDF', icon='description', on_click=moteur.export_dossier).props('outline color=primary').classes('rounded-full')

                # Card de saisie principale
                with ui.card().classes('w-full p-8 bg-white shadow-2xl border-none rounded-xl'):
                    ui.label('SAISIE DES ÉLÉMENTS JURIDIQUES').classes('text-xs font-bold text-slate-400 mb-4')
                    
                    # On bind la valeur pour que rien ne se perde en changeant de page
                    area = ui.textarea(label="Analyse détaillée", placeholder="Saisissez ici les notes de la phase...").classes('w-full h-96 text-lg').props('outlined')
                    area.bind_value(moteur.data, moteur.step_index)

                # NAVIGATION BASSE
                with ui.row().classes('w-full mt-10 justify-between'):
                    ui.button('PRÉCÉDENT', icon='chevron_left', on_click=lambda: nav_to(-1)).props('flat').visible(moteur.step_index > 0)
                    
                    if moteur.step_index < 10:
                        ui.button('PHASE SUIVANTE', icon='chevron_right', on_click=lambda: nav_to(1)).props('elevated color=primary').classes('px-10 py-2')
                    else:
                        ui.button('FINALISER ET ARCHIVER', icon='verified', on_click=moteur.export_dossier).props('elevated color=green').classes('px-10 py-2 shadow-lg scale-110 transition-transform')

# LANCEMENT
ui.run(title='Kareem IA LegalOS', port=8088, reload=False)
