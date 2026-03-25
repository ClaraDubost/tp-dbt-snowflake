with statuts_ordered as (
    select
        id_mission,
        statut,
        date_statut,
        row_number() over (partition by id_mission order by date_statut) as step_number
    from {{ ref('base_statuts_missions') }}
),
transitions as (
    select
        s1.statut as source_statut,
        s2.statut as target_statut,
        count(*) as nb_transitions
    from statuts_ordered s1
    join statuts_ordered s2
        on s1.id_mission = s2.id_mission
        and s2.step_number = s1.step_number + 1
    group by s1.statut, s2.statut
)
select
    source_statut,
    target_statut,
    nb_transitions
from transitions
order by nb_transitions desc