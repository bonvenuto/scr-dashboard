select
    data_referencia,
    sigla_uf,   
    sum(valor_carteira_ativa) as carteira_ativa_total,
    sum(valor_carteira_inadimplida) as carteira_inadimplida_total,
    
    round((sum(valor_carteira_inadimplida) / nullif(sum(valor_carteira_ativa), 0)) * 100, 2) as indice_inadimplencia_perc

from {{ ref('stg_scr_data') }}
where sigla_uf is not null 
  and sigla_uf != 'NI'
group by data_referencia, sigla_uf