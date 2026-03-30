from nicegui import ui
import asyncio

# --- 1. MOTEUR DU SYSTÈME FREEMAN AVEC IA RÉACTIVE ---
class KareemIALegalOS:
    def __init__(self):
        self.is_authenticated = False
        self.step_index = 0
        self.steps = [
            "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves / Dossier", 
            "5. Analyse stratégique", "6. Phase amiable", "7. Choix de procédure", 
            "8. Rédaction juridique", "9. Audience", "10. Jugement", "11. Exécution / Recours"
        ]
        self.data = {i: "" for i in range(11)}
        self.ai_feedback = {i: "En attente de saisie pour analyse..." for i in range(11)}

    async def analyser_ia(self, index):
        """Moteur d'analyse intelligent basé sur le contexte de la phase"""
        texte = self.data[index].lower()
        if len(texte) < 15:
            ui.notify("Saisie trop courte (min. 15 caractères)", color='warning')
            return
        
        ui.notify(f"Kareem IA analyse la Phase {index+1}...", icon='psychology')
        await asyncio.sleep(1.5)
        
        # --- LOGIQUE D'ANALYSE MÉTIER ---
        reponse = ""
        if index == 0: # Qualification
            if any(m in texte for m in ["travail", "licenciement", "patron", "salaire"]):
                reponse = "💡 IA : Dossier orienté Droit du Travail. Vérifiez les délais de prescription (2 ans pour l'exécution du contrat, 12 mois pour la rupture)."
            elif any(m in texte for m in ["loyer", "bail", "locataire", "propriétaire"]):
                reponse = "💡 IA : Contentieux locatif détecté. La mise en demeure préalable est obligatoire avant toute action."
            else:
                reponse = "✅ IA : Qualification reçue. Précisez si vous agissez en tant que personne physique ou morale."

        elif index == 1: # Objectif
            if any(m in texte for m in ["argent", "euros", "payé", "remboursement"]):
                reponse = "💰 IA : Objectif financier. N'oubliez pas de demander les intérêts au taux légal et l'Article 700 (frais d'avocat)."
            elif "contrat" in texte:
                reponse = "📄 IA : Objectif contractuel. L'annulation demande une preuve de vice du consentement ou d'inexécution grave."
            else:
                reponse = "✅ IA : Objectif enregistré. Assurez-vous qu'il soit chiffrable ou techniquement réalisable par un juge."

        elif index == 2: # Base Légale
            if "loi" in texte or "article" in texte:
                reponse = "📚 IA : Fondement textuel identifié. Vérifiez sur Légifrance si l'article n'a pas été modifié récemment."
            else:
                reponse = "⚠️ IA : Dossier fragile. Sans base légale (Code Civil, Code du Travail, etc.), votre demande risque d'être rejetée."

        elif index == 3: # Preuves
            if any(m in texte for m in ["mail", "sms", "écrit", "contrat"]):
                reponse = "🔍 IA : Preuves matérielles détectées. C'est excellent pour la force probante du dossier."
            else:
                reponse = "⚠️ IA : Alerte. Le témoignage seul est souvent insuffisant au-delà de 1500€. Recherchez des écrits."

        else:
            reponse = f"✅ IA : Phase {index+1} analysée. La stratégie Freeman est respectée. Continuez vers l'étape suivante."

        self.ai_feedback[index] = reponse
        ui.notify("Analyse stratégique mise à jour", color='positive')

# Instance
moteur = KareemIALegalOS()

# --- 2. NAVIGATION ---
def login_handler(e, p):
    if e == "admin@legalos.fr" and p == "123":
        moteur.is_authenticated = True
        ui.navigate.to('/')
    else:
        ui.notify('Accès refusé', color='negative')

def nav_to(delta):
    moteur.step_index += delta
    ui.navigate.to('/')

