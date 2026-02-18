select
    data_referencia,
    tipo_cliente,
    faixa_rendimento_porte,   
    sum(valor_vencer_curto_prazo) as total_curto_prazo,
    sum(valor_vencer_longo_prazo) as total_longo_prazo
from {{ ref('stg_scr_data') }}
where faixa_rendimento_porte is not null
group by data_referencia,
    tipo_cliente,
    faixa_rendimento_porte