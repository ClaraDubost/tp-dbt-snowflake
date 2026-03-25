-- Test unitaire pour la transformation des statuts
-- Vérifie qu'on n'a pas de missions orphelines

select distinct id_mission
from {{ ref('base_statuts_missions') }}
except
select id_mission
from {{ ref('stg_missions') }}

-- Si aucune ligne retournée = pas de missions orphelines = test passe 