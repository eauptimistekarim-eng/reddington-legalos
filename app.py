from nicegui import ui
import asyncio

# =========================================================
# 🧠 LE MOTEUR DE FONCTIONS (TON ARCHITECTURE)
# =========================================================

def detect_domain(text):
    keywords = {"travail": ["salaire", "licenciement", "patron"], "contrat": ["contrat", "obligation", "achat"], "penal": ["plainte", "vol", "agression"]}
    for domain, words in keywords.items():
        if any(w in text.lower() for w in words): return domain
    return "civil général"

def search_legal_basis(keyword):
    base = {"travail": "Code du travail - L1232-1", "contrat": "Code civil - art. 1103", "penal": "Code pénal - art. 222-1"}
    return base.get(keyword.lower(), "Base à déterminer via Légifrance")

def score_case_strength(dossier_len):
    return min(dossier_len * 2.5, 10) # Score sur 10

def devil_advocate(dossier_len):
    if dossier_len < 3: return "⚠️ ATTENTION : Dossier fragile. Manque de preuves matérielles."
    return "✅ Structure solide, mais préparez-vous à la contestation de la partie adverse."

# =========================================================
# ⚙️ GESTIONNAIRE D'ÉTAT (SAAS)
# =========================================================

class LegalOS_SaaS:
    def __init__(self):
        self.user_authenticated = False
        self.step_index = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves / Dossier", 
            "5. Analyse stratégique", "6. Phase amiable", "7. Choix de procédure", 
            "8. Rédaction juridique", "9. Audience", "10. Jugement", "11. Exécution / Recours"
        ]
        self.data = {i: "" for i in range(11)}
        self.ai_feedback = {i: "En attente d'analyse..." for i in range(11)}
        self.dossier_pieces = [] # Pour stocker les preuves

    async def executer_etape_ia(self, index):
        """Déclenche les fonctions spécifiques à l'étape"""
        txt = self.data[index]
        if len(txt) < 5:
            ui.notify("Saisie trop courte", color='warning')
            return

        ui.notify(f"Kareem IA active le module {self.steps[index]}...", icon='bolt')
        await asyncio.sleep(1)

        # Application de tes fonctions selon l'index
        if index == 0: # Qualification
            domaine = detect_domain(txt)
            res = f"Domaine détecté : {domaine.upper()}. Parties : Utilisateur vs Partie adverse."
        elif index == 1: # Objectif
            res = "Objectif validé. L'IA suggère : Demander l'exécution forcée + Article 700."
        elif index == 2: # Base légale
            domaine = detect_domain(self.data[0])
            base = search_legal_basis(domaine)
            res = f"Fondement suggéré : {base}. (Vérification Légifrance recommandée)."
        elif index == 3: # Preuves
            self.dossier_pieces.append(txt)
            score = score_case_strength(len(self.dossier_pieces))
            res = f"Force du dossier : {score}/10. {len(self.dossier_pieces)} pièce(s) enregistrée(s)."
        elif index == 4: # Strategie / Avocat du diable
            res = devil_advocate(len(self.dossier_pieces))
        else:
            res = f"Module {self.steps[index]} traité avec succès."

        self.ai_feedback[index] = res
        ui.notify("Analyse terminée", color='positive')
        
        await asyncio.sleep(0.5)
        if self.step_index < 10:
            self.step_index += 1
            ui.navigate.to('/')

moteur = LegalOS_SaaS()

# =========================================================
# 🎨 INTERFACE (UI)
# =========================================================

@ui.page('/')
def main_page():
    ui.colors(primary='#0f172a', secondary='#10b981')

    if not moteur.user_authenticated:
        # --- LOGIN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('p-10 shadow-2xl border-t-8 border-primary w-96'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full')
                ui.label('SYSTÈME FREEMAN').classes('text-xs text-center w-full mb-8 text-slate-400 tracking-widest')
                u = ui.input('Identifiant')
                p = ui.input('Mot de passe', password=True)
                ui.button('ACTIVER', on_click=lambda: setattr(moteur, 'user_authenticated', True) or ui.navigate.to('/')).classes('w-full mt-4')
    
    else:
        # --- DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-lg'):
            ui.label('LEGALOS | KAREEM IA').classes('font-bold text-xl text-white')
            ui.button('STRIPE PAIEMENT', icon='payments').props('flat color=amber')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'user_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-[10px] font-black text-slate-400 mb-4 tracking-widest')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'bg-slate-900 text-white shadow-lg' if active else 'text-slate-400'
                    ui.label(name).classes(f'p-3 rounded-lg mb-1 transition-all {style}')

            # Main Area
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-8 h-1 rounded-full')
                ui.label(moteur.steps[moteur.step_index]).classes('text-6xl font-black text-slate-800 mb-10 tracking-tighter')

                with ui.row().classes('w-full no-wrap gap-8'):
                    # Zone de saisie
                    with ui.card().classes('w-2/3 p-8 shadow-xl rounded-2xl border-none'):
                        ui.label('RÉDACTION STRATÉGIQUE').classes('text-xs font-bold text-slate-400 mb-4')
                        area = ui.textarea(placeholder="Décrivez ici...").classes('w-full h-80 text-lg').props('outlined rounded')
                        area.bind_value(moteur.data, moteur.step_index)
                        
                        with ui.row().classes('w-full justify-between mt-4'):
                            ui.button('PRÉCÉDENT', on_click=lambda: setattr(moteur, 'step_index', moteur.step_index - 1) or ui.navigate.to('/')).props('flat').visible(moteur.step_index > 0)
                            ui.button('ANALYSER ET CONTINUER ➔', on_click=lambda: moteur.executer_etape_ia(moteur.step_index)).props('color=secondary').classes('px-8 py-2 font-bold shadow-lg')

                    # Feedback IA
                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-2xl shadow-2xl border-l-8 border-secondary'):
                            ui.label('ASSISTANT FREEMAN').classes('text-[10px] font-bold text-secondary mb-4 tracking-widest uppercase')
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm leading-relaxed')
                        
                        if moteur.step_index == 3: # Module Preuves spécial
                             ui.label(f"Pièces au dossier : {len(moteur.dossier_pieces)}").classes('mt-4 text-slate-500 font-bold')

ui.run(title='LegalOS Freeman', port=8088, reload=False)
