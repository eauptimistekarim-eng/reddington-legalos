from nicegui import ui
import asyncio

class KareemEngine:
    def __init__(self):
        self.user_authenticated = False
        self.auth_mode = 'login' # 'login' ou 'signup'
        self.step_index = 0
        self.steps = [
            "Qualification", "Objectif", "Base légale", "Preuves / Dossier", 
            "Analyse stratégique", "Phase amiable", "Choix de procédure", 
            "Rédaction juridique", "Audience", "Jugement", "Exécution / Recours"
        ]
        # Instructions spécifiques par étape
        self.instructions = {
            0: "Expliquez votre situation avec vos mots. Qui ? Quoi ? Quand ?",
            1: "Que voulez-vous obtenir concrètement ? (Remboursement, excuses, annulation...)",
            2: "Kareem suggère ici les textes de loi applicables à votre cas.",
            3: "Listez ou uploadez vos preuves : mails, contrats, témoignages, photos.",
            4: "Analyse des chances de succès selon la méthode Reddington.",
            5: "Préparation d'un courrier de mise en demeure ou d'une médiation.",
        }
        self.data = {i: "" for i in range(11)}
        self.ai_feedback = {i: "Kareem IA : Prêt à traduire votre situation." for i in range(11)}
        self.analysis_done = False

    def traduire_en_juridique(self, texte, index):
        t = texte.lower()
        if index == 0:
            if any(w in t for w in ["logement", "loyer", "appart"]):
                self.data[2] = "Loi ELAN / Code de la construction"
                return "🏠 **Kareem :** Litige de **Droit Immobilier** détecté. C'est une excellente base pour l'étape 3."
            if any(w in t for w in ["patron", "viré", "travail"]):
                self.data[2] = "Code du Travail - Art. L1232-1"
                return "💼 **Kareem :** Nous sommes en **Droit du Travail**. Procédure de licenciement à vérifier."
        return f"✅ **Kareem :** Phase {self.steps[index]} analysée. Prêt pour la suite."

    async def analyser_ia(self, index):
        if len(self.data[index]) < 5:
            ui.notify("Kareem : 'Dites-m'en un peu plus...'", color='warning')
            return
        ui.notify("Kareem analyse...", icon='psychology')
        await asyncio.sleep(1)
        self.ai_feedback[index] = self.traduire_en_juridique(self.data[index], index)
        self.analysis_done = True
        ui.navigate.to('/')

moteur = KareemEngine()

@ui.page('/')
def main():
    ui.colors(primary='#0f172a', secondary='#10b981', accent='#f59e0b')

    if not moteur.user_authenticated:
        # --- LOGIN / INSCRIPTION (UX AMÉLIORÉE) ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-8 shadow-2xl rounded-3xl border-t-8 border-primary'):
                ui.label('⚖️ LEGALOS').classes('text-3xl font-black text-center w-full mb-2')
                
                with ui.tabs().classes('w-full') as tabs:
                    login_tab = ui.tab('CONNEXION')
                    signup_tab = ui.tab('INSCRIPTION')
                
                with ui.tab_panels(tabs, value=login_tab).classes('w-full bg-transparent'):
                    with ui.tab_panel(login_tab):
                        e = ui.input('Email').classes('w-full').props('outlined rounded')
                        p = ui.input('Pass', password=True).classes('w-full mt-2').props('outlined rounded')
                        ui.button('SE CONNECTER', on_click=lambda: (setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')) 
                                  if e.value == "admin@legalos.fr" and p.value == "123" else ui.notify('admin@legalos.fr / 123')).classes('w-full mt-6 py-4 shadow-lg')
                    
                    with ui.tab_panel(signup_tab):
                        ui.input('Nom complet').classes('w-full').props('outlined rounded')
                        ui.input('Email').classes('w-full mt-2').props('outlined rounded')
                        ui.input('Mot de passe', password=True).classes('w-full mt-2').props('outlined rounded')
                        ui.button('CRÉER UN COMPTE', on_click=lambda: ui.notify('Compte créé ! Connectez-vous.')).classes('w-full mt-6 py-4').props('color=accent')

    else:
        # --- DASHBOARD KAREEM IA ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            ui.label('KAREEM IA | SYSTÈME FREEMAN').classes('font-black text-white tracking-tighter')
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
                    ui.button(f"{i+1}. {name}", on_click=goto).classes(f'w-full text-left justify-start p-3 rounded-xl mb-1 no-caps {style}').props('flat' if not active else '')

            # Workzone
            with ui.column().classes('flex-grow p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-10 rounded-full h-1.5')
                
                # Header Étape
                with ui.row().classes('w-full justify-between items-center mb-8'):
                    ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-black text-slate-800 tracking-tighter')
                    # Indicateur de force
                    with ui.column().classes('items-end'):
                        ui.label('FORCE DU DOSSIER').classes('text-[10px] font-bold text-slate-400')
                        ui.badge(f'{min(len(moteur.data[moteur.step_index])//5, 100)}%', color='secondary').classes('p-2')

                with ui.row().classes('w-full no-wrap gap-10 items-start'):
                    # Zone de saisie
                    with ui.card().classes('w-2/3 p-10 shadow-2xl rounded-3xl border-none'):
                        # MESSAGE D'INSTRUCTIONS (UX)
                        with ui.row().classes('bg-blue-50 p-4 rounded-xl items-center gap-3 mb-6'):
                            ui.icon('info', color='primary')
                            ui.label(moteur.instructions.get(moteur.step_index, "Complétez cette étape pour avancer.")).classes('text-primary text-sm font-medium')
                        
                        area = ui.textarea(placeholder="Parlez à Kareem...").classes('w-full h-72 text-lg').props('outlined rounded shadow-inner')
                        area.bind_value(moteur.data, moteur.step_index)
                        
                        with ui.row().classes('w-full justify-between mt-8'):
                            if moteur.step_index > 0:
                                ui.button('RETOUR', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/'))).props('flat color=slate-400')
                            else: ui.label('')
                            ui.button('LANCER L\'ANALYSE', on_click=lambda: moteur.analyser_ia(moteur.step_index)).classes('px-10 py-3 font-bold shadow-2xl shadow-blue-100').props('color=primary rounded')

                    # Feedback Panel
                    with ui.column().classes('w-1/3 gap-4'):
                        with ui.card().classes('w-full p-8 bg-slate-800 text-white rounded-3xl shadow-2xl border-l-8 border-secondary'):
                            ui.label('KAREEM IA').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest')
                            ui.markdown().bind_content_from(moteur.ai_feedback, moteur.step_index).classes('text-sm leading-relaxed')

                        if moteur.analysis_done and moteur.step_index < 10:
                            ui.button('ÉTAPE SUIVANTE ➔', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index + 1) or setattr(moteur, 'analysis_done', False) or ui.navigate.to('/'))).classes('w-full py-6 font-black shadow-2xl shadow-green-200 animate-bounce').props('color=secondary rounded')

ui.run(title='LegalOS Freeman', port=8088, reload=False)
