select
    data_referencia,
    natureza_ocupacao,
    sum(valor_carteira_ativa) as carteira_ativa_total,
    sum(valor_carteira_inadimplida) as carteira_inadimplida_total,
    sum(valor_ativo_problematico) as ativo_problematico_total,
    round((sum(valor_carteira_inadimplida) / nullif(sum(valor_carteira_ativa), 0)) * 100, 2) as indice_inadimplencia_perc,
    round((sum(valor_ativo_problematico) / nullif(sum(valor_carteira_ativa), 0)) * 100, 2) as indice_ativo_problematico_perc

from {{ ref('stg_scr_data') }}
where faixa_rendimento_porte is not null
group by data_referencia,
natureza_ocupacao