{% macro check_table_schemas() %}

  {% set tables_to_check = [
    ('stg_entreprises', 'expected_stg_entreprises'),
    ('stg_commerciaux', 'expected_stg_commerciaux'),
    ('stg_missions', 'expected_stg_missions'),
    ('base_statuts_missions', 'expected_base_statuts_missions'),
  ] %}

  {% for actual_table, expected_table in tables_to_check %}
    
    {{ log("🔍 Vérification de " ~ actual_table, info=true) }}
    
    {# Colonnes de la table actuelle #}
    {% set actual_query %}
      describe table {{ ref(actual_table) }}
    {% endset %}
    
    {# Colonnes de la table attendue #}  
    {% set expected_query %}
      describe table {{ ref(expected_table) }}
    {% endset %}
    
    {% set actual_cols = run_query(actual_query) %}
    {% set expected_cols = run_query(expected_query) %}
    
    {{ log("📊 Table actuelle: " ~ actual_cols.rows|length ~ " colonnes", info=true) }}
    {{ log("📋 Table attendue: " ~ expected_cols.rows|length ~ " colonnes", info=true) }}
    
    {% for row in actual_cols.rows %}
      {{ log("  - " ~ row[0] ~ " (" ~ row[1] ~ ")", info=true) }}
    {% endfor %}
    
    {{ log("", info=true) }}
    
  {% endfor %}

{% endmacro %}