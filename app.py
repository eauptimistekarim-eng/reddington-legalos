from nicegui import ui

# --- ARCHITECTURE DE L'OUTIL ---
class LegalEngine:
    def __init__(self):
        # On n'utilise PAS le mot 'auth' ou 'login' pour éviter les conflits NiceGUI
        self.acces_autorise = False 
        self.page_index = 0
        self.phases = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

# Instance unique
moteur = LegalEngine()

# --- LOGIQUE ---
def verifier_identifiants(u, p):
    if u == "admin@legalos.fr" and p == "123":
        moteur.acces_autorise = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé', color='negative')

def sortir():
    moteur.acces_autorise = False
    ui.navigate.to('/')

def changer_phase(delta):
    moteur.page_index += delta
    ui.navigate.to('/')

# --- INTERFACE ---
@ui.page('/')
def interface_principale():
    ui.colors(primary='#1a237e')

    # ON VÉRIFIE LA VALEUR (PAS L'APPEL DE FONCTION)
    if moteur.acces_autorise == False:
        # --- CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2 text-slate-800')
                ui.label('Bienvenue Sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 italic text-slate-500')
                
                champ_u = ui.input('Email').classes('w-full')
                champ_p = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER AU SYSTÈME', 
                          on_click=lambda: verifier_identifiants(champ_u.value, champ_p.value)
                ).classes('w-full mt-6 py-4 font-bold uppercase')
    
    else:
        # --- TABLEAU DE BORD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-lg'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=sortir).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                for i, nom in enumerate(moteur.phases):
                    est_ici = (i == moteur.page_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if est_ici else 'text-slate-300'
                    with ui.row().classes(f'w-full p-2 rounded-l-md {style}'):
                        ui.label(f"{'➔' if est_ici else '○'} {nom}")

            # Zone de travail
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {moteur.page_index + 1}').classes('text-primary font-bold text-xs tracking-widest')
                ui.label(moteur.phases[moteur.page_index]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if moteur.page_index == 0:
                        ui.label('Instruction du Dossier').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Décrivez les faits ici...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label('Module expert prêt pour analyse.').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-40 mt-4')

                # Boutons
                with ui.row().classes('w-full mt-12 justify-between'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: changer_phase(-1)).props('flat').visible(moteur.page_index > 0)
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: changer_phase(1)).props('elevated color=primary').visible(moteur.page_index < 10)

# FORCE LE PORT 8085 (Pour tuer tout conflit de cache)
ui.run(title='LegalOS - Kareem IA', port=8085, reload=False)
