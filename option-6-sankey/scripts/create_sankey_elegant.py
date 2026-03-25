# -*- coding: utf-8 -*-
import os
import sys
import locale

# Configuration complète de l'encodage AVANT tous les autres imports
if sys.platform == "win32":
    # Configurer la console Windows pour UTF-8
    os.system('chcp 65001 > nul')
    
    # Configurer les variables d'environnement
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# Reconfigurer les flux standards avec gestion d'erreur
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    # Pour les versions Python plus anciennes
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

# Configuration locale
try:
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'French_France.1252')
    except locale.Error:
        pass  # Ignorer si la locale n'est pas disponible

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import json

# Ajouter le dossier parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_elegant_sankey(csv_path: str = "../data/sankey_transitions.csv", output_path: str = "../outputs/sankey_missions.html"):
    """
    Crée un diagramme de Sankey élégant et dynamique à partir des données dbt
    Adapté pour fonctionner depuis le dossier scripts/ OU depuis la racine du projet dbt
    """
    
    # Résoudre les chemins relatifs selon l'emplacement d'exécution
    script_dir = Path(__file__).parent
    
    # Si on est dans le dossier scripts/, utiliser les chemins relatifs normaux
    if script_dir.name == 'scripts':
        csv_path = script_dir / csv_path
        output_path = script_dir / output_path
    else:
        # Si on est à la racine, ajuster les chemins
        csv_path = Path("data/sankey_transitions.csv")
        output_path = Path("outputs/sankey_missions.html")
    
    # Charger les données
    if not csv_path.exists():
        print(f"ERREUR: Fichier {csv_path} introuvable !")
        print("INFO: Lancez d'abord votre script d'export : python scripts/export_sankey.py")
        return None
        
    df = pd.read_csv(csv_path)
    print(f"INFO: Chargement de {len(df)} transitions depuis {csv_path.name}")
    
    # Calculer les statistiques automatiquement
    stats = calculate_funnel_stats(df)
    
    # Préparer les données pour le Sankey
    sankey_data = prepare_sankey_data(df)
    
    # Générer le HTML complet
    html_content = generate_html_template(stats, sankey_data)
    
    # Créer le dossier de sortie
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder avec encodage explicite
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"SUCCES: Diagramme créé : {output_path}")
    print_stats_summary(stats)
    
    return str(output_path)

def calculate_funnel_stats(df):
    """Calcule automatiquement les statistiques du funnel"""
    
    # Normaliser les noms de colonnes (flexibilité)
    df.columns = df.columns.str.upper()
    if 'SOURCE_STATUT' not in df.columns:
        # Essayer d'autres variantes
        if 'SOURCE' in df.columns:
            df = df.rename(columns={'SOURCE': 'SOURCE_STATUT', 'TARGET': 'TARGET_STATUT', 'VALUE': 'NB_TRANSITIONS'})
        elif 'FROM_STATUS' in df.columns:
            df = df.rename(columns={'FROM_STATUS': 'SOURCE_STATUT', 'TO_STATUS': 'TARGET_STATUT', 'COUNT': 'NB_TRANSITIONS'})
    
    # Mapping des statuts pour identifier les finaux
    final_success = ['ACCEPTÉ', 'ACCEPTÉE', 'ACCEPTED', 'WON']
    final_failure = ['REFUSÉ', 'REFUSÉE', 'REFUSED', 'REJECTED', 'ABANDONNÉ', 'ABANDONED', 'LOST']
    
    # Calculer les métriques
    total_transitions = df['NB_TRANSITIONS'].sum()
    success_transitions = df[df['TARGET_STATUT'].str.upper().isin(final_success)]['NB_TRANSITIONS'].sum()
    failure_transitions = df[df['TARGET_STATUT'].str.upper().isin(final_failure)]['NB_TRANSITIONS'].sum()
    
    # Estimer le nombre de missions uniques
    nouveau_transitions = df[df['SOURCE_STATUT'].str.upper().isin(['NOUVEAU', 'NEW', 'CREATED'])]['NB_TRANSITIONS'].sum()
    missions_estimate = nouveau_transitions if nouveau_transitions > 0 else max(df['NB_TRANSITIONS'])
    
    # Calculer le taux de succès
    total_final = success_transitions + failure_transitions
    success_rate = round((success_transitions / total_final) * 100) if total_final > 0 else 0
    
    return {
        'total_missions': missions_estimate,
        'total_transitions': total_transitions,
        'success_count': success_transitions,
        'failure_count': failure_transitions,
        'success_rate': success_rate,
        'in_progress': missions_estimate - success_transitions - failure_transitions
    }

