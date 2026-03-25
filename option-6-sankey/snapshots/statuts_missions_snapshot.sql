{% snapshot statuts_missions_snapshot %}
    {{
        config(
            target_database='SILVER',
            target_schema='snapshots',
            unique_key='id_mission',
            strategy='timestamp',
            updated_at='date_statut'
        )
    }}

    select
        id_mission,
        statut,
        date_statut,
        commentaire,
        case
            when statut in ('Accepté', 'Refusé') then true
            else false
        end as is_statut_final,
        case
            when statut not in ('Accepté', 'Refusé', 'Abandonné')
            and datediff(day, date_statut, current_date()) > 14
            then true
            else false
        end as is_ghost,
        current_timestamp() as loaded_at
    from {{ ref('base_statuts_missions') }}

{% endsnapshot %}