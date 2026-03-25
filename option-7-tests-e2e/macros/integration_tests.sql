{% macro test_integration_pipeline() %}
  
  {{ log("🧪 TESTS D'INTÉGRATION - PIPELINE COMPLET", info=true) }}
  {{ log("=" * 50, info=true) }}
  
  -- Test 1: stg_entreprises
  {% set query1 %}
    select 
      'stg_entreprises' as table_name,
      count(*) as diff_count
    from (
      select id_entreprise, nom_entreprise, secteur_activite, taille_entreprise, ville
      from {{ ref('stg_entreprises') }}
      except 
      select id_entreprise, nom_entreprise, secteur_activite, taille_entreprise, ville
      from {{ ref('expected_stg_entreprises') }}
      
      union all
      
      select id_entreprise, nom_entreprise, secteur_activite, taille_entreprise, ville
      from {{ ref('expected_stg_entreprises') }}
      except
      select id_entreprise, nom_entreprise, secteur_activite, taille_entreprise, ville
      from {{ ref('stg_entreprises') }}
    ) as differences
    having count(*) > 0
  {% endset %}
  
  {{ log("📊 Test de stg_entreprises...", info=true) }}
  {% set results1 = run_query(query1) %}
  
  {% if results1.rows|length > 0 %}
    {{ log("❌ ÉCHEC: stg_entreprises - " ~ results1.rows[0][1] ~ " différences", info=true) }}
  {% else %}
    {{ log("✅ SUCCÈS: stg_entreprises correspond parfaitement !", info=true) }}
  {% endif %}
  
  -- Test 2: stg_commerciaux
  {% set query2 %}
    select 
      'stg_commerciaux' as table_name,
      count(*) as diff_count
    from (
      select id_commercial, id_entreprise, nom_commercial, prenom_commercial, email_commercial, telephone
      from {{ ref('stg_commerciaux') }}
      except 
      select id_commercial, id_entreprise, nom_commercial, prenom_commercial, email_commercial, telephone
      from {{ ref('expected_stg_commerciaux') }}
      
      union all
      
      select id_commercial, id_entreprise, nom_commercial, prenom_commercial, email_commercial, telephone
      from {{ ref('expected_stg_commerciaux') }}
      except
      select id_commercial, id_entreprise, nom_commercial, prenom_commercial, email_commercial, telephone
      from {{ ref('stg_commerciaux') }}
    ) as differences
    having count(*) > 0
  {% endset %}
  
  {{ log("📊 Test de stg_commerciaux...", info=true) }}
  {% set results2 = run_query(query2) %}
  
  {% if results2.rows|length > 0 %}
    {{ log("❌ ÉCHEC: stg_commerciaux - " ~ results2.rows[0][1] ~ " différences", info=true) }}
  {% else %}
    {{ log("✅ SUCCÈS: stg_commerciaux correspond parfaitement !", info=true) }}
  {% endif %}
  
  -- Test 3: stg_missions
  {% set query3 %}
    select 
      'stg_missions' as table_name,
      count(*) as diff_count
    from (
      select id_mission, id_commercial, titre_mission, description_mission, duree_mission_jours, salaire_propose_euros, competences_requises, date_creation
      from {{ ref('stg_missions') }}
      except 
      select id_mission, id_commercial, titre_mission, description_mission, duree_mission_jours, salaire_propose_euros, competences_requises, date_creation
      from {{ ref('expected_stg_missions') }}
      
      union all
      
      select id_mission, id_commercial, titre_mission, description_mission, duree_mission_jours, salaire_propose_euros, competences_requises, date_creation
      from {{ ref('expected_stg_missions') }}
      except
      select id_mission, id_commercial, titre_mission, description_mission, duree_mission_jours, salaire_propose_euros, competences_requises, date_creation
      from {{ ref('stg_missions') }}
    ) as differences
    having count(*) > 0
  {% endset %}
  
  {{ log("📊 Test de stg_missions...", info=true) }}
  {% set results3 = run_query(query3) %}
  
  {% if results3.rows|length > 0 %}
    {{ log("❌ ÉCHEC: stg_missions - " ~ results3.rows[0][1] ~ " différences", info=true) }}
  {% else %}
    {{ log("✅ SUCCÈS: stg_missions correspond parfaitement !", info=true) }}
  {% endif %}
  
  -- Test 4: base_statuts_missions
  {% set query4 %}
    select 
      'base_statuts_missions' as table_name,
      count(*) as diff_count
    from (
      select id_mission, statut, date_statut, commentaire
      from {{ ref('base_statuts_missions') }}
      except 
      select id_mission, statut, date_statut, commentaire
      from {{ ref('expected_base_statuts_missions') }}
      
      union all
      
      select id_mission, statut, date_statut, commentaire
      from {{ ref('expected_base_statuts_missions') }}
      except
      select id_mission, statut, date_statut, commentaire
      from {{ ref('base_statuts_missions') }}
    ) as differences
    having count(*) > 0
  {% endset %}
  
  {{ log("📊 Test de base_statuts_missions...", info=true) }}
  {% set results4 = run_query(query4) %}
  
  {% if results4.rows|length > 0 %}
    {{ log("❌ ÉCHEC: base_statuts_missions - " ~ results4.rows[0][1] ~ " différences", info=true) }}
  {% else %}
    {{ log("✅ SUCCÈS: base_statuts_missions correspond parfaitement !", info=true) }}
  {% endif %}
  
  {{ log("", info=true) }}
  {{ log("🎉 TESTS D'INTÉGRATION TERMINÉS !", info=true) }}

{% endmacro %}