def prepare_sankey_data(df):
    """Prépare les données pour le diagramme de Sankey"""
    
    # Normaliser les colonnes
    df.columns = df.columns.str.upper()
    
    # Créer la liste unique des statuts
    all_statuts = list(set(df['SOURCE_STATUT'].tolist() + df['TARGET_STATUT'].tolist()))
    
    # Ordonner logiquement les statuts (français et anglais)
    status_order = [
        'NOUVEAU', 'NEW', 'CREATED',
        'PREMIER CONTACT', 'FIRST CONTACT', 'CONTACTED',
        'ENTRETIEN PLANIFIÉ', 'INTERVIEW PLANNED', 'SCHEDULED',
        'ENTRETIEN RÉALISÉ', 'INTERVIEW DONE', 'INTERVIEWED',
        'PROPOSITION ENVOYÉE', 'PROPOSAL SENT', 'PROPOSED',
        'NÉGOCIATION', 'NEGOTIATION', 'NEGOTIATING',
        'ACCEPTÉ', 'ACCEPTÉE', 'ACCEPTED', 'WON',
        'REFUSÉ', 'REFUSÉE', 'REFUSED', 'REJECTED',
        'ABANDONNÉ', 'ABANDONED', 'LOST'
    ]
    
    # Trier selon l'ordre logique quand possible
    ordered_statuts = []
    for status in status_order:
        if status in all_statuts:
            ordered_statuts.append(status)
    
    # Ajouter les statuts restants
    for status in all_statuts:
        if status not in ordered_statuts:
            ordered_statuts.append(status)
    
    statut_to_index = {statut: idx for idx, statut in enumerate(ordered_statuts)}
    
    # Préparer les indices et valeurs
    source_indices = [statut_to_index[statut] for statut in df['SOURCE_STATUT']]
    target_indices = [statut_to_index[statut] for statut in df['TARGET_STATUT']]
    values = df['NB_TRANSITIONS'].tolist()
    
    # Couleurs pour chaque statut (plus de variantes)
    colors = [
        "#3498db",  # Nouveau/New
        "#1abc9c",  # Premier contact
        "#9b59b6",  # Entretien planifié
        "#8e44ad",  # Entretien réalisé
        "#f39c12",  # Proposition envoyée
        "#e67e22",  # Négociation
        "#27ae60",  # Accepté
        "#27ae60",  # Acceptée
        "#e74c3c",  # Refusé
        "#e74c3c",  # Refusée
        "#95a5a6",  # Abandonné
        "#34495e",  # Autre
        "#16a085",  # Autre
        "#8e44ad",  # Autre
        "#d35400",  # Autre
        "#c0392b"   # Autre
    ]
    
    # Assurer qu'on a assez de couleurs
    while len(colors) < len(ordered_statuts):
        colors.extend(["#34495e", "#16a085", "#8e44ad", "#d35400", "#c0392b"])
    
    node_colors = colors[:len(ordered_statuts)]
    
    # Couleurs des liens avec transparence
    link_colors = []
    for source, target in zip(df['SOURCE_STATUT'], df['TARGET_STATUT']):
        target_upper = target.upper()
        if target_upper in ['ACCEPTÉ', 'ACCEPTÉE', 'ACCEPTED', 'WON']:
            link_colors.append("rgba(39, 174, 96, 0.4)")  # Vert pour succès
        elif target_upper in ['REFUSÉ', 'REFUSÉE', 'REFUSED', 'REJECTED']:
            link_colors.append("rgba(231, 76, 60, 0.4)")  # Rouge pour échec
        elif target_upper in ['ABANDONNÉ', 'ABANDONED', 'LOST']:
            link_colors.append("rgba(149, 165, 166, 0.4)")  # Gris pour abandon
        else:
            link_colors.append("rgba(52, 152, 219, 0.4)")  # Bleu par défaut
    
    return {
        'labels': ordered_statuts,
        'colors': node_colors,
        'source': source_indices,
        'target': target_indices,
        'values': values,
        'link_colors': link_colors
    }

