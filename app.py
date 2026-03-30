from nicegui import ui

# --- 1. MOTEUR DU SYSTÈME FREEMAN ---
class KareemIALegalOS:
    def __init__(self):
        self.is_authenticated = False
        self.step_index = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
            "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
            "9. Audience", "10. Jugement", "11. Exécution"
        ]
        # On initialise un stockage pour chaque champ de chaque étape
        self.data = {i: "" for i in range(11)}
        self.meta = {
            'obj_type': '',
            'loi_art': '',
            'preuves_list': [],
            'interlocuteur': ''
        }

# Instance unique
moteur = KareemIALegalOS()

# --- 2. ACTIONS ---
def login_handler(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.is_authenticated = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé', color='negative', icon='lock')

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
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary rounded-xl'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-2')
                ui.label('Bienvenue Sur Kareem IA LegalOS').classes('text-sm text-center w-full mb-8 text-slate-500 italic')
                
                email = ui.input('Email').classes('w-full').props('outlined')
                password = ui.input('Mot de passe', password=True).classes('w-full mt-2').props('outlined')
                
                ui.button('ACTIVER LE SYSTÈME', on_click=lambda: login_handler(email.value, password.value)).classes('w-full mt-8 py-4 font-bold rounded-lg shadow-lg')
    
    else:
        # --- TABLEAU DE BORD (SYSTÈME FREEMAN) ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            with ui.row().classes('items-center'):
                ui.icon('gavel', color='white').classes('text-2xl mr-2')
                ui.label('LEGALOS | SYSTÈME FREEMAN').classes('font-bold text-xl text-white tracking-tighter')
            
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'is_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR : Méthode Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary shadow-sm' if active else 'text-slate-300'
                    ui.label(f"{'➔' if active else '○'} {name}").classes(f'p-3 rounded-md mb-1 transition-all {style}')

            # ZONE DE TRAVAIL CENTRALE
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-6 rounded-full')
                
                with ui.row().classes('justify-between items-end w-full mb-8'):
                    with ui.column():
                        ui.label(f'PHASE {moteur.step_index + 1}').classes('text-primary font-bold text-xs tracking-widest')
                        ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-light text-slate-800')
                
                # --- CARD DYNAMIQUE SELON L'ÉTAPE ---
                with ui.card().classes('w-full p-8 bg-white shadow-xl rounded-xl border-none'):
                    
                    if moteur.step_index == 0: # Qualification
                        ui.label('Instruction du Litige').classes('text-xl font-bold mb-4')
                        area = ui.textarea(label="Faits marquants", placeholder="Qui, quoi, quand, où ?").classes('w-full h-64').props('outlined')
                        area.bind_value(moteur.data, 0)

                    elif moteur.step_index == 1: # Objectif
                        ui.label('Cible du Dossier').classes('text-xl font-bold mb-4')
                        ui.select(['Dommages-Intérêts', 'Rupture de Contrat', 'Mise en demeure', 'Référé'], label="Type d'action").classes('w-full mb-4').bind_value(moteur.meta, 'obj_type')
                        area = ui.textarea(label="Détail du résultat attendu").classes('w-full h-40').props('outlined')
                        area.bind_value(moteur.data, 1)

                    elif moteur.step_index == 2: # Base légale
                        ui.label('Fondement Juridique').classes('text-xl font-bold mb-4')
                        ui.input(label="Articles (ex: Art. 1240 Code Civil)").classes('w-full mb-4').bind_value(moteur.meta, 'loi_art').props('outlined')
                        area = ui.textarea(label="Jurisprudence de référence").classes('w-full h-40').props('outlined')
                        area.bind_value(moteur.data, 2)

                    elif moteur.step_index == 3: # Preuves
                        ui.label('Inventaire Probatoire').classes('text-xl font-bold mb-4')
                        with ui.row().classes('gap-4 mb-4'):
                            ui.checkbox('Contrats').bind_value(moteur.meta, 'p1')
                            ui.checkbox('E-mails').bind_value(moteur.meta, 'p2')
                            ui.checkbox('Témoignages').bind_value(moteur.meta, 'p3')
                        area = ui.textarea(label="Analyse des pièces").classes('w-full h-40').props('outlined')
                        area.bind_value(moteur.data, 3)

                    elif moteur.step_index == 7: # Rédaction
                        ui.label('Génération du Document').classes('text-xl font-bold mb-4')
                        ui.markdown('**Mode :** Rédaction assistée activée.')
                        area = ui.textarea(label="Corps du texte juridique").classes('w-full h-80').props('outlined')
                        area.bind_value(moteur.data, 7)

                    else: # Toutes les autres étapes (Générique)
                        ui.label(f'Détails : {moteur.steps[moteur.step_index]}').classes('text-xl font-bold mb-4')
                        area = ui.textarea(label="Notes et observations").classes('w-full h-64').props('outlined')
                        area.bind_value(moteur.data, moteur.step_index)

                # --- NAVIGATION BASSE ---
                with ui.row().classes('w-full mt-10 justify-between items-center'):
                    if moteur.step_index > 0:
                        ui.button('PRÉCÉDENT', icon='chevron_left', on_click=lambda: nav_to(-1)).props('flat')
                    else:
                        ui.label('')

                    if moteur.step_index < 10:
                        ui.button('PHASE SUIVANTE', icon='chevron_right', on_click=lambda: nav_to(1)).props('elevated color=primary').classes('px-10 py-2 shadow-md')
                    else:
                        ui.button('GÉNÉRER LE RAPPORT FINAL', icon='verified', on_click=lambda: ui.notify('Génération PDF...', color='positive')).props('elevated color=green').classes('px-10 py-2 shadow-lg scale-110')

# LANCEMENT SUR PORT 8088
ui.run(title='Kareem IA LegalOS', port=8088, reload=False)
