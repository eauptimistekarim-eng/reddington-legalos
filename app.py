from nicegui import ui
import asyncio

# --- 1. MOTEUR KAREEM IA (LOGIQUE MÉTIER & PERSISTANCE) ---
class KareemIA:
    def __init__(self):
        self.user_authenticated = False
        self.step_index = 0
        self.steps = [
            "Qualification", "Objectif", "Base légale", "Preuves / Dossier", 
            "Analyse stratégique", "Phase amiable", "Choix de procédure", 
            "Rédaction juridique", "Audience", "Jugement", "Exécution / Recours"
        ]
        # Initialisation propre des dictionnaires
        self.data = {i: "" for i in range(11)}
        self.ai_feedback = {i: "Kareem IA attend votre saisie..." for i in range(11)}
        self.is_pro = False

    async def analyser_ia(self, index):
        txt = self.data[index]
        if len(txt) < 8:
            ui.notify("Kareem : 'Saisie trop courte pour une analyse sérieuse.'", color='warning')
            return

        ui.notify("Kareem IA analyse...", icon='auto_awesome')
        await asyncio.sleep(1.2)

        # LOGIQUE D'AUTOMATISATION (TA VISION)
        if index == 0: # Qualification automatique de la base légale
            if any(w in txt.lower() for w in ["travail", "salaire", "licenciement", "patron"]):
                self.data[2] = "Code du Travail - Article L1232-1 (Rupture du contrat)"
                self.ai_feedback[2] = "Kareem : J'ai pré-rempli la base légale en Droit du Travail."
            elif any(w in txt.lower() for w in ["contrat", "vente", "achat", "rembourser"]):
                self.data[2] = "Code Civil - Article 1103 (Force obligatoire des contrats)"
                self.ai_feedback[2] = "Kareem : J'ai pré-rempli la base légale en Droit Civil."

        # FEEDBACK PERSONNALISÉ
        res = f"✅ Kareem : Analyse de la phase '{self.steps[index]}' terminée. "
        if index == 3: res += "N'oubliez pas d'uploader les originaux."
        if index == 4: res += "Conseil : Tentez une médiation, les risques sont modérés."
        
        self.ai_feedback[index] = res
        ui.notify("Analyse validée", color='positive')

moteur = KareemIA()

# --- 2. INTERFACE UTILISATEUR (UX FREEMAN) ---
@ui.page('/')
def main():
    ui.colors(primary='#0f172a', secondary='#10b981', accent='#f59e0b')

    if not moteur.user_authenticated:
        # --- LOGIN / INSCRIPTION ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-full max-w-sm p-10 shadow-2xl border-t-8 border-primary rounded-2xl'):
                ui.label('⚖️ LEGALOS').classes('text-4xl font-black text-center w-full mb-2')
                ui.label('SYSTÈME FREEMAN').classes('text-[10px] text-center w-full mb-8 text-slate-400 tracking-[.3em]')
                
                email = ui.input('Email (admin@legalos.fr)').classes('w-full').props('outlined')
                password = ui.input('Mot de passe (123)', password=True).classes('w-full mt-2').props('outlined')
                
                with ui.row().classes('w-full justify-between mt-8 items-center'):
                    ui.button('S\'INSCRIRE', on_click=lambda: ui.notify('Ouverture des inscriptions bientôt')).props('flat no-caps')
                    ui.button('CONNEXION', on_click=lambda: (setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')) 
                              if email.value=="admin@legalos.fr" and password.value=="123" 
                              else ui.notify('Erreur identifiants', color='negative')).classes('px-8 py-2 shadow-lg font-bold')
    
    else:
        # --- APP DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl border-b border-slate-800'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('balance', color='white').classes('text-2xl')
                ui.label('KAREEM IA').classes('font-black text-xl text-white tracking-tighter')
            
            with ui.row().classes('items-center gap-4'):
                ui.button('PRO PLAN', icon='bolt', on_click=lambda: ui.notify('Redirection Stripe...')).props('flat color=amber').classes('text-xs font-bold')
                ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # SIDEBAR DYNAMIQUE
            with ui.column().classes('w-80 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-black text-slate-400 mb-6 tracking-widest uppercase')
                for i, name in enumerate(moteur.steps):
                    def change_step(new_idx=i):
                        moteur.step_index = new_idx
                        ui.navigate.to('/')
                    
                    is_active = (i == moteur.step_index)
                    color = 'bg-slate-900 text-white shadow-xl' if is_active else 'text-slate-400 hover:bg-slate-100'
                    ui.button(f"{i+1}. {name}", on_click=change_step).classes(f'w-full text-left justify-start p-4 rounded-xl mb-1 transition-all no-caps {color}').props('flat' if not is_active else '')

            # ZONE DE TRAVAIL (THE WORKSPACE)
            with ui.column().classes('flex-grow p-12 overflow-auto'):
                # Barre de progression
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-8 rounded-full h-1.5 shadow-sm')
                
                with ui.row().classes('w-full justify-between items-end mb-10'):
                    with ui.column().classes('gap-0'):
                        ui.label(f'PHASE {moteur.step_index + 1}').classes('text-primary font-black text-[10px] tracking-widest')
                        ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-black text-slate-800 tracking-tighter')

                with ui.row().classes('w-full no-wrap gap-8 items-start'):
                    # CARTE DE RÉDACTION
                    with ui.card().classes('w-2/3 p-8 shadow-2xl rounded-3xl border-none bg-white'):
                        ui.label('DÉTAILS DU DOSSIER').classes('text-[10px] font-bold text-slate-400 mb-4 tracking-widest uppercase')
                        
                        # Interface spécifique par étape
                        idx = moteur.step_index
                        if idx == 3:
                            ui.upload(label='📁 Déposer vos preuves (PDF, PNG, JPG)', on_upload=lambda: ui.notify('Fichier reçu')).classes('w-full mb-4').props('flat bordered')
                        
                        area = ui.textarea(placeholder="Décrivez les faits ici...").classes('w-full h-80 text-lg').props('outlined rounded')
                        area.bind_value(moteur.data, idx)
                        
                        with ui.row().classes('w-full justify-between mt-8'):
                            if moteur.step_index > 0:
                                ui.button('RETOUR', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/'))).props('flat color=slate-400')
                            else: ui.label('')
                            ui.button('ANALYSER AVEC KAREEM ➔', on_click=lambda: moteur.analyser_ia(moteur.step_index)).classes('px-10 py-3 font-bold shadow-2xl shadow-green-200 text-lg').props('color=secondary rounded')

                    # CARTE KAREEM IA (FEEDBACK)
                    with ui.column().classes('w-1/3 gap-4'):
                        with ui.card().classes('w-full p-6 bg-slate-900 text-white rounded-3xl shadow-2xl border-l-8 border-secondary'):
                            with ui.row().classes('items-center gap-2 mb-4'):
                                ui.icon('psychology', color='secondary')
                                ui.label('KAREEM IA').classes('text-[10px] font-bold text-secondary tracking-widest')
                            
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm leading-relaxed text-slate-300')

                        if moteur.step_index < 10:
                            ui.button('Étape suivante', icon='chevron_right', on_click=lambda: (setattr(moteur, 'step_index', moteur.step_index + 1) or ui.navigate.to('/'))).classes('w-full py-4 text-slate-400').props('flat')

ui.run(title='LegalOS - Kareem IA', port=8088, reload=False)