def generate_html_template(stats, sankey_data):
    """Génère le template HTML complet avec les données"""
    
    # Convertir les données en JSON pour JavaScript
    sankey_json = json.dumps(sankey_data, ensure_ascii=False)
    
    html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Funnel des Missions - Diagramme de Sankey</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.26.0/plotly.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        h1 {{
           font-size: 3.2em;
            font-weight: 700;
            margin-bottom: 15px;
            color: #2c3e50;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .subtitle {{
            color: #6c757d;
            font-size: 1.3em;
            font-weight: 400;
            margin-bottom: 15px;
        }}
        
        .data-info {{
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid rgba(26, 188, 156, 0.2);
            font-size: 1em;
            color: #2c3e50;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }}
        
        .stat-card {{
            padding: 30px 20px;
            border-radius: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            cursor: pointer;
            border: 2px solid rgba(255,255,255,0.2);
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: inherit;
            z-index: -1;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-card:hover::before {{
            transform: scale(1.1);
        }}
        
        .stat-card.info {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }}
        
        .stat-card.success {{
            background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        }}
        
        .stat-card.danger {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        }}
        
        .stat-number {{
            font-size: 3.5em;
            font-weight: 800;
            color: #2c3e50;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: block;
        }}
        
        .stat-label {{
            font-size: 1.1em;
            color: #34495e;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        #sankeyDiv {{
            width: 100%;
            height: 700px;
            margin: 40px 0;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            background: white;
        }}
        
        .analysis {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 35px;
            border-radius: 20px;
            margin-top: 40px;
            border-left: 6px solid #667eea;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        }}
        
        .analysis h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 600;
        }}
        
        .analysis p {{
            color: #5d6d7e;
            line-height: 1.8;
            margin-bottom: 15px;
            font-size: 1.05em;
        }}
        
        .analysis strong {{
            color: #2c3e50;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}
            
            h1 {{
                font-size: 2.5em;
            }}
            
            .stats {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }}
            
            .stat-card {{
                padding: 20px 15px;
            }}
            
            .stat-number {{
                font-size: 2.5em;
            }}
            
            #sankeyDiv {{
                height: 500px;
            }}
        }}
        
        .animate-in {{
            animation: slideInUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        
        @keyframes slideInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Funnel des Missions</h1>
            <p class="subtitle">Analyse dynamique du parcours commercial</p>
            
            <div class="data-info">
                <strong>📊 Données dbt en temps réel :</strong> {stats['total_transitions']} transitions analysées automatiquement
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card info animate-in">
                <div class="stat-number">{stats['total_missions']}</div>
                <div class="stat-label">Total Missions</div>
            </div>
            <div class="stat-card success animate-in">
                <div class="stat-number">{stats['success_rate']}%</div>
                <div class="stat-label">Taux Succès</div>
            </div>
            <div class="stat-card success animate-in">
                <div class="stat-number">{stats['success_count']}</div>
                <div class="stat-label">Acceptées</div>
            </div>
            <div class="stat-card danger animate-in">
                <div class="stat-number">{stats['failure_count']}</div>
                <div class="stat-label">Perdues</div>
            </div>
            <div class="stat-card info animate-in">
                <div class="stat-number">{max(0, stats['in_progress'])}</div>
                <div class="stat-label">En Cours</div>
            </div>
        </div>

        <div id="sankeyDiv"></div>

        <div class="analysis">
            <h3>📈 Analyse Automatique</h3>
            {generate_dynamic_analysis(stats)}
        </div>
    </div>

    <script>
        // Données dynamiques depuis dbt
        const sankeyData = {sankey_json};
        
        const data = [{{
            type: "sankey",
            orientation: "h",
            arrangement: "snap",
            node: {{
                pad: 20,
                thickness: 30,
                line: {{
                    color: "rgba(0,0,0,0.3)",
                    width: 2
                }},
                label: sankeyData.labels,
                color: sankeyData.colors,
                font: {{
                    size: 14,
                    color: "#2c3e50",
                    family: "Segoe UI, sans-serif"
                }}
            }},
            link: {{
                source: sankeyData.source,
                target: sankeyData.target,
                value: sankeyData.values,
                color: sankeyData.link_colors,
                line: {{
                    color: "rgba(0,0,0,0.2)",
                    width: 1
                }}
            }}
        }}];

        const layout = {{
            font: {{ 
                size: 16,
                family: "Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif",
                color: "#2c3e50"
            }},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: {{ l: 60, r: 60, t: 40, b: 40 }}
        }};

        const config = {{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d', 'pan2d'],
            responsive: true,
            toImageButtonOptions: {{
                format: 'png',
                filename: 'funnel_missions_sankey',
                height: 700,
                width: 1200,
                scale: 2
            }}
        }};

        Plotly.newPlot('sankeyDiv', data, layout, config);
        
        // Animation séquentielle des cartes
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.stat-card');
            cards.forEach((card, index) => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                setTimeout(() => {{
                    card.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }}, index * 150 + 500);
            }});
        }});
    </script>
