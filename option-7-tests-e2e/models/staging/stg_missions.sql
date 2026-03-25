{{ config(
    materialized='table'
) }}

select
    id_mission,
    id_commercial,
    titre_mission,
    description_mission,
    duree_mission_jours,
    salaire_propose_euros,
    competences_requises,
    date_creation,
    current_timestamp() as loaded_at
from {{ custom_ref('dim_missions') }}