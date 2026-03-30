from nicegui import ui

class LegalOS_Final:
    def __init__(self):
        self.est_authentifie = False
        self.etape_actuelle = 0
        self.etapes = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

# Instance unique
moteur = LegalOS_Final()

def connexion(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.est_authentifie = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé', color='negative')

def deconnexion():
    moteur.est_authentifie = False
    ui.navigate.to('/')

def naviguer(delta):
    moteur.etape_actuelle += delta
    ui.navigate.to('/')

@ui.page('/')
def main_ui():
    ui.colors(primary='#1a237e')

    # Utilisation d'une vérification de valeur simple (pas d'appel de fonction)
    if not moteur.est_authentifie:
        # --- PAGE DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2')
                ui.label('Bienvenue Sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 italic text-slate-500')
                
                email = ui.input('Email').classes('w-full')
                password = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER', on_click=lambda: connexion(email.value, password.value)).classes('w-full mt-6 py-4')
    
    else:
        # --- DASHBOARD (L'OUTIL COMPLET) ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=deconnexion).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar : La Méthode Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                
                for i, nom in enumerate(moteur.etapes):
                    actif = (i == moteur.etape_actuelle)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if actif else 'text-slate-300'
                    with ui.row().classes(f'w-full p-2 rounded-l-md {style}'):
                        ui.label(f"{'➔' if actif else '○'} {nom}")

            # Zone de travail centrale
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {moteur.etape_actuelle + 1}').classes('text-primary font-bold text-xs tracking-widest')
                ui.label(moteur.etapes[moteur.etape_actuelle]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if moteur.etape_actuelle == 0:
                        ui.label('Analyse et Qualification').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Décrivez les faits ici...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label(f'Module {moteur.etapes[moteur.etape_actuelle]} prêt.').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-40 mt-4')

                # BOUTONS DE NAVIGATION (Correction de l'erreur 500)
                with ui.row().classes('w-full mt-12 justify-between'):
                    # Au lieu de .visible(), on utilise un if Python standard pour ne pas créer de conflit de type
                    if moteur.etape_actuelle > 0:
                        ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: naviguer(-1)).props('flat')
                    else:
                        ui.label('') # Espaceur
                        
                    if moteur.etape_actuelle < 10:
                        ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: naviguer(1)).props('elevated color=primary')

# Lancement sur un port neutre
ui.run(title='Kareem IA LegalOS', port=8088)