</body>
</html>"""
    
    return html_template

def generate_dynamic_analysis(stats):
    """Génère une analyse textuelle dynamique basée sur les stats"""
    
    analysis_parts = []
    
    # Analyse du taux de succès
    if stats['success_rate'] >= 60:
        analysis_parts.append("<p><strong>✅ Performance excellente :</strong> "
                             f"Taux de conversion de {stats['success_rate']}% avec {stats['success_count']} missions acceptées. "
                             "Votre processus commercial est très efficace.</p>")
    elif stats['success_rate'] >= 40:
        analysis_parts.append("<p><strong>🟡 Performance correcte :</strong> "
                             f"Taux de conversion de {stats['success_rate']}% ({stats['success_count']} acceptées). "
                             "Des améliorations sont possibles pour optimiser le funnel.</p>")
    else:
        analysis_parts.append("<p><strong>⚠️ Performance à améliorer :</strong> "
                             f"Taux de conversion de {stats['success_rate']}%. "
                             "Une analyse approfondie du processus commercial est recommandée.</p>")
    
    # Analyse des missions perdues
    if stats['failure_count'] > stats['success_count']:
        analysis_parts.append("<p><strong>🔍 Point d'attention :</strong> "
                             f"Plus de missions perdues ({stats['failure_count']}) que d'acceptées. "
                             "Analysez les raisons d'échec pour améliorer la qualification.</p>")
    
    # Analyse des missions en cours
    if stats['in_progress'] > 0:
        analysis_parts.append(f"<p><strong>⏳ Suivi nécessaire :</strong> "
                             f"{stats['in_progress']} mission(s) en cours nécessitent un suivi attentif "
                             "pour maximiser les conversions.</p>")
    
    # Recommandations intelligentes
    recommendations = []
    if stats['failure_count'] > stats['success_count']:
        recommendations.append("améliorer la qualification initiale des prospects")
    if stats['success_rate'] < 50:
        recommendations.append("revoir la stratégie de proposition commerciale")
    if stats['in_progress'] > stats['total_missions'] * 0.2:
        recommendations.append("accélérer le suivi des opportunités en cours")
    
    if recommendations:
        rec_text = ", ".join(recommendations)
        analysis_parts.append(f"<p><strong>🎯 Recommandations :</strong> {rec_text.capitalize()}.</p>")
    else:
        analysis_parts.append("<p><strong>🎯 Félicitations :</strong> "
                             "Votre funnel fonctionne bien ! Maintenez cette performance.</p>")
    
    return "".join(analysis_parts)

def print_stats_summary(stats):
    """Affiche un résumé des statistiques"""
    print("\nRESUME du funnel :")
    print(f"   - Total missions : {stats['total_missions']}")
    print(f"   - Taux de succès : {stats['success_rate']}%")
    print(f"   - Acceptées : {stats['success_count']}")
    print(f"   - Perdues : {stats['failure_count']}")
    print(f"   - En cours : {max(0, stats['in_progress'])}")

if __name__ == "__main__":
    print("Générateur de Sankey Élégant pour dbt")
    print("=" * 50)
    
    # Vérifier qu'on est dans un projet dbt (deux façons possibles)
    if not (Path("../models").exists() or Path("models").exists()):
        print("ATTENTION: Ce script doit être lancé depuis le dossier scripts/ OU depuis la racine du projet dbt")
        print("Structure attendue :")
        print("   mon_projet_dbt/")
        print("   ├── scripts/  ← Vous êtes ici")
        print("   ├── models/")
        print("   └── data/")
        print("OU lancez depuis la racine du projet")
        sys.exit(1)
    
    # Générer le diagramme
    result = create_elegant_sankey()
    
    if result:
        print(f"\nSUCCES: Diagramme généré avec succès !")
        print(f"Ouvrez {result} dans votre navigateur")
    else:
        print("\nERREUR lors de la génération")
        print("Assurez-vous d'avoir exporté les données avec votre script d'export")