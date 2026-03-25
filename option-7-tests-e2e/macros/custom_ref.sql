{% macro custom_ref(model_name) %}
  
  {% if var('integration_test_mode', false) %}
    
    {% if model_name == 'dim_entreprises' %}
      {{ return(ref('test_dim_entreprises')) }}
    {% elif model_name == 'dim_commercial' %}
      {{ return(ref('test_dim_commercial')) }}
    {% elif model_name == 'dim_missions' %}
      {{ return(ref('test_dim_missions')) }}
    {% elif model_name == 'fct_missions' %}
      {{ return(ref('test_fct_missions')) }}
    {% elif model_name == 'fct_missions_batch2' %}
      {{ return(ref('test_fct_missions')) }}
    {% else %}
      {{ return(ref(model_name)) }}
    {% endif %}
    
  {% else %}
    
    {{ return(ref(model_name)) }}
    
  {% endif %}
  
{% endmacro %}