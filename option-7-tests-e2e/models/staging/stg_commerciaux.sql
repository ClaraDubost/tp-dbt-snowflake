{{ config(
    materialized='table'
) }}

select
    id_commercial,
    id_entreprise,
    nom_commercial,
    prenom_commercial,
    email_commercial,
    telephone,
    current_timestamp() as loaded_at
from {{ custom_ref('dim_commercial') }}