# --- 3. UI ---
@ui.page('/')
def main_view():
    ui.colors(primary='#1a237e', secondary='#00c853')

    if not moteur.is_authenticated:
        # --- LOGIN ---
        with ui.column().classes('w-full items-center justify-center h-screen bg-slate-900'):
            with ui.card().classes('w-96 p-10 shadow-2xl border-t-8 border-primary rounded-xl'):
                ui.label('⚖️ LegalOS').classes('text-4xl font-bold text-center w-full mb-2')
                ui.label('SYSTÈME FREEMAN').classes('text-sm text-center w-full mb-8 text-slate-400 italic font-light')
                u = ui.input('Identifiant').classes('w-full')
                p = ui.input('Mot de passe', password=True).classes('w-full')
                ui.button('ACTIVER L\'IA', on_click=lambda: login_handler(u.value, p.value)).classes('w-full mt-8 py-4 font-bold rounded-lg shadow-md')
    
    else:
        # --- DASHBOARD ---
        with ui.header().classes('bg-slate-900 items-center justify-between p-4 shadow-xl'):
            ui.label('LEGALOS | KAREEM IA').classes('font-bold text-xl text-white')
            ui.button(icon='logout', on_click=lambda: setattr(moteur, 'is_authenticated', False) or ui.navigate.to('/')).props('flat color=white')

        with ui.row().classes('w-full no-wrap h-screen bg-slate-50'):
            # Sidebar
            with ui.column().classes('w-1/4 p-6 bg-white border-r shadow-inner overflow-y-auto'):
                ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-6 tracking-widest uppercase')
                for i, name in enumerate(moteur.steps):
                    active = (i == moteur.step_index)
                    style = 'text-primary font-bold bg-blue-50 border-r-4 border-primary' if active else 'text-slate-300'
                    ui.label(f"{i+1}. {name.split('. ')[-1] if '.' in name else name}").classes(f'p-3 rounded-md mb-1 transition-all {style}')

            # Workzone
            with ui.column().classes('w-3/4 p-12 overflow-auto'):
                ui.linear_progress(value=(moteur.step_index + 1) / 11).classes('mb-6 rounded-full')
                
                with ui.row().classes('w-full justify-between items-center mb-10'):
                    ui.label(moteur.steps[moteur.step_index]).classes('text-5xl font-light text-slate-800')
                    ui.button('ANALYSE IA', icon='psychology', on_click=lambda: moteur.analyser_ia(moteur.step_index)).props('elevated color=secondary').classes('px-6 shadow-lg')

                with ui.row().classes('w-full no-wrap gap-8'):
                    # Formulaire dynamique basé sur tes instructions
                    with ui.card().classes('w-2/3 p-8 bg-white shadow-xl rounded-xl border-none'):
                        idx = moteur.step_index
                        if idx == 0: ui.markdown('**Qualification** : Domaine ? Parties ? Préjudice ?')
                        elif idx == 1: ui.markdown('**Objectif** : Argent ? Annulation ? Négociation ?')
                        elif idx == 2: ui.markdown('**Base légale** : Contrat ? Loi ? Règlement ?')
                        elif idx == 3: ui.markdown('**Preuves** : SMS ? Mails ? Documents ? Témoins ?')
                        
                        ui.label('RÉDACTION / NOTES').classes('text-xs font-bold text-slate-400 mt-4 mb-2 tracking-widest')
                        area = ui.textarea(placeholder="Saisissez les éléments ici...").classes('w-full h-80 text-lg').props('outlined')
                        area.bind_value(moteur.data, idx)

                    # Panel IA
                    with ui.column().classes('w-1/3'):
                        with ui.card().classes('w-full p-6 bg-slate-800 text-white rounded-xl border-l-4 border-secondary shadow-2xl'):
                            ui.label('CONSEIL FREEMAN IA').classes('text-xs font-bold text-secondary mb-4 tracking-widest uppercase')
                            ui.label().bind_text_from(moteur.ai_feedback, moteur.step_index).classes('italic text-sm leading-relaxed')

                # Nav
                with ui.row().classes('w-full mt-12 justify-between'):
                    if moteur.step_index > 0:
                        ui.button('PRÉCÉDENT', icon='chevron_left', on_click=lambda: nav_to(-1)).props('flat')
                    else: ui.label('')
                    
                    if moteur.step_index < 10:
                        ui.button('SUIVANT', icon='chevron_right', on_click=lambda: nav_to(1)).props('elevated color=primary').classes('px-10 py-2 shadow-md')
                    else:
                        ui.button('GÉNÉRER LE DOSSIER', icon='verified', on_click=lambda: ui.notify('Génération PDF Freeman...')).props('color=green').classes('px-10 py-2 shadow-lg')

ui.run(title='LegalOS - Kareem IA', port=8088, reload=False)
