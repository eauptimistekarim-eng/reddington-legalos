from nicegui import ui
import asyncio

class KareemEngine:
    def __init__(self):
        self.user_authenticated = False
        self.step_index = 0
        self.steps = [
            "Qualification", "Objectif", "Base légale", "Preuves / Dossier", 
            "Analyse stratégique", "Phase amiable", "Choix de procédure", 
            "Rédaction juridique", "Audience", "Jugement", "Exécution / Recours"
        ]
        self.data = {i: "" for i in range(11)}
        self.ai_feedback = {i: "🏠 **Kareem :** Je suis prêt. Décrivez-moi votre situation ci-contre." for i in range(11)}
        self.analysis_done = False # Nouveau : pour contrôler l'affichage du bouton suivant

    def traduire_en_juridique(self, texte, index):
        t = texte.lower()
        if index == 0:
            if any(w in t for w in ["logement", "hlm", "loyer", "appart", "expulsion"]):
                self.data[2] = "Loi ELAN / Code de la construction et de l'habitation"
                return "🏠 **Kareem :** Analyse terminée. Il s'agit d'un litige de **Droit Immobilier**. \n\nNotion clé : *Droit au maintien dans les lieux*. J'ai préparé les textes pour l'étape 3."
            if any(w in t for w in ["patron", "viré", "salaire", "travail"]):
                self.data[2] = "Code du Travail - Article L1232-1"
                return "💼 **Kareem :** Analyse terminée. Dossier de **Droit du Travail**. \n\nNotion clé : *Licenciement abusif*. Nous allons monter une stratégie Reddington solide."
        
        return f"✅ **Kareem :** Analyse de la phase {self.steps[index]} validée. Vous pouvez passer à la suite."

    async def analyser_ia(self, index):
        if len(self.data[index]) < 5:
            ui.notify("Kareem : 'Détaillez un peu plus votre propos...'", color='warning')
            return
        
        self.analysis_done = False
        ui.notify("Kareem analyse...", icon='psychology')
        await asyncio.sleep(1) # Simulation de réflexion
        
        self.ai_feedback[index] = self.traduire_en_juridique(self.data[index], index)
        self.analysis_done = True # L'analyse est finie, on peut afficher le bouton
        ui.navigate.to('/') # On rafraîchit pour montrer le bouton "Suivant"

moteur = KareemEngine()

@ui.page('/')
def main():
    ui.colors(primary='#0f172a', secondary='#10b981')

    if not moteur.user_authenticated:
        # --- LOGIN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-80 p-8 shadow-2xl rounded-3xl'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-black text-center w-full mb-6')
                e = ui.input('Email').classes('w-full').props('outlined')
                p = ui.input('Pass', password=True).classes('w-full mt-2').props('outlined')
                ui.button('ACCÉDER', on_click=lambda: (setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')) 
                          if e.value == "admin@legalos.fr" and p.value == "123" else ui.notify('Erreur login')).classes('w-full mt-6 shadow-lg')
    else:
        # --- APP DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            ui.label('KAREEM IA | SYSTÈME FREEMAN').classes('font-bold text-white uppercase tracking-tighter')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-72 p-6 bg-white border-r overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-bold text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    def goto(idx=i): 
                        moteur.step_index = idx
                        moteur.analysis_done = False
                        ui.navigate.to('/')
                    active = (i == moteur.step_index)
                    style = 'bg-slate-900 text-white shadow-xl' if active else 'text-slate-400 hover:text-primary'
                    ui.button(f"{i+1}. {name}", on_click=goto).classes(f'w-full text-left justify-start p-3 rounded-xl mb-1 no-caps transition-all {style}').props('flat' if not active else '')

            # Workzone
            with ui.column().classes('flex-grow p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-10 rounded-full h-1.5')
                ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-black text-slate-800 mb-10 tracking-tighter')

                with ui.row().classes('w-full no-wrap gap-10 items-start'):
                    # Carte Saisie
                    with ui.card().classes('w-2/3 p-10 shadow-2xl rounded-3xl border-none'):
                        area = ui.textarea(placeholder="Parlez à Kareem...").classes('w-full h-72 text-lg').props('outlined rounded')
                        area.bind_value(moteur.data, moteur.step_index)
                        
                        with ui.row().classes('w-full justify-between mt-8'):
                            if moteur.step_index > 0:
                                ui.button('RETOUR', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/'))).props('flat color=slate-400')
                            else: ui.label('')
                            
                            # BOUTON ANALYSE
                            ui.button('LANCER L\'ANALYSE', on_click=lambda: moteur.analyser_ia(moteur.step_index)).classes('px-10 py-3 font-bold shadow-xl shadow-blue-100').props('color=primary rounded')

                    # Feedback Panel (KAREEM PARLE)
                    with ui.column().classes('w-1/3 gap-4'):
                        with ui.card().classes('w-full p-8 bg-slate-800 text-white rounded-3xl shadow-2xl border-l-8 border-secondary'):
                            ui.label('KAREEM IA').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest')
                            ui.markdown().bind_content_from(moteur.ai_feedback, moteur.step_index).classes('text-sm leading-relaxed')

                        # LE BOUTON "SUIVANT" APPARAÎT UNIQUEMENT APRÈS ANALYSE
                        if moteur.analysis_done and moteur.step_index < 10:
                            ui.button('ÉTAPE SUIVANTE ➔', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index + 1) or setattr(moteur, 'analysis_done', False) or ui.navigate.to('/'))).classes('w-full py-6 font-black shadow-2xl shadow-green-200 animate-bounce').props('color=secondary rounded')

ui.run(title='LegalOS', port=8088, reload=False)
