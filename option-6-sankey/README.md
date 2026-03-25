# TP dbt Snowflake - Pipeline de Données et Visualisation Sankey

Pipeline de données avec dbt et Snowflake pour analyser le funnel de missions d'un freelance, avec génération automatique d'un diagramme de Sankey interactif.

## Fonctionnalités

* **Pipeline dbt complet** avec tests de qualité
* **Export automatique** depuis Snowflake
* **Diagramme de Sankey interactif** avec Plotly.js
* **Pipeline CI/CD GitLab** pour l'intégration continue
* **Auto-détection des batches** de données
* **Métriques automatiques** (taux de conversion, analyses)

## Architecture

```txt
📦 BRONZE (CSV) → 📦 SILVER (dbt models) → 📊 Sankey HTML
```

* **Sources** : 5 fichiers CSV (entreprises, commerciaux, missions, statuts)
* **Transformations** : Models dbt avec tests de qualité
* **Output** : Diagramme interactif avec analyses automatiques

## Utilisation

### Pipeline complet automatisé

```bash
python sankey_auto.py
```

### Étapes manuelles

```bash
# 1. Charger les données
dbt seed

# 2. Transformations
dbt run

# 3. Tests qualité
dbt test

# 4. Export et génération Sankey
python scripts/export_sankey_data.py
python scripts/create_sankey_elegant.py
```

## Structure

```txt
├── models/
│   ├── staging/           # Tables nettoyées
│   └── marts/            # Données finales (sankey_data)
├── seeds/                # Fichiers CSV sources
├── scripts/              # Automatisation Python
├── outputs/              # Diagramme HTML généré
└── sankey_auto.py        # Pipeline automatique
```

## Tests Implémentés

* **Tests dbt** : unique, not_null, relationships, accepted_values
* **Test personnalisé** : Vérification intégrité des transitions
* **Pipeline CI/CD** : Tests automatiques sur GitLab

## Résultat

Génère automatiquement :

* **Diagramme de Sankey interactif** (`outputs/sankey_missions.html`)
* **Métriques clés** : Taux de conversion, missions en cours
* **Analyse automatique** : Recommandations basées sur les données

## Technologies

* **dbt** : Transformations et tests SQL
* **Snowflake** : Data warehouse cloud
* **Python** : Pandas, Plotly pour visualisation
* **GitLab CI** : Pipeline d'intégration continue

---

**Auteur** : Clara DUBOST , Sirine DAKHLI

**Cours** : DataOPS - Université de Nantes

**Année** : 2025
