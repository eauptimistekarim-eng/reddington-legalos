from nicegui import ui

# --- ÉTAT DE L'APPLICATION ---
class State:
    authenticated = False
    step = 0
    steps = [
        "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
        "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
        "9. Audience", "10. Jugement", "11. Exécution"
    ]

app_state = State()

# --- FONCTIONS DE NAVIGATION ---
def login(email, pwd):
    if email == "admin@legalos.fr" and pwd == "123":
        app_state.authenticated = True
        ui.navigate.to('/') # Relance la page avec l'état True
    else:
        ui.notify('Accès refusé', color='negative')

def logout():
    app_state.authenticated = False
    ui.navigate.to('/')

def move(delta):
    app_state.step += delta
    ui.navigate.to('/')

# --- PAGE PRINCIPALE ---
@ui.page('/')
def main():
    ui.colors(primary='#1a237e')

    if not app_state.authenticated:
        # --- LOGIN SCREEN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-6')
                e = ui.input('Email (admin@legalos.fr)').classes('w-full')
                p = ui.input('Pass (123)', password=True).classes('w-full')
                ui.button('ACCÉDER', on_click=lambda: login(e.value, p.value)).classes('w-full mt-4 py-3')
    
    else:
        # --- DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4'):
            ui.label('LEGALOS | Système Freeman').classes('font-bold text-xl')
            ui.button(icon='logout', on_click=logout).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-4')
                for i, name in enumerate(app_state.steps):
                    color = 'text-primary font-bold' if i == app_state.step else 'text-slate-400'
                    ui.label(name).classes(color)

            # Workzone
            with ui.column().classes('w-3/4 p-10'):
                ui.label(f'ÉTAPE {app_state.step + 1}').classes('text-primary font-bold')
                ui.label(app_state.steps[app_state.step]).classes('text-4xl font-light mb-6')
                
                with ui.card().classes('w-full p-8 bg-white shadow-xl border-t-4 border-primary'):
                    if app_state.step == 0:
                        ui.textarea(label="Analyse des faits").classes('w-full h-64').props('outlined')
                    else:
                        ui.label('Module expert prêt.').classes('italic text-slate-400')
                        ui.skeleton().classes('w-full h-32')

                with ui.row().classes('w-full mt-8 justify-between'):
                    ui.button('PRÉCÉDENT', on_click=lambda: move(-1)).visible(app_state.step > 0)
                    ui.button('SUIVANT', on_click=lambda: move(1)).visible(app_state.step < 10)

ui.run(title='LegalOS', port=8080)
