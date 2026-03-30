from nicegui import ui
import asyncio
import secrets # Pour générer des codes si besoin

# --- MOTEUR KAREEM IA & GESTION DES ACCÈS ---
class KareemEngine:
    def __init__(self):
        self.user_authenticated = False
        # Liste des codes d'accès pour tes premiers contacts
        self.valid_codes = ["FREEMAN2024", "LEGALOS_VIP", "KAREEM_BETA", "TEST01"]
        
        self.step_index = 0
        self.steps = [
            "Qualification", "Objectif", "Base légale", "Preuves / Dossier", 
            "Analyse stratégique", "Phase amiable", "Choix de procédure", 
            "Rédaction juridique", "Audience", "Jugement", "Exécution / Recours"
        ]
        
        # Instructions par étape
        self.instructions = {
            0: "Décrivez les faits de manière chronologique. Qui est impliqué ?",
            1: "Quel est le résultat idéal ? (Ex: Remboursement de 1500€)",
            2: "Textes de loi identifiés par Kareem IA pour votre dossier.",
            3: "Déposez vos documents (PDF, Photos, Emails) ci-dessous.",
            4: "Kareem analyse les points forts et faibles de votre position.",
            5: "Préparons le courrier de mise en demeure.",
        }

        self.data = {i: "" for i in range(11)}
        self.files = {i: [] for i in range(11)} # Stockage des noms de fichiers par étape
        self.ai_feedback = {i: "Kareem IA : Prêt pour l'analyse." for i in range(11)}
        self.analysis_done = False

    def check_access(self, code):
        if code.upper() in self.valid_codes:
            self.user_authenticated = True
            return True
        return False

    def analyser_ia(self, index):
        t = self.data[index].lower()
        # Logique de traduction intelligente
        if "loyer" in t or "bail" in t:
            self.data[2] = "Loi du 6 juillet 1989 / Code Civil"
            res = "🏠 **Kareem :** Litige locatif détecté. Nous allons viser la mise en conformité du bail."
        elif "patron" in t or "travail" in t:
            self.data[2] = "Code du Travail - Art. L1221-1"
            res = "💼 **Kareem :** Conflit employeur détecté. Focus sur le contrat de travail."
        else:
            res = f"✅ **Kareem :** Analyse de la phase {self.steps[index]} terminée."
        
        self.ai_feedback[index] = res
        self.analysis_done = True
        ui.navigate.to('/')

moteur = KareemEngine()

@ui.page('/')
def main():
    ui.colors(primary='#0f172a', secondary='#10b981')

    if not moteur.user_authenticated:
        # --- PAGE D'ACCÈS EXCLUSIF ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl rounded-3xl border-t-8 border-secondary'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-black text-center w-full mb-2 text-slate-800')
                ui.label('ACCÈS PRIVÉ KAREEM IA').classes('text-[10px] text-center w-full mb-8 text-slate-400 tracking-[.3em]')
                
                code_input = ui.input('Entrez votre code d\'accès').classes('w-full').props('outlined rounded')
                
                def try_login():
                    if moteur.check_access(code_input.value):
                        ui.notify('Accès accordé. Bienvenue dans le Système Freeman.', color='positive')
                        ui.navigate.to('/')
                    else:
                        ui.notify('Code invalide. Contactez l\'administrateur.', color='negative')

                ui.button('ACTIVER LE SYSTÈME', on_click=try_login).classes('w-full mt-6 py-4 font-bold shadow-lg')
                ui.label('Codes valides pour test : FREEMAN2024, TEST01').classes('text-[8px] text-slate-400 mt-4 text-center')

    else:
        # --- DASHBOARD KAREEM ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            ui.label('KAREEM IA | SYSTÈME FREEMAN').classes('font-black text-white tracking-tighter')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR
            with ui.column().classes('w-72 p-6 bg-white border-r overflow-y-auto shadow-inner'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-bold text-slate-400 mb-6 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    def goto(idx=i):
                        moteur.step_index = idx
                        moteur.analysis_done = False
                        ui.navigate.to('/')
                    active = (i == moteur.step_index)
                    style = 'bg-slate-900 text-white shadow-xl scale-105' if active else 'text-slate-400 hover:text-primary'
                    ui.button(f"{i+1}. {name}", on_click=goto).classes(f'w-full text-left justify-start p-3 rounded-xl mb-1 no-caps {style}').props('flat' if not active else '')

            # WORKZONE
            with ui.column().classes('flex-grow p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-10 rounded-full h-1.5')
                ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-black text-slate-800 mb-8 tracking-tighter')

                with ui.row().classes('w-full no-wrap gap-10 items-start'):
                    # Zone Saisie et Upload
                    with ui.card().classes('w-2/3 p-10 shadow-2xl rounded-3xl border-none'):
                        # Bulle d'instruction
                        with ui.row().classes('bg-blue-50 p-4 rounded-xl items-center gap-3 mb-6 w-full'):
                            ui.icon('info', color='primary')
                            ui.label(moteur.instructions.get(moteur.step_index, "Détaillez cette étape.")).classes('text-primary text-sm italic')
                        
                        area = ui.textarea(placeholder="Saisissez ici...").classes('w-full h-64 text-lg').props('outlined rounded')
                        area.bind_value(moteur.data, moteur.step_index)

                        # SYSTÈME D'UPLOAD (Disponible à chaque étape si besoin)
                        ui.label('DOCUMENTS & PREUVES').classes('text-[10px] font-bold text-slate-400 mt-6 mb-2')
                        ui.upload(label='Ajouter un fichier', on_upload=lambda e: moteur.files[moteur.step_index].append(e.name)).classes('w-full').props('flat bordered')
                        
                        with ui.row().classes('w-full justify-between mt-8'):
                            if moteur.step_index > 0:
                                ui.button('RETOUR', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/'))).props('flat color=slate-400')
                            else: ui.label('')
                            ui.button('ANALYSER', on_click=lambda: moteur.analyser_ia(moteur.step_index)).classes('px-10 py-3 font-bold shadow-xl shadow-blue-100').props('color=primary rounded')

                    # Feedback Kareem
                    with ui.column().classes('w-1/3 gap-4'):
                        with ui.card().classes('w-full p-8 bg-slate-800 text-white rounded-3xl shadow-2xl border-l-8 border-secondary'):
                            ui.label('KAREEM IA').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest')
                            ui.markdown().bind_content_from(moteur.ai_feedback, moteur.step_index).classes('text-sm leading-relaxed')

                        if moteur.analysis_done and moteur.step_index < 10:
                            ui.button('ÉTAPE SUIVANTE ➔', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index + 1) or setattr(moteur, 'analysis_done', False) or ui.navigate.to('/'))).classes('w-full py-6 font-black shadow-2xl shadow-green-200').props('color=secondary rounded')

ui.run(title='LegalOS Freeman', port=8088, reload=False)
