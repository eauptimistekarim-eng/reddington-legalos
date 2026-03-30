from nicegui import ui

# --- STRUCTURE DE DONNÉES ---
class LegalOS:
    def __init__(self):
        self.auth = False
        self.etape = 0
        self.etapes = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]

# Instance unique
app = LegalOS()

# --- LOGIQUE (SANS APPELS DE FONCTIONS SUR DES BOOLÉENS) ---
def tenter_connexion(e, p):
    if e == "admin@legalos.fr" and p == "123":
        app.auth = True
        ui.navigate.to('/')
    else:
        ui.notify('Email ou mot de passe incorrect', color='negative')

def deconnexion():
    app.auth = False
    ui.navigate.to('/')

def changer_page(direction):
    app.etape += direction
    ui.navigate.to('/')

# --- INTERFACE ---
@ui.page('/')
def main():
    ui.colors(primary='#1a237e')

    # Utilisation d'une comparaison simple pour éviter l'erreur "not callable"
    if app.auth == False:
        # --- LOGIN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-2')
                ui.label('Bienvenue sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 italic text-slate-500')
                
                mail = ui.input('Email').classes('w-full')
                pwd = ui.input('Mot de passe', password=True).classes('w-full')
                
                ui.button('ACCÉDER', on_click=lambda: tenter_connexion(mail.value, pwd.value)).classes('w-full mt-6 py-4 font-bold')
    
    else:
        # --- DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=deconnexion).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                for i, nom in enumerate(app.etapes):
                    actif = (i == app.etape)
                    couleur = 'text-primary font-bold' if actif else 'text-slate-400'
                    ui.label(f"{'➔' if actif else '○'} {nom}").classes(f'py-1 {couleur}')

            # Zone de travail
            with ui.column().classes('w-3/4 p-10 overflow-auto'):
                ui.label(f'PHASE {app.etape + 1}').classes('text-primary font-bold text-xs')
                ui.label(app.etapes[app.etape]).classes('text-4xl font-light mb-8 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if app.etape == 0:
                        ui.label('Instruction du Litige').classes('text-h6 mb-4')
                        ui.textarea(placeholder="Décrivez les faits ici...").classes('w-full h-64').props('outlined')
                    else:
                        ui.label('Module prêt pour analyse.').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-32')

                # Boutons
                with ui.row().classes('w-full mt-12 justify-between'):
                    ui.button('PRÉCÉDENT', icon='arrow_back', on_click=lambda: changer_page(-1)).props('flat').visible(app.etape > 0)
                    ui.button('SUIVANT', icon='arrow_forward', on_click=lambda: changer_page(1)).props('elevated color=primary').visible(app.etape < 10)

# LANCEMENT
ui.run(title='LegalOS', port=8080)
