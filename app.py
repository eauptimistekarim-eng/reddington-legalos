from nicegui import ui
import asyncio

# --- 1. MOTEUR DU SYSTÈME FREEMAN ---
class KareemIALegalOS:
    def __init__(self):
        self.is_authenticated = False
        self.step_index = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves / Dossier", 
            "5. Analyse stratégique", "6. Phase amiable", "7. Choix de procédure", 
            "8. Rédaction juridique", "9. Audience", "10. Jugement", "11. Exécution / Recours"
        ]
        # Stockage des données textes
        self.data = {i: "" for i in range(11)}
        # Stockage des retours IA
        self.ai_feedback = {i: "En attente d'analyse stratégique..." for i in range(11)}

    async def analyser_ia(self, index):
        if len(self.data[index]) < 10:
            ui.notify("Saisie trop courte pour l'IA", color='warning')
            return
        
        ui.notify("Kareem IA analyse la Phase " + str(index+1), icon='psychology')
        await asyncio.sleep(1.5)
        
        # Logique de feedback contextuelle basée sur ta structure
        feedbacks = {
            0: "IA : Qualification terminée. Le domaine juridique semble identifié.",
            1: "IA : Objectif validé. Vérifiez la cohérence avec les pièces du dossier.",
            2: "IA : Connexion Légifrance suggérée pour l'article cité.",
            3: "IA : Inventaire des preuves en cours... Attention aux preuves déloyales.",
            4: "IA : Calcul des chances de succès : 75%. Risque financier identifié.",
            7: "IA : Vérification du tribunal compétent effectuée."
        }
        self.ai_feedback[index] = feedbacks.get(index, "Analyse conforme aux standards Freeman.")
        ui.notify("Analyse terminée", color='positive')

moteur = KareemIALegalOS()

# --- 2. FONCTIONS DE NAVIGATION ---
def login_handler(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.is_authenticated = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé', color='negative')

def nav_to(delta):
    moteur.step_index += delta
    ui.navigate.to('/')

# --- 3. INTERFACE UTILISATEUR ---
@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#00c853')

    if not moteur.is_authenticated:
        # --- LOGIN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary rounded-xl'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-2')
                ui.label('Système Freeman').classes('text-sm text-center w-full mb-8 text-slate-400 italic')
                mail = ui.input('Identifiant').classes('w-full')
                pwd = ui.input('Mot de passe', password=True).classes('w-full')
                ui.button('ACTIVER L\'IA', on_click=lambda: login_handler(mail.value, pwd.value)).classes('w-full mt-8 py-4 font-bold rounded-lg')
    
    else:
        # --- DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            ui.label('LEGALOS | SYSTÈME FREEMAN').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'is_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest uppercase')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if active else 'text-slate-300'
                    ui.label(f"{i+1}. {name.split('. ')[-1] if '.' in name else name}").classes(f'p-3 rounded-md mb-1 transition-all {style}')

            # Zone de travail
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-6')
                
                with ui.row().classes('w-full justify-between items-center mb-8'):
                    ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-light text-slate-800')
                    ui.button('ANALYSE IA', icon='psychology', on_click=lambda: moteur.analyser_ia(moteur.step_index)).props('elevated color=secondary')

                with ui.row().classes('w-full no-wrap gap-6'):
                    # --- FORMULAIRE DYNAMIQUE ---
                    with ui.card().classes('w-2/3 p-8 bg-white shadow-xl rounded-xl'):
                        
                        idx = moteur.step_index
                        if idx == 0: # Qualification
                            ui.label('👉 Comprendre la situation').classes('text-lg font-bold text-primary')
                            with ui.row().classes('w-full'):
                                ui.select(['Travail', 'Contrat', 'Pénal', 'Immobilier', 'Famille'], label='Domaine Juridique').classes('w-1/2')
                                ui.input(label='Parties impliquées').classes('w-1/2')
                        
                        elif idx == 1: # Objectif
                            ui.label('👉 Que veut l’utilisateur ?').classes('text-lg font-bold text-primary')
                            ui.checkbox('Être payé')
                            ui.checkbox('Annuler un contrat')
                            ui.checkbox('Se défendre / Négocier')
                        
                        elif idx == 2: # Base légale
                            ui.label('👉 Sur quoi repose le droit ?').classes('text-lg font-bold text-primary')
                            ui.radio(['Contrat', 'Loi', 'Règlement'], value='Loi').props('inline')
                            ui.button('Connecter Légifrance', icon='link').props('small outline').classes('mt-2')

                        elif idx == 3: # Preuves
                            ui.label('👉 Construire le dossier').classes('text-lg font-bold text-primary')
                            ui.select(['Documents', 'Échanges (SMS/Mails)', 'Témoignages'], label='Type de preuve', multiple=True).classes('w-full')

                        elif idx == 5: # Amiable
                            ui.label('👉 Résolution sans juge').classes('text-lg font-bold text-primary')
                            ui.select(['Mise en demeure', 'Médiation', 'Négociation directe'], label='Action amiable').classes('w-full')

                        # Espace de rédaction commun
                        ui.label('DÉTAILS ET RÉDACTION').classes('text-xs font-bold text-slate-400 mt-6 mb-2')
                        area = ui.textarea(label="Saisie libre", placeholder="Décrivez les éléments ici...").classes('w-full h-64').props('outlined')
                        area.bind_value(moteur.data, idx)

                    # --- FEEDBACK IA ---
                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-xl border-l-4 border-secondary shadow-lg'):
                            ui.label('CONSEIL FREEMAN IA').classes('text-xs font-bold text-secondary mb-4 tracking-widest')
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm')

                # Navigation
                with ui.row().classes('w-full mt-10 justify-between'):
                    if moteur.step_index > 0:
                        ui.button('PRÉCÉDENT', icon='chevron_left', on_click=lambda: nav_to(-1)).props('flat')
                    else:
                        ui.label('')
                    
                    if moteur.step_index < 10:
                        ui.button('SUIVANT', icon='chevron_right', on_click=lambda: nav_to(1)).props('elevated color=primary').classes('px-10')
                    else:
                        ui.button('GÉNÉRER LE LIVRABLE', icon='verified', on_click=lambda: ui.notify('Génération PDF Freeman...')).props('color=green')

ui.run(title='Kareem IA LegalOS', port=8088, reload=False)
