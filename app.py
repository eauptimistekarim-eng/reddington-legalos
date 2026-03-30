from nicegui import ui
import asyncio

# --- MOTEUR KAREEM IA ---
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
        self.ai_feedback = {i: "Kareem IA : Prêt à analyser votre situation." for i in range(11)}

    def traduire_en_droit(self, texte, index):
        t = texte.lower()
        if index == 0:
            if any(w in t for w in ["patron", "viré", "salaire"]):
                self.data[2] = "Code du Travail - Art. L1232-1"
                return "⚖️ NOTION : Droit du Travail. J'ai automatisé l'étape 3."
            if any(w in t for w in ["argent", "prêt", "dette"]):
                self.data[2] = "Code Civil - Art. 1103"
                return "⚖️ NOTION : Obligation contractuelle."
        return "Analyse effectuée. Continuez la progression."

    async def analyser_ia(self, index):
        if len(self.data[index]) < 5:
            ui.notify("Kareem : Saisie trop courte", color='warning')
            return
        ui.notify("Kareem IA réfléchit...", icon='psychology')
        await asyncio.sleep(1)
        self.ai_feedback[index] = self.traduire_en_droit(self.data[index], index)
        if self.step_index < 10:
            self.step_index += 1
            ui.navigate.to('/')

moteur = KareemEngine()

@ui.page('/')
def main():
    ui.colors(primary='#0f172a', secondary='#10b981')

    if not moteur.user_authenticated:
        # --- LOGIN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-80 p-8 shadow-2xl rounded-2xl'):
                ui.label('⚖️ LegalOS').classes('text-3xl font-bold text-center w-full mb-6')
                e = ui.input('Email').classes('w-full')
                p = ui.input('Pass', password=True).classes('w-full')
                ui.button('CONNEXION', on_click=lambda: (setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')) 
                          if e.value == "admin@legalos.fr" and p.value == "123" else ui.notify('admin@legalos.fr / 123')).classes('w-full mt-4')
    else:
        # --- APP ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4'):
            ui.label('KAREEM IA | SYSTÈME FREEMAN').classes('font-bold text-white')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar (Navigation Libre)
            with ui.column().classes('w-72 p-6 bg-white border-r overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-bold text-slate-400 mb-4 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    def goto(idx=i): 
                        moteur.step_index = idx
                        ui.navigate.to('/')
                    active = (i == moteur.step_index)
                    btn_color = 'bg-slate-900 text-white shadow-lg' if active else 'text-slate-400 hover:text-primary'
                    ui.button(f"{i+1}. {name}", on_click=goto).classes(f'w-full text-left justify-start p-3 rounded-lg mb-1 no-caps {btn_color}').props('flat' if not active else '')

            # Zone de travail
            with ui.column().classes('flex-grow p-12 overflow-auto'):
                # Correction de la parenthèse manquante ici (Image 3)
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-8 rounded-full h-1')
                
                ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-black text-slate-800 mb-8 tracking-tighter')

                with ui.row().classes('w-full no-wrap gap-8 items-start'):
                    # Formulaire
                    with ui.card().classes('w-2/3 p-8 shadow-xl rounded-2xl border-none'):
                        if moteur.step_index == 3:
                            ui.upload(label='Ajouter des preuves').classes('w-full mb-4').props('flat bordered')
                        
                        area = ui.textarea(placeholder="Écrivez ici...").classes('w-full h-64 text-lg').props('outlined rounded')
                        area.bind_value(moteur.data, moteur.step_index)
                        
                        with ui.row().classes('w-full justify-between mt-6'):
                            # Correction du bug .visible() (Images 1 & 2)
                            if moteur.step_index > 0:
                                ui.button('RETOUR', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/'))).props('flat')
                            else:
                                ui.label('')
                            ui.button('ANALYSER ET SUIVANT', on_click=lambda: moteur.analyser_ia(moteur.step_index)).classes('px-8 font-bold shadow-lg').props('color=secondary rounded')

                    # Feedback Kareem
                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-2xl shadow-xl border-l-8 border-secondary'):
                            ui.label('KAREEM IA').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest')
                            ui.markdown().bind_content_from(moteur.ai_feedback, moteur.step_index).classes('text-sm italic')

ui.run(title='LegalOS', port=8088, reload=False)
