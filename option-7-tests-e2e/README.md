# TP dbt Snowflake - Tests de Bout en Bout

Pipeline de données avec dbt et Snowflake pour analyser le funnel de missions d'un freelance, avec focus sur les **tests d'intégration bout en bout** (Partie 7 du TP).

## Objectif Principal

Développement d'un **système complet de tests d'intégration** pour valider automatiquement que les transformations dbt produisent exactement les résultats attendus sur l'ensemble du pipeline.

## Architecture

```
📦 BRONZE (CSV seeds) → 📦 SILVER (dbt models) → 🧪 Tests Intégration
```

### Sources de Données
- **4 tables principales** : entreprises, commerciaux, missions, statuts
- **Pipeline en 3 couches** : Bronze → Silver → Marts
- **Auto-détection des batches** : Union automatique des fichiers `fct_missions*`

### Innovation : Tests de Bout en Bout
- **Mini datasets** pour tests rapides (2-5 lignes vs 100+ en prod)
- **Basculement automatique** prod/test via variables dbt
- **Validation automatique** des transformations avec comparaison exacte

## Utilisation

### Tests d'intégration complets

```bash
# 1. Chargement des mini datasets de test
dbt seed --select integration_tests

# 2. Exécution en mode test
dbt run --vars '{"integration_test_mode": true}'

# 3. Validation automatique
dbt run-operation test_integration_pipeline
```

### Pipeline production

```bash
# Pipeline complet production
dbt seed    # Chargement données réelles
dbt run     # Transformations
dbt test    # Tests de qualité (21 tests)
```

## Structure du Projet

```
├── models/
│   ├── staging/              # Tables nettoyées (SILVER)
│   │   ├── stg_entreprises.sql
│   │   ├── stg_commerciaux.sql
│   │   ├── stg_missions.sql
│   │   └── base_statuts_missions.sql
│   └── marts/               # Tables analytiques
│       └── fct_missions_incremental.sql
├── seeds/
│   ├── dim_entreprises.csv         # Données production
│   ├── dim_commercial.csv
│   ├── dim_missions.csv
│   ├── fct_missions*.csv
│   └── integration_tests/          # 🎯 INNOVATION PRINCIPALE
│       ├── input/                  # Mini datasets (2-5 lignes)
│       │   ├── test_dim_entreprises.csv
│       │   ├── test_dim_commercial.csv
│       │   ├── test_dim_missions.csv
│       │   └── test_fct_missions.csv
│       └── expected/              # Résultats attendus
│           ├── expected_stg_entreprises.csv
│           ├── expected_stg_commerciaux.csv
│           ├── expected_stg_missions.csv
│           └── expected_base_statuts_missions.csv
├── macros/
│   ├── custom_ref.sql             # Basculement prod/test
│   └── test_integration_pipeline.sql  # Validation automatique
├── .gitlab-ci.yml                 # Pipeline CI/CD avec tests
└── dbt_project.yml
```

## Tests Implémentés

### Tests de Qualité (21 tests)
- **Unicité** : Clés primaires et emails
- **Non-nullité** : Colonnes obligatoires
- **Relations** : Clés étrangères entre tables
- **Valeurs acceptées** : Énumérations métier
- **Logique métier** : Contraintes business (salaires > 0)

### Tests d'Intégration (Innovation Principale)
- **4/4 tables validées** avec succès
- **Comparaison exacte** des résultats via requêtes `EXCEPT`
- **Basculement automatique** entre datasets prod/test
- **Intégration CI/CD** pour validation continue

## Fonctionnalités Avancées

### Système de Basculement Prod/Test

```sql
-- Macro custom_ref.sql
{% macro custom_ref(model_name) %}
  {% if var('integration_test_mode', false) %}
    {% if model_name == 'dim_entreprises' %}
      {{ return(ref('test_dim_entreprises')) }}
    {% endif %}
  {% else %}
    {{ return(ref(model_name)) }}
  {% endif %}
{% endmacro %}
```

### Auto-détection des Batches

Union automatique de tous les fichiers `fct_missions*` détectés dans le projet, permettant l'ajout de nouveaux batches sans modification de code.

### Pipeline CI/CD GitLab

Pipeline en 4 étapes avec tests d'intégration automatiques :
1. **Build** : `dbt seed` + `dbt run`
2. **Test** : `dbt test` (qualité)
3. **Docs** : `dbt docs generate`
4. **Integration Tests** : Validation bout en bout

## Résultats Obtenus

```
🧪 TESTS D'INTÉGRATION - PIPELINE COMPLET
==================================================
📊 Test de stg_entreprises...
✅ SUCCÈS: stg_entreprises correspond parfaitement !
📊 Test de stg_commerciaux...
✅ SUCCÈS: stg_commerciaux correspond parfaitement !
📊 Test de stg_missions...
✅ SUCCÈS: stg_missions correspond parfaitement !
📊 Test de base_statuts_missions...
✅ SUCCÈS: base_statuts_missions correspond parfaitement !

🎉 RÉSULTAT FINAL : 4/4 tables validées avec succès !
```

## Technologies Utilisées

- **dbt** : Transformations, tests, macros, variables
- **Snowflake** : Data warehouse cloud (BRONZE/SILVER)
- **GitLab CI** : Pipeline d'intégration continue
- **SQL** : Requêtes de transformation et validation

## Valeur Pédagogique

Ce projet illustre les **bonnes pratiques modernes** des pipelines de données :
- **Tests de qualité** systématiques
- **Tests d'intégration** pour validation bout en bout
- **CI/CD** pour automatisation et qualité continue
- **Gestion des environnements** (prod/test/dev)

## Applicabilité Professionnelle

Solution directement utilisable en entreprise pour :
- Valider les transformations complexes
- Éviter les régressions sur les pipelines de données
- Assurer la qualité des livraisons data
- Automatiser les tests dans les process DevOps

---

**Auteur** : Clara DUBOST  
**Formation** : Ingénieur 4ème année - Ingénierie des Données et IA  
**Cours** : DataOPS - Université de Nantes  
**Année** : 2025

**Focus** : Tests d'intégration et qualité des pipelines de données