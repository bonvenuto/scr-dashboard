with source as (
    select * from {{ source('raw_scr', 'scr_dados_anuais') }}
),

renamed as (
    select
        strftime(cast("data_base" as date), '%Y-%m-%d') as data_referencia,
        cast("uf" as varchar) as sigla_uf,
        cast("segmento" as varchar) as segmento_instituicao,
        cast("cliente" as varchar) as tipo_cliente,
        cast("porte" as varchar) as faixa_rendimento_porte,
        cast("cnae_ocupacao" as varchar) as natureza_ocupacao,
        cast("modalidade" as varchar) as modalidade_credito,
        cast(replace("carteira_ativa", ',', '.') as double) as valor_carteira_ativa,
        cast(replace("carteira_inadimplencia", ',', '.') as double) as valor_carteira_inadimplida,
        cast(replace("ativo_problematico", ',', '.') as double) as valor_ativo_problematico,
        cast(replace("a_vencer_ate_90_dias", ',', '.') as double) as valor_vencer_curto_prazo,
        cast(replace("a_vencer_de_361_ate_1080_dias", ',', '.') as double) +
        cast(replace("a_vencer_de_1081_ate_1800_dias", ',', '.') as double) +
        cast(replace("a_vencer_de_1801_ate_5400_dias", ',', '.') as double) +
        cast(replace("a_vencer_acima_de_5400_dias", ',', '.') as double) as valor_vencer_longo_prazo

    from source
)

select * from renamed