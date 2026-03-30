from nicegui import ui
import asyncio

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
        # Stockage des données saisies (textes)
        self.data = {i: "" for i in range(11)}
        # Stockage des retours de l'IA
        self.ai_feedback = {i: "En attente d'analyse..." for i in range(11)}

    async def analyser_ia(self, index):
        """Simule l'intelligence juridique de Kareem IA"""
        texte_utilisateur = self.data[index]
        
        if len(texte_utilisateur) < 15:
            ui.notify("Veuillez saisir plus de détails pour l'analyse.", color='warning')
            return

        ui.notify("Kareem IA traite les données...", icon='psychology')
        await asyncio.sleep(2) # Simulation de réflexion réseau/IA
        
        # Réponses contextuelles simulées selon l'étape
        reponses = {
            0: "Analyse Qualification : Les faits sont identifiés. Vérifiez si la prescription n'est pas acquise.",
            1: "Conseil Objectif : La demande est chiffrable. Avez-vous inclus les frais d'article 700 ?",
            2: "Base Légale : Le fondement semble correct. Citez également l'article 9 du CPC sur la preuve.",
            3: "Preuves : L'IA suggère d'ajouter une attestation de témoin (Cerfa 11527*03).",
            7: "Rédaction : Attention aux termes trop émotionnels. Restez factuel et juridique.",
        }
        
        self.ai_feedback[index] = reponses.get(index, "Analyse terminée : Le contenu est conforme à la stratégie Reddington.")
        ui.notify("Analyse terminée", color='positive')

# Instance unique pour gérer l'état de l'application
moteur = KareemIALegalOS()

# --- 2. FONCTIONS DE CONTRÔLE ---
def login_handler(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.is_authenticated = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé : Identifiants incorrects', color='negative', icon='lock')

def nav_to(delta):
    moteur.step_index += delta
    ui.navigate.to('/')

# --- 3. INTERFACE UTILISATEUR (UI) ---
@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#00c853', accent='#ffd600')

    if not moteur.is_authenticated:
        # --- ÉCRAN DE CONNEXION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary rounded-xl'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-2 text-slate-800')
                ui.label('Bienvenue sur Kareem IA').classes('text-sm text-center w-full mb-8 text-slate-400 italic')
                
                email = ui.input('Email (admin@legalos.fr)').classes('w-full').props('outlined')
                password = ui.input('Mot de passe (123)', password=True).classes('w-full mt-2').props('outlined')
                
                ui.button('ACTIVER SYSTÈME FREEMAN', on_click=lambda: login_handler(email.value, password.value)).classes('w-full mt-8 py-4 font-bold rounded-lg shadow-lg')
    
    else:
        # --- TABLEAU DE BORD PRINCIPAL ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            with ui.row().classes('items-center'):
                ui.icon('balance', color='white').classes('text-2xl mr-2')
                ui.label('LEGALOS | SYSTÈME FREEMAN').classes('font-bold text-xl text-white tracking-tighter')
            
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'is_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            
            # SIDEBAR : Navigation Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest uppercase')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if active else 'text-slate-300'
                    ui.label(f"{'➔' if active else '○'} {name}").classes(f'p-3 rounded-md mb-1 transition-all {style}')

            # ZONE DE TRAVAIL CENTRALE (L'IA et la Saisie)
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                # Barre de progression visuelle
                ui.linear_progress(value=(moteur.step_index + 1) / 11, show_value=False).classes('mb-6 rounded-full h-2 shadow-sm')
                
                with ui.row().classes('w-full justify-between items-center mb-8'):
                    with ui.column():
                        ui.label(f'PHASE {moteur.step_index + 1}').classes('text-primary font-bold text-xs tracking-widest uppercase')
                        ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-light text-slate-800')
                    
                    # Bouton d'analyse IA
                    ui.button('ANALYSER AVEC KAREEM IA', icon='psychology', 
                              on_click=lambda: moteur.analyser_ia(moteur.step_index)).props('elevated color=secondary').classes('px-6 py-2 shadow-lg')

                with ui.row().classes('w-full no-wrap gap-6'):
                    # Zone de saisie principale
                    with ui.card().classes('w-2/3 p-8 bg-white shadow-xl rounded-xl border-none'):
                        ui.label('VOTRE RÉDACTION JURIDIQUE').classes('text-xs font-bold text-slate-400 mb-4 tracking-widest')
                        area = ui.textarea(label="Notes du dossier", placeholder="Saisissez ici les éléments de cette phase...").classes('w-full h-96 text-lg').props('outlined')
                        area.bind_value(moteur.data, moteur.step_index)

                    # Panneau de Feedback IA
                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-xl shadow-2xl border-l-4 border-secondary'):
                            ui.label('CONSEILS KAREEM IA').classes('text-xs font-bold text-secondary mb-4 tracking-widest')
                            # Liaison dynamique du feedback
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm leading-relaxed')

                # BARRE DE NAVIGATION BASSE
                with ui.row().classes('w-full mt-10 justify-between items-center'):
                    if moteur.step_index > 0:
                        ui.button('ÉTAPE PRÉCÉDENTE', icon='chevron_left', on_click=lambda: nav_to(-1)).props('flat color=primary')
                    else:
                        ui.label('') # Espaceur

                    if moteur.step_index < 10:
                        ui.button('ÉTAPE SUIVANTE', icon='chevron_right', on_click=lambda: nav_to(1)).props('elevated color=primary').classes('px-12 py-3 shadow-md')
                    else:
                        ui.button('GÉNÉRER LE DOSSIER FINAL', icon='verified', on_click=lambda: ui.notify('Génération du PDF...')).props('elevated color=green').classes('px-12 py-3 shadow-lg scale-105')

# LANCEMENT SUR LE PORT 8088
ui.run(title='Kareem IA LegalOS', port=8088, reload=False)
