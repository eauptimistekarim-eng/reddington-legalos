from nicegui import ui

# --- CONFIGURATION COULEURS "BANQUE/SNCF" ---
ui.colors(primary='#1a237e', secondary='#42a5f5', accent='#00c853')

# --- FONCTION DE RÉPONSE DE KAREEM (À CONNECTER À TES PROMPTS) ---
def analyser_dossier():
    # Ici, on appellera tes fonctions de logic_streamlit.py plus tard
    ui.notify('Kareem lance l\'analyse Reddington...', color='primary')
    chat_box.append('Kareem', 'J\'analyse vos faits. Selon l\'étape 1, votre récit est cohérent. Je prépare la qualification juridique (Étape 2).', 'Kareem', 'https://robohash.org/kareem')

# --- INTERFACE SAAS PRO ---
with ui.header().classes('items-center justify-between bg-primary text-white p-4 shadow-2'):
    with ui.row().classes('items-center'):
        ui.icon('gavel', size='md')
        ui.label('LEGALOS').classes('text-2xl font-bold tracking-tighter')
    ui.badge('SYSTÈME KAREEM V1.0', color='accent').classes('px-4 py-1')

with ui.row().classes('w-full no-wrap h-screen'):
    
    # 1. LE STEPPER VERTICAL (Tes 11 étapes Reddington)
    with ui.column().classes('w-1/4 bg-slate-50 p-6 border-r'):
        ui.label('MÉTHODE REDDINGTON').classes('text-xs font-black text-slate-400 mb-4 tracking-widest')
        with ui.stepper().props('vertical animated gray') as stepper:
            etapes = [
                "Analyse des Faits", "Qualification Juridique", "Inventaire des Preuves",
                "Analyse de la Force Probante", "Ciblage de l'Adversaire", "Stratégie de Recouvrement",
                "Calcul des Préjudices", "Génération de l'Acte", "Vérification Conformité",
                "Protocole d'Envoi", "Suivi & Relances"
            ]
            for i, nom in enumerate(etapes, 1):
                with ui.step(f'{i}. {nom}'):
                    ui.label(f'Instruction en cours pour : {nom}').classes('text-xs italic')
            
            with ui.stepper_navigation():
                ui.button('ÉTAPE SUIVANTE', on_click=stepper.next).props('flat color=primary')
                ui.button('RETOUR', on_click=stepper.previous).props('flat color=grey')

    # 2. ZONE DE TRAVAIL (Saisie et Upload)
    with ui.column().classes('w-2/4 p-10'):
        ui.label('Instruction du Litige').classes('text-3xl font-light text-slate-800 mb-6')
        
        with ui.card().classes('w-full p-6 shadow-xl border-t-4 border-primary'):
            ui.label('Récit des faits').classes('text-sm font-bold text-primary mb-2')
            input_text = ui.textarea(placeholder='Décrivez ici la situation de manière chronologique...').classes('w-full h-48 border-none')
            
        with ui.row().classes('mt-6 w-full justify-between items-center'):
            ui.upload(label='Ajouter des preuves (PDF, Photos)', on_upload=lambda e: ui.notify(f'Fichier {e.name} reçu')).classes('w-64')
            ui.button('LANCER L\'EXPERTISE', on_click=analyser_dossier, icon='psychology').props('size=lg color=primary rounded')

    # 3. LE PANEL KAREEM (Le Chat Expert)
    with ui.column().classes('w-1/4 bg-blue-50 p-6 border-l shadow-inner'):
        ui.label('CONSEILLER KAREEM').classes('text-xs font-black text-blue-800 mb-4 tracking-widest')
        with ui.scroll_area().classes('h-full'):
            chat_box = ui.chat_message('Bonjour Karim. Je suis Kareem. Votre dossier est prêt à être traité par la méthode Reddington. On commence par les faits ?', 
                                    name='Kareem', stamp='En ligne', avatar='https://robohash.org/kareem')

# --- LANCEMENT ---
ui.run(title='LegalOS - Infrastructure IA', port=8080, reload=True)
