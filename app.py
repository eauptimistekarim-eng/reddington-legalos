from nicegui import ui
import asyncio

# =========================================================
# 🧠 LE CERVEAU DE KAREEM IA (LOGIQUE & TRADUCTION)
# =========================================================

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
        self.ai_feedback = {i: "Kareem IA : J'attends votre description pour débuter l'analyse." for i in range(11)}
        self.dossier_pieces = []

    def vulgariser(self, texte, index):
        """Traduit le langage courant en notions juridiques simples"""
        t = texte.lower()
        notion = "Analyse en cours..."
        conseil = "Continuez à remplir les détails."

        if index == 0: # Qualification
            if any(w in t for w in ["patron", "chef", "boulot", "viré", "salaire"]):
                notion = "⚖️ NOTION : Droit du Travail / Rupture contractuelle"
                conseil = "Kareem : Je pré-remplis la base légale avec le Code du Travail."
                self.data[2] = "Code du Travail - Article L1232-1"
            elif any(w in t for w in ["argent", "prêt", "rembourser", "dette", "facture"]):
                notion = "⚖️ NOTION : Créance civile / Obligation de payer"
                conseil = "Kareem : Nous allons viser l'exécution forcée du contrat."
                self.data[2] = "Code Civil - Article 1103"
            elif any(w in t for w in ["appart", "loyer", "bail", "proprio"]):
                notion = "⚖️ NOTION : Droit Immobilier / Litige locatif"
                conseil = "Kareem : La mise en demeure sera l'étape clé ici."
                self.data[2] = "Loi du 6 juillet 1989"
        
        elif index == 3: # Preuves
            score = min(len(self.data[3].split('\n')) * 2, 10)
            notion = f"⚖️ DOSSIER : Force probante estimée à {score}/10"
            conseil = "Kareem : Plus vous avez d'écrits (mails, SMS), plus le dossier est solide."

        return f"**{notion}**\n\n{conseil}"

    async def analyser_ia(self, index):
        if len(self.data[index]) < 10:
            ui.notify("Kareem : 'Saisie trop courte pour une analyse.'", color='warning')
            return

        ui.notify("Kareem analyse et traduit...", icon='psychology')
        await asyncio.sleep(1.2)
        
        # Mise à jour du feedback avec la traduction
        self.ai_feedback[index] = self.vulgariser(self.data[index], index)
        ui.notify("Analyse terminée", color='positive')
        
        await asyncio.sleep(0.5)
        if self.step_index < 10:
            self.step_index += 1
            ui.navigate.to('/')

moteur = KareemEngine()

# =========================================================
# 🎨 INTERFACE UTILISATEUR (UX PREMIUM)
# =========================================================

@ui.page('/')
def main_view():
    ui.colors(primary='#0f172a', secondary='#10b981', accent='#f59e0b')

    if not moteur.user_authenticated:
        # --- LOGIN / INSCRIPTION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-full max-w-sm p-10 shadow-2xl border-t-8 border-primary rounded-3xl'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-black text-center w-full mb-2 text-slate-800')
                ui.label('SYSTÈME FREEMAN').classes('text-[10px] text-center w-full mb-10 text-slate-400 tracking-[.3em]')
                
                email = ui.input('Email').classes('w-full').props('outlined rounded')
                pwd = ui.input('Mot de passe', password=True).classes('w-full mt-2').props('outlined rounded')
                
                with ui.row().classes('w-full justify-between mt-8 items-center'):
                    ui.button('INSCRIPTION', on_click=lambda: ui.notify('Bientôt disponible')).props('flat no-caps').classes('text-slate-400')
                    ui.button('CONNEXION', on_click=lambda: (setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')) 
                              if email.value == "admin@legalos.fr" and pwd.value == "123" 
                              else ui.notify('Identifiants : admin@legalos.fr / 123', color='negative')).classes('px-8 py-2 font-bold shadow-lg shadow-blue-200')
    
    else:
        # --- DASHBOARD PRINCIPAL ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl border-b border-slate-800'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('balance', color='white').classes('text-2xl')
                ui.label('KAREEM IA').classes('font-black text-xl text-white tracking-tighter')
            
            with ui.row().classes('items-center gap-6'):
                ui.button('STRIPE PRO', icon='bolt').props('flat color=amber').classes('text-xs font-bold')
                ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR : NAVIGATION LIBRE
            with ui.column().classes('w-80 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-black text-slate-400 mb-6 tracking-widest uppercase')
                for i, name in enumerate(moteur.steps):
                    def change_step(new_idx=i):
                        moteur.step_index = new_idx
                        ui.navigate.to('/')
                    
                    is_active = (i == moteur.step_index)
                    color = 'bg-slate-900 text-white shadow-xl translate-x-2' if is_active else 'text-slate-400 hover:text-primary hover:bg-slate-50'
                    ui.button(f"{i+1}. {name}", on_click=change_step).classes(f'w-full text-left justify-start p-4 rounded-xl mb-1 transition-all no-caps {color}').props('flat' if not is_active else '')

            # WORKSPACE
            with ui.column().classes('flex-grow p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1)
