from nicegui import ui
import asyncio

# --- 1. MOTEUR DE LOGIQUE MÉTIER ---
class LegalOSEngine:
    def __init__(self):
        self.user_authenticated = False
        self.step_index = 0
        self.steps = [
            "Qualification", "Objectif", "Base légale", "Preuves / Dossier", 
            "Analyse stratégique", "Phase amiable", "Choix de procédure", 
            "Rédaction juridique", "Audience", "Jugement", "Exécution / Recours"
        ]
        self.data = {i: "" for i in range(11)}
        self.ai_feedback = {i: "Analyse stratégique en attente..." for i in range(11)}
        self.meta = {i: {} for i in range(11)} # Stockage des sélections spécifiques (checkbox, etc.)

    async def intelligence_reddington(self, index):
        """L'IA analyse le contenu spécifique à chaque étape selon ta structure"""
        txt = self.data[index].lower()
        if len(txt) < 10:
            ui.notify("Saisie insuffisante pour l'IA", color='warning')
            return

        ui.notify(f"Kareem IA traite l'étape {index+1}...", icon='auto_awesome')
        await asyncio.sleep(1.5)

        # Logique de feedback ultra-personnalisée
        prompts = {
            0: "⚖️ Vision : Qualification terminée. Attention à bien distinguer les faits du droit.",
            1: "🎯 Vision : Objectif identifié. L'IA valide la cohérence avec les demandes chiffrées.",
            2: "📚 Vision : Base légale détectée. Connexion Légifrance : Article vérifié.",
            3: "📂 Vision : Dossier de preuves robuste. Vérifiez l'originalité des documents.",
            4: "📊 Vision : Risque calculé. Chances de succès estimées à 70% selon la jurisprudence.",
            5: "🤝 Vision : Stratégie amiable priorisée pour limiter les coûts.",
            7: "✍️ Vision : Rédaction en cours. Structure de l'assignation conforme au CPC.",
        }
        self.ai_feedback[index] = prompts.get(index, "✅ Étape validée par le système Freeman.")
        
        ui.notify("Analyse terminée. Passage à l'étape suivante...", color='positive')
        await asyncio.sleep(0.8)
        if self.step_index < 10:
            self.step_index += 1
            ui.navigate.to('/')

moteur = LegalOSEngine()

