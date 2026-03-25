{{ config(
    materialized='table'
) }}

-- Utilisation du manifest pour construire les requêtes
{% set ns = namespace(seeds=[]) %}
{% for node_id, node in graph.nodes.items() %}
    {% if node.resource_type == 'seed' and node.name.startswith('fct_missions') %}
        {% set ns.seeds = ns.seeds + [node] %}
    {% endif %}
{% endfor %}

{{ log("Seeds trouvés: " ~ ns.seeds | map(attribute='name') | join(', '), info=true) }}

-- Construction dynamique sans ref()
{% for seed in ns.seeds %}
    select
        id_mission,
        statut,
        date_statut,
        commentaire,
        '{{ seed.name }}' as source_batch,
        current_timestamp() as loaded_at
    from {{ seed.database }}.{{ seed.schema }}.{{ seed.alias }}
    
    {% if not loop.last %}
    union all
    {% endif %}
{% endfor %}