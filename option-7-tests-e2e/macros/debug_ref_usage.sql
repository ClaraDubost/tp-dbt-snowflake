{% macro debug_ref_usage() %}

  {{ log("🔍 Test de la macro ref() en mode test", info=true) }}
  {{ log("Mode test actuel: " ~ var('integration_test_mode', false), info=true) }}
  
  {% if var('integration_test_mode', false) %}
    {{ log("✅ Mode test activé", info=true) }}
  {% else %}
    {{ log("❌ Mode production", info=true) }}
  {% endif %}
  
  {% set query %}
    select count(*) as nb_lignes 
    from {{ ref('base_statuts_missions') }}
  {% endset %}
  
  {% set results = run_query(query) %}
  
  {{ log("📊 Nombre de lignes dans base_statuts_missions: " ~ results.rows[0][0], info=true) }}
  
  {% if var('integration_test_mode', false) %}
    {{ log("🎯 En mode test, ça devrait être 5 lignes", info=true) }}
  {% else %}
    {{ log("🎯 En mode prod, ça devrait être plus que 5 lignes", info=true) }}
  {% endif %}

{% endmacro %}