with

ultima_ref as (
select   
    data_referencia,
    sum(valor_carteira_ativa) as carteira_ativa_total,
    sum(valor_carteira_inadimplida) as carteira_inadimplida_total,
    sum(valor_ativo_problematico) as ativo_problematico_total,
    
    round((sum(valor_carteira_inadimplida) / nullif(sum(valor_carteira_ativa), 0)) * 100, 2) as indice_inadimplencia_perc,
    round((sum(valor_ativo_problematico) / nullif(sum(valor_carteira_ativa), 0)) * 100, 2) as indice_ativo_problematico_perc

from {{ ref('stg_scr_data') }}
group by data_referencia
)

select
atual.data_referencia
, atual.carteira_ativa_total
, atual.carteira_inadimplida_total
, atual.ativo_problematico_total
, atual.indice_inadimplencia_perc
, atual.indice_ativo_problematico_perc
, ((atual.carteira_inadimplida_total/anterior.carteira_inadimplida_total)-1)*100 as variavao_carteira_inadimplida_total
, ((atual.carteira_ativa_total/anterior.carteira_ativa_total)-1)*100 as variavao_carteira_ativa_total
, ((atual.ativo_problematico_total/anterior.ativo_problematico_total)-1)*100 as variavao_ativo_problematico_total
, ((atual.indice_inadimplencia_perc/anterior.indice_inadimplencia_perc)-1)*100 as variavao_indice_inadimplencia_perc
, ((atual.indice_ativo_problematico_perc/anterior.indice_ativo_problematico_perc)-1)*100 as variavao_indice_ativo_problematico_perc
from ultima_ref as atual
left join ultima_ref as anterior
on date_trunc('month', CAST(atual.data_referencia AS DATE)) = date_trunc('month', CAST(anterior.data_referencia AS DATE)) + INTERVAL 1 MONTH