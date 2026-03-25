{{ config(
    materialized='table'
) }}

select
    id_entreprise,
    nom_entreprise,
    secteur_activite,
    taille_entreprise,
    ville,
    current_timestamp() as loaded_at
from {{ custom_ref('dim_entreprises') }}