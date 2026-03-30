from nicegui import ui
import asyncio

# --- MOTEUR DE FONCTIONS REDDINGTON ---
def detect_domain(text):
    keywords = {"travail": ["salaire", "licenciement"], "contrat": ["contrat", "obligation"], "penal": ["plainte", "infraction"]}
    for domain, words in keywords.items():
        if any(w in text.lower() for w in words): return domain
    return "civil"

def score_case_strength(dossier_len):
    return min(dossier_len * 2, 10)

class LegalOS_Engine:
    def __init__(self):
        self.user_authenticated = False
        self.step_index = 0
        self.steps = ["Qualification", "Objectif", "Base légale", "Preuves", "Stratégie", "Amiable", "Procédure", "Rédaction", "Audience", "Jugement", "Recours"]
        self.data = {i: "" for i in range(11)}
        self.ai_feedback = {i: "En attente d'analyse..." for i in range(11)}
        self.dossier_len = 0

    async def analyser_ia(self, index):
        txt = self.data[index]
        if len(txt) < 5:
            ui.notify("Saisie trop courte", color='warning')
            return
        
        ui.notify("Analyse Reddington en cours...", icon='psychology')
        await asyncio.sleep(1)

        # Logique basée sur tes fonctions
        if index == 0:
            dom = detect_domain(txt)
            self.ai_feedback[index] = f"🧠 IA : Domaine {dom.upper()} détecté. Précisez les dates clés."
        elif index == 3:
            self.dossier_len += 1
            score = score_case_strength(self.dossier_len)
            self.ai_feedback[index] = f"📂 Dossier : Force de {score}/10. Ajoutez d'autres preuves."
        else:
            self.ai_feedback[index] = "✅ Étape validée par le système Freeman."

        ui.notify("Terminé. Passage à l'étape suivante.", color='positive')
        await asyncio.sleep(0.5)
        if self.step_index < 10:
            self.step_index += 1
            ui.navigate.to('/')

moteur = LegalOS_Engine()

@ui.page('/')
def main_view():
    ui.colors(primary='#0f172a', secondary='#10b981')

    if not moteur.user_authenticated:
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl rounded-2xl'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-8')
                ui.button('ACTIVER LE SYSTÈME', on_click=lambda: setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')).classes('w-full')
    else:
        with ui.header().classes('bg-slate-900 items-center justify-between p-4'):
            ui.label('LEGALOS | SYSTEM FREEMAN').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r'):
                ui.label('PHASES REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'bg-slate-900 text-white shadow-lg' if active else 'text-slate-300'
                    ui.label(f"{i+1}. {name}").classes(f'p-3 rounded-lg mb-1 transition-all {style}')

            # Zone de travail
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-8 rounded-full h-2')
                ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-black text-slate-800 mb-10')

                with ui.row().classes('w-full no-wrap gap-8'):
                    with ui.card().classes('w-2/3 p-8 shadow-xl rounded-2xl'):
                        ui.label('SAISIE DES DONNÉES').classes('text-xs font-bold text-slate-400 mb-4')
                        area = ui.textarea(placeholder="Décrivez ici...").classes('w-full h-64').props('outlined')
                        area.bind_value(moteur.data, moteur.step_index)
                        
                        # NAVIGATION SANS LE BUG .VISIBLE()
                        with ui.row().classes('w-full justify-between mt-6'):
                            if moteur.step_index > 0:
                                ui.button('PRÉCÉDENT', on_click=lambda: setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/')).props('flat')
                            else:
                                ui.label('')
                            ui.button('ANALYSER ET SUIVANT ➔', on_click=lambda: moteur.analyser_ia(moteur.step_index)).props('color=secondary').classes('px-8 shadow-lg')

                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-2xl border-l-8 border-secondary shadow-xl'):
                            ui.label('FEEDBACK IA').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest')
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm')

ui.run(title='LegalOS', port=8088, reload=False)
