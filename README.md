# Pipeline de données dbt + Snowflake — Funnel de recrutement freelance

Pipeline de données complet avec dbt et Snowflake sur un funnel de missions freelance (entreprises, commerciaux, missions, statuts).

Les deux options de la question finale ont été implémentées dans deux dossiers séparés :
- `option-6-sankey/` → Visualisation Sankey
- `option-7-tests-e2e/` → Tests de bout en bout

## Structure

### Option 6 — Visualisation Sankey (`option-6-sankey/`)
```
├── models/
│   ├── staging/                        # Typage et nettoyage des données
│   │   ├── stg_commerciaux.sql
│   │   ├── stg_entreprises.sql
│   │   ├── stg_missions.sql
│   │   └── base_statuts_missions.sql
│   └── marts/
│       ├── fct_missions_incremental.sql  # Chargement incrémental
│       ├── fct_missions_window.sql
│       └── sankey_data.sql               # Données pour le Sankey
├── snapshots/
│   └── statuts_missions_snapshot.sql     # SCD + détection ghosting
├── seeds/                                # Données sources
├── scripts/
│   ├── create_sankey_elegant.py          # Génération du diagramme
│   └── export_sankey_data.py
├── outputs/
│   ├── sankey_missions.html              # Diagramme interactif
│   └── diagramme_sankey.png             # Export image
└── tests/unit/
    └── test_statuts_transformation.sql
```

### Option 7 — Tests de bout en bout (`option-7-tests-e2e/`)
```
├── models/
│   ├── staging/           # Même pipeline que l'option 6
│   └── marts/
│       ├── fct_missions_incremental.sql
│       └── fct_missions_window.sql
├── snapshots/
├── seeds/
│   ├── (données sources)
│   └── integration_tests/
│       ├── input/         # Seeds d'entrée pour les tests E2E
│       └── expected/      # Seeds de sortie attendus
├── macros/
│   ├── custom_ref.sql         # Macro ref surchargée (target dev)
│   ├── integration_tests.sql  # Logique de vérification E2E
│   └── check_schemas.sql
├── scripts/
│   └── run_integration_tests.py
└── tests/unit/
```

## Installation

```bash
pip install dbt-snowflake
dbt deps
dbt seed
dbt build
```

Configurer la connexion Snowflake dans `~/.dbt/profiles.yml`.

> ⚠️ Ne pas committer `profiles.yml` avec vos credentials !

## CI/CD

Pipeline GitLab CI qui lance automatiquement les tests dbt sur chaque push (`dbt test`).

## Auteure

Clara DUBOST — Étudiante Ingénieure Data & IA, Polytech Nantes — 2025
