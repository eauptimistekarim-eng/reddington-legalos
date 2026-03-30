from nicegui import ui

class KareemIALegalOS:
    def __init__(self):
        self.is_authenticated = False
        self.step_index = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]
        self.data = {i: "" for i in range(11)}

moteur = KareemIALegalOS()

def login_handler(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.is_authenticated = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé', color='negative')

def nav_to(delta):
    moteur.step_index += delta
    ui.navigate.to('/')

@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#42a5f5')

    if not moteur.is_authenticated:
        # --- LOGIN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-8')
                mail = ui.input('Identifiant').classes('w-full')
                pwd = ui.input('Code Accès', password=True).classes('w-full')
                ui.button('ACTIVER', on_click=lambda: login_handler(mail.value, pwd.value)).classes('w-full mt-6 py-4')
    
    else:
        # --- DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4'):
            ui.label('LEGALOS | SYSTÈME FREEMAN').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'is_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if active else 'text-slate-300'
                    ui.label(f"{'➔' if active else '○'} {name}").classes(f'p-3 rounded-md {style}')

            # Zone de travail
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-6')
                ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-light mb-10 text-slate-800')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl'):
                    area = ui.textarea(label="Analyse détaillée", placeholder="Saisissez vos notes...").classes('w-full h-80').props('outlined')
                    area.bind_value(moteur.data, moteur.step_index)

                # NAVIGATION (LA CORRECTION EST ICI)
                with ui.row().classes('w-full mt-10 justify-between'):
                    # On utilise un IF standard au lieu de .visible()
                    if moteur.step_index > 0:
                        ui.button('PRÉCÉDENT', icon='chevron_left', on_click=lambda: nav_to(-1)).props('flat')
                    else:
                        ui.label('') # Espaceur vide

                    if moteur.step_index < 10:
                        ui.button('SUIVANT', icon='chevron_right', on_click=lambda: nav_to(1)).props('elevated color=primary').classes('px-10')
                    else:
                        ui.button('EXPORT PDF', icon='check_circle', on_click=lambda: ui.notify('Dossier prêt !')).props('color=green')

ui.run(title='Kareem IA LegalOS', port=8088, reload=False)
