from nicegui import ui

# --- STRUCTURE DE L'APPLICATION ---
class LegalOSApp:
    def __init__(self):
        # On utilise des noms de variables très explicites pour éviter tout conflit
        self.est_authentifie = False
        self.etape_index = 0
        self.liste_etapes = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

# Instance unique
app_data = LegalOSApp()

# --- ACTIONS ---
def valider_connexion(email, password):
    if email == "admin@legalos.fr" and password == "123":
        app_data.est_authentifie = True
        ui.navigate.to('/') # Recharge la page avec le nouvel état
    else:
        ui.notify('Email ou mot de passe incorrect', color='negative')

def quitter():
    app_data.est_authentifie = False
    ui.navigate.to('/')

def naviguer(direction):
    app_data.etape_index += direction
    ui.navigate.to('/')

# --- INTERFACE PRINCIPALE ---
@ui.page('/')
def build_ui():
    ui.colors(primary='#1a237e')

    # CONDITION DE CONNEXION (Syntaxe sécurisée)
    if app_data.est_authentifie == False:
        # --- ÉCRAN DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2 text-slate-800')
                ui.label('Bienvenue sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 italic text-slate-500')
                
                # Champs propres sans indications entre parenthèses
                champ_email = ui.input('Email').classes('w-full')
                champ_pass = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER AU SYSTÈME', 
                          on_click=lambda: valider_connexion(champ_email.value, champ_pass.value)
                ).classes('w-full mt-6 py-4 font-bold tracking-wide')
    
    else:
        # --- TABLEAU DE BORD (LES 11 ÉTAPES) ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=quitter).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar : Liste des étapes
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                
                for i, nom in enumerate(app_data.liste_etapes):
                    est_actif = (i == app_data.etape_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if est_actif else 'text-slate-400'
                    with ui.row().classes(f'w-full p-2 rounded-l-md {style}'):
                        ui.label(f"{'➔' if est_actif else '○'} {nom}")

            # Zone de travail centrale
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {app_data.etape_index + 1}').classes('text-primary font-bold text-xs tracking-widest')
                ui.label(app_data.liste_etapes[app_data.etape_index]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if app_data.etape_index == 0:
                        ui.label('Analyse et Qualification').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Décrivez les faits du litige ici...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label(f'Module {app_data.liste_etapes[app_data.etape_index]} prêt.').classes('italic text-slate-400 text-lg')
                        ui.skeleton().classes('w-full h-40 mt-4')

                # Boutons de navigation
                with ui.row().classes('w-full mt-12 justify-between items-center'):
                    ui.button('ÉTAPE PRÉCÉDENTE', icon='arrow_back', 
                              on_click=lambda: naviguer(-1)).props('flat').visible(app_data.etape_index > 0)
                    
                    ui.label(f'{app_data.etape_index + 1} / 11').classes('text-slate-300 font-mono')
                    
                    ui.button('ÉTAPE SUIVANTE', icon='arrow_forward', 
                              on_click=lambda: naviguer(1)).props('elevated color=primary').visible(app_data.etape_index < 10)

# LANCEMENT
ui.run(title='LegalOS - Kareem IA', port=8080, reload=True)
