{{ config(
    materialized='incremental',
    unique_key=['id_mission', 'date_statut'],
    on_schema_change='fail'
) }}

select
    m.id_mission,
    m.id_commercial,
    c.nom_commercial,
    c.prenom_commercial,
    e.nom_entreprise,
    m.titre_mission,
    s.statut,
    s.date_statut,
    s.commentaire,
    s.source_batch,
    current_timestamp() as loaded_at
from {{ ref('stg_missions') }} m
left join {{ ref('stg_commerciaux') }} c on m.id_commercial = c.id_commercial
left join {{ ref('stg_entreprises') }} e on c.id_entreprise = e.id_entreprise
left join {{ ref('base_statuts_missions') }} s on m.id_mission = s.id_mission

{% if is_incremental() %}
    -- Seulement les nouveaux statuts
    where s.date_statut > (select max(date_statut) from {{ this }})
{% endif %}