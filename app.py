from nicegui import ui
import asyncio

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

    async def intelligence_reddington(self, index):
        txt = self.data[index].lower()
        if len(txt) < 10:
            ui.notify("Saisie insuffisante pour l'IA", color='warning')
            return

        ui.notify(f"Analyse Freeman...", icon='auto_awesome')
        await asyncio.sleep(1)

        feedbacks = {
            0: "⚖️ Qualification : Dommage identifié. Vérifiez la date des faits.",
            1: "🎯 Objectif : Demande de dommages-intérêts cohérente.",
            2: "📚 Base légale : Article du Code Civil détecté.",
            3: "📂 Preuves : Pensez à scanner les courriers recommandés."
        }
        self.ai_feedback[index] = feedbacks.get(index, "✅ Étape validée par Kareem IA.")
        ui.notify("Analyse terminée. Passage automatique...", color='positive')
        
        await asyncio.sleep(0.5)
        if self.step_index < 10:
            self.step_index += 1
            ui.navigate.to('/')

moteur = LegalOSEngine()

def nav_to(delta):
    moteur.step_index += delta
    ui.navigate.to('/')

@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#00c853')

    if not moteur.user_authenticated:
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl rounded-2xl'):
                ui.label('⚖️ LEGALOS').classes('text-4xl font-black text-center w-full mb-8')
                u = ui.input('Email').classes('w-full')
                p = ui.input('Pass', password=True).classes('w-full')
                ui.button('ACTIVER L\'IA', on_click=lambda: setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')).classes('w-full mt-6 py-4')
    
    else:
        with ui.header().classes('bg-slate-900 items-center justify-between p-4'):
            ui.label('LEGALOS | KAREEM IA').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-black text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if active else 'text-slate-300'
                    ui.label(f"{i+1}. {name}").classes(f'p-3 rounded-md mb-1 {style}')

            # Workzone
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-8 rounded-full h-2')
                
                ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-light text-slate-800 mb-10')

                with ui.row().classes('w-full no-wrap gap-8'):
                    with ui.column().classes('w-2/3 gap-4'):
                        with ui.card().classes('w-full p-8 shadow-xl rounded-2xl'):
                            # Formulaire dynamique
                            idx = moteur.step_index
                            if idx == 0:
                                ui.markdown('👉 **Qualification** : Quel type de problème ? Quelles parties ?')
                            elif idx == 1:
                                ui.markdown('👉 **Objectif** : Que voulez-vous obtenir ?')
                            elif idx == 2:
                                ui.markdown('👉 **Base légale** : Quel article ou contrat ?')
                            elif idx == 3:
                                ui.markdown('👉 **Preuves** : Listez vos documents.')
                            
                            area = ui.textarea(placeholder="Écrivez ici...").classes('w-full h-64 text-lg').props('outlined')
                            area.bind_value(moteur.data, idx)

                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-2xl border-l-8 border-secondary'):
                            ui.label('KAREEM IA').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest')
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm')
                        
                        ui.button('ANALYSER ET CONTINUER ➔', on_click=lambda: moteur.intelligence_reddington(moteur.step_index)).classes('w-full mt-6 py-6 font-bold shadow-xl').props('color=secondary')

                # Navigation (Correction du bug .visible)
                with ui.row().classes('w-full mt-12 justify-between'):
                    if moteur.step_index > 0:
                        ui.button('ÉTAPE PRÉCÉDENTE', icon='arrow_back', on_click=lambda: nav_to(-1)).props('flat')
                    else:
                        ui.label('')

ui.run(title='LegalOS', port=8088, reload=False)