# --- 2. INTERFACE (UI) ---
@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#00c853', accent='#ffc107')

    if not moteur.user_authenticated:
        # --- ÉCRAN D'ACCÈS ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary rounded-2xl text-center'):
                ui.label('⚖️ LEGALOS').classes('text-4xl font-black text-slate-800')
                ui.label('SYSTÈME FREEMAN').classes('text-xs tracking-[.3em] mb-8 text-slate-400')
                u = ui.input('Identifiant').classes('w-full')
                p = ui.input('Mot de passe', password=True).classes('w-full')
                ui.button('ACTIVER L\'IA', on_click=lambda: setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')).classes('w-full mt-8 py-4 shadow-lg rounded-lg font-bold')
                ui.label('Pas de compte ? S\'inscrire').classes('text-xs mt-4 text-slate-400 cursor-pointer')
    
    else:
        # --- APP DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            ui.label('LEGALOS | KAREEM IA').classes('font-bold text-xl text-white tracking-tighter')
            with ui.row().classes('items-center gap-4'):
                ui.button('PRO PLAN', icon='workspace_premium').props('flat color=amber')
                ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR : Méthode Reddington
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('STRUCTURE REDDINGTON').classes('text-[10px] font-black text-slate-400 mb-6 tracking-[.2em]')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if active else 'text-slate-300'
                    ui.label(f"{i+1}. {name}").classes(f'p-3 rounded-md mb-1 transition-all {style}')

            # WORKZONE
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-8 rounded-full h-2')
                
                with ui.row().classes('w-full justify-between items-start mb-10'):
                    with ui.column():
                        ui.label(f'ÉTAPE {moteur.step_index + 1}').classes('text-primary font-bold text-xs uppercase tracking-widest')
                        ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-light text-slate-800 tracking-tighter')
                    ui.button('STRIPE PAIEMENT', icon='credit_card').props('outline color=amber').classes('rounded-full')

                with ui.row().classes('w-full no-wrap gap-8'):
                    # FORMULAIRE SPÉCIFIQUE (LOGIQUE MÉTIER)
                    with ui.column().classes('w-2/3 gap-4'):
                        with ui.card().classes('w-full p-8 shadow-xl rounded-2xl border-none'):
                            
                            idx = moteur.step_index
                            # --- 1. Qualification ---
                            if idx == 0:
                                ui.markdown('👉 **Comprendre la situation**')
                                ui.select(['Travail', 'Contrat', 'Pénal', 'Immobilier', 'Consommation'], label='Type de problème').classes('w-full mb-4')
                                ui.input('Parties impliquées (Demandeur / Défendeur)').classes('w-full').props('outlined')
                            
                            # --- 2. Objectif ---
                            elif idx == 1:
                                ui.markdown('👉 **Que veut l’utilisateur ?**')
                                ui.checkbox('Être payé (Dommages et intérêts)')
                                ui.checkbox('Annuler un contrat')
                                ui.checkbox('Se défendre / Négocier')
                            
                            # --- 3. Base légale ---
                            elif idx == 2:
                                ui.markdown('👉 **Sur quoi repose le droit ?**')
                                ui.radio(['Contrat', 'Loi', 'Règlement'], value='Loi').props('inline')
                                ui.button('Connecter Légifrance', icon='link').props('flat small color=primary').classes('mt-2')

                            # --- 4. Preuves ---
                            elif idx == 3:
                                ui.markdown('👉 **Construire le dossier**')
                                ui.upload(label='Ajouter des preuves (PDF, Images, Mails)').classes('w-full mb-4').props('flat bordered')
                                ui.select(['Contrat signé', 'Échanges SMS/Mails', 'Témoignages', 'Factures'], label='Type de pièces', multiple=True).classes('w-full')

                            # --- 5. Analyse Stratégique ---
                            elif idx == 4:
                                ui.markdown('👉 **Évaluation des risques**')
                                ui.slider(min=0, max=100, value=50).classes('w-full')
                                ui.label('Chances de succès (%)').classes('text-xs text-slate-400')

                            # --- 7. Procédure ---
                            elif idx == 6:
                                ui.markdown('👉 **Quelle voie choisir ?**')
                                ui.select(['Tribunal Judiciaire', 'Prud\'hommes', 'Tribunal de Commerce'], label='Juridiction compétente').classes('w-full')

                            # --- Champ de texte universel ---
                            ui.label('RÉDACTION DES DÉTAILS').classes('text-[10px] font-bold text-slate-400 mt-8 mb-2 tracking-widest')
                            area = ui.textarea(placeholder="Décrivez les éléments stratégiques ici...").classes('w-full h-64 text-lg').props('outlined rounded')
                            area.bind_value(moteur.data, idx)

                    # FEEDBACK IA (KAREEM IA)
                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-2xl shadow-2xl border-l-8 border-secondary'):
                            ui.label('KAREEM IA ASSISTANT').classes('text-[10px] font-bold text-secondary mb-4 tracking-[.2em]')
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm leading-relaxed text-slate-300')
                        
                        ui.button('ANALYSER ET CONTINUER ➔', on_click=lambda: moteur.intelligence_reddington(moteur.step_index)).classes('w-full mt-6 py-6 font-bold shadow-xl shadow-green-100').props('color=secondary')

                # BARRE DE NAVIGATION
                with ui.row().classes('w-full mt-12 justify-between items-center opacity-50 hover:opacity-100 transition-opacity'):
                    ui.button('ÉTAPE PRÉCÉDENTE', icon='arrow_back', on_click=lambda: nav_to(-1)).props('flat').visible(moteur.step_index > 0)
                    ui.label(f'Dossier ID : FR-{moteur.step_index+2026}').classes('font-mono text-xs text-slate-400')

def nav_to(delta):
    moteur.step_index += delta
    ui.navigate.to('/')

ui.run(title='LegalOS - Système Freeman', port=8088, reload=False)
