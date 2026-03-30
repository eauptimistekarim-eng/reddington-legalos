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
        self.ai_feedback = {i: "Kareem IA : Posez vos valises ici, je vous écoute." for i in range(11)}

    def traduire_en_juridique(self, texte, index):
        t = texte.lower()
        
        # --- LOGIQUE DE TRADUCTION PAR ÉTAPE ---
        if index == 0: # Qualification
            if any(w in t for w in ["logement social", "hlm", "loyer", "appart"]):
                self.data[2] = "Loi n° 2018-1021 (Loi ELAN) / Code de la construction"
                return "🏠 **Kareem :** Je vois, c'est un litige lié au **Droit du Logement**. En droit, on parle de 'Droit au logement opposable' (DALO) si votre demande est urgente. J'ai préparé les textes de loi pour l'étape 3."
            
            if any(w in t for w in ["patron", "viré", "boulot", "salaire"]):
                self.data[2] = "Code du Travail - Article L1232-1"
                return "💼 **Kareem :** C'est du **Droit du Travail**. On va analyser s'il s'agit d'un licenciement 'sans cause réelle et sérieuse'. Respirez, on va construire un dossier solide."
            
            if any(w in t for w in ["argent", "prêt", "rembourser"]):
                self.data[2] = "Code Civil - Article 1103"
                return "💸 **Kareem :** On entre dans le **Droit des Obligations**. Le principe est simple : les contrats légalement formés font loi entre ceux qui les ont faits."

        return f"✅ **Kareem :** Bien reçu. C'est noté pour la phase {self.steps[index]}. Continuons la méthode Reddington."

    async def analyser_ia(self, index):
        if len(self.data[index]) < 5:
            ui.notify("Kareem : 'Dites-m'en un peu plus...'", color='warning')
            return
        
        ui.notify("Kareem IA analyse...", icon='psychology')
        await asyncio.sleep(1.2)
        
        # On fait parler l'IA
        self.ai_feedback[index] = self.traduire_en_juridique(self.data[index], index)
        ui.notify("Analyse terminée", color='positive')
        
        # On attend un peu pour que l'utilisateur lise avant de changer d'étape
        await asyncio.sleep(2) 
        if self.step_index < 10:
            self.step_index += 1
            ui.navigate.to('/')

moteur = KareemEngine()

@ui.page('/')
def main():
    ui.colors(primary='#0f172a', secondary='#10b981')

    if not moteur.user_authenticated:
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-80 p-8 shadow-2xl rounded-3xl'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-4')
                ui.label('SYSTÈME FREEMAN').classes('text-[10px] text-center w-full mb-6 text-slate-400 tracking-widest')
                e = ui.input('Email').classes('w-full').props('outlined')
                p = ui.input('Pass', password=True).classes('w-full mt-2').props('outlined')
                ui.button('ACCÉDER À KAREEM', on_click=lambda: (setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')) 
                          if e.value == "admin@legalos.fr" and p.value == "123" else ui.notify('admin@legalos.fr / 123')).classes('w-full mt-6 shadow-lg')
    else:
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            ui.label('KAREEM IA | SYSTÈME FREEMAN').classes('font-bold text-white')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-72 p-6 bg-white border-r overflow-y-auto shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-bold text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    def goto(idx=i): 
                        moteur.step_index = idx
                        ui.navigate.to('/')
                    active = (i == moteur.step_index)
                    btn_style = 'bg-slate-900 text-white shadow-xl scale-105' if active else 'text-slate-400 hover:text-primary'
                    ui.button(f"{i+1}. {name}", on_click=goto).classes(f'w-full text-left justify-start p-3 rounded-xl mb-1 no-caps transition-all {btn_style}').props('flat' if not active else '')

            # Workzone
            with ui.column().classes('flex-grow p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-10 rounded-full h-1.5')
                
                ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-black text-slate-800 mb-10 tracking-tighter')

                with ui.row().classes('w-full no-wrap gap-10 items-start'):
                    with ui.card().classes('w-2/3 p-10 shadow-2xl rounded-3xl border-none'):
                        ui.label('VOTRE SITUATION').classes('text-[10px] font-bold text-slate-400 mb-4 tracking-widest')
                        area = ui.textarea(placeholder="Parlez à Kareem...").classes('w-full h-72 text-lg').props('outlined rounded')
                        area.bind_value(moteur.data, moteur.step_index)
                        
                        with ui.row().classes('w-full justify-between mt-8'):
                            if moteur.step_index > 0:
                                ui.button('RETOUR', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/'))).props('flat')
                            else: ui.label('')
                            ui.button('ANALYSER ET SUIVANT', on_click=lambda: moteur.analyser_ia(moteur.step_index)).classes('px-10 py-3 font-bold shadow-2xl text-lg shadow-green-100').props('color=secondary rounded')

                    # Feedback Panel
                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-8 bg-slate-800 text-white rounded-3xl shadow-2xl border-l-8 border-secondary'):
                            ui.label('KAREEM IA').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest')
                            ui.markdown().bind_content_from(moteur.ai_feedback, moteur.step_index).classes('text-sm leading-relaxed')

ui.run(title='LegalOS', port=8088, reload=False)
