import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(page_title="Análise de Crédito - Brasil", layout="wide")

st.title("Análise de Crédito do Brasil (SCR)")
st.markdown("Visão analítica do Sistema de Informações de Créditos. Dados otimizados via dbt e DuckDB.")

@st.cache_data
def carregar_meses_disponiveis():
    con = duckdb.connect('data/scr_database.duckdb', read_only=True)
    df_datas = con.execute("SELECT DISTINCT data_referencia FROM mart_scr_macro_tendencias ORDER BY data_referencia DESC").df()
    con.close()
    return df_datas['data_referencia'].tolist()

meses = carregar_meses_disponiveis()

st.sidebar.title("Dashboard SCR")
st.sidebar.header("Filtros")
data_selecionada = st.sidebar.selectbox("Mês de Referência:", meses)


def carregar_dados_do_mes(data_filtro):
    con = duckdb.connect('data/scr_database.duckdb', read_only=True)
    
    query_macro = f"SELECT * FROM mart_scr_macro_tendencias"
    df_macro = con.execute(query_macro).df()
    
    query_geo = f"SELECT * FROM mart_scr_geografico_uf WHERE data_referencia = '{data_filtro}'"
    df_geo = con.execute(query_geo).df()

    query_perfil = f"SELECT * FROM mart_scr_perfil_endividamento WHERE data_referencia = '{data_filtro}' and tipo_cliente = 'PF'"
    df_perfil = con.execute(query_perfil).df()

    query_mod = f"SELECT * FROM mart_scr_modalidade WHERE data_referencia = '{data_filtro}'"
    df_mod = con.execute(query_mod).df()

    query_ocup = f"SELECT * FROM mart_scr_ocupacao WHERE data_referencia = '{data_filtro}'"
    df_ocup = con.execute(query_ocup).df()

    query_tpc = f"SELECT * FROM mart_scr_tipo_cliente"
    df_tpc = con.execute(query_tpc).df()

    query_big = f"select * from mart_scr_bignumbers WHERE data_referencia = '{data_filtro}'"
    df_big = con.execute(query_big).df()
    
    con.close()
    return df_macro, df_geo, df_perfil, df_mod, df_ocup, df_tpc, df_big

df_macro_atual, df_geo_atual, df_perfil_atual, df_mod_atual, df_ocup_atual, df_tpc_atual, df_big_atual = carregar_dados_do_mes(data_selecionada)

def format_with_commas(number):
    num_str = f"{number:,.2f}"
    return num_str.replace(',', 'X').replace('.', ',').replace('X', '.')

def format_abreviacao(number):
    if number > 1000000000000:
        valor_formatado = f"R$ {number/1000000000000:,.2f} Tri".replace(',', 'X').replace('.', ',').replace('X', '.')
    elif number > 1000000000:
        valor_formatado = f"R$ {number/1000000000:,.2f} Bi".replace(',', 'X').replace('.', ',').replace('X', '.')
    elif number > 1000000:
        valor_formatado = f"R$ {number/1000000:,.2f} MM".replace(',', 'X').replace('.', ',').replace('X', '.')    
    return valor_formatado



def display_metric(col, title, column, total_value, col_delta):
    with col:
        with st.container(border=True):
            match(column):
                case "carteira_ativa_total":
                    delta_percent = df_big_atual[col_delta].iloc[0]
                    delta_str = f"{delta_percent:+.2f}%"
                    st.metric(title, format_abreviacao(total_value), delta=delta_str)
                case "carteira_inadimplida_total":
                    delta_percent = df_big_atual[col_delta].iloc[0]
                    delta_str = f"{delta_percent:+.2f}%"
                    st.metric(title, format_abreviacao(total_value), delta=delta_str, delta_color = "inverse")
                case "ativo_problematico_total":
                    delta_percent = df_big_atual[col_delta].iloc[0]
                    delta_str = f"{delta_percent:+.2f}%"
                    st.metric(title, format_abreviacao(total_value), delta=delta_str, delta_color = "inverse")
                case "indice_inadimplencia_perc":
                    delta_percent = df_big_atual[col_delta].iloc[0]
                    delta_str = f"{delta_percent:+.2f}%"
                    value_perc = f"{total_value:+.2f}%"
                    st.metric(title, value_perc, delta=delta_str, delta_color = "inverse")
                case "indice_ativo_problematico_perc":
                    delta_percent = df_big_atual[col_delta].iloc[0]
                    delta_str = f"{delta_percent:+.2f}%"
                    value_perc = f"{total_value:+.2f}%"
                    st.metric(title, value_perc, delta=delta_str, delta_color = "inverse")
st.subheader("BigNumbers SCR")

metrics = [
    ("Carteira Ativa", "carteira_ativa_total", 'variavao_carteira_ativa_total'),
    ("Carteira over90", "carteira_inadimplida_total", 'variavao_carteira_inadimplida_total'),
    ("Ativo problemático (entre E e H)", "ativo_problematico_total", 'variavao_ativo_problematico_total'),
    ("Indicador Over90", "indice_inadimplencia_perc", 'variavao_indice_inadimplencia_perc'),
    ("Indicador Ativo Problemático", "indice_ativo_problematico_perc", 'variavao_indice_ativo_problematico_perc')
]

cols = st.columns(5)
for col, (title, column, col_delta) in zip(cols, metrics):
    total_value = df_big_atual[column].iloc[0]
    display_metric(col, title, column, total_value, col_delta)



col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("Tendência de Inadimplência e Ativo Problemático")

    fig_tendencia = px.line(
        df_macro_atual, 
        x="data_referencia", 
        y=["indice_inadimplencia_perc", "indice_ativo_problematico_perc"],
        labels={"value": "Taxa (%)", "data_referencia": "Data", "variable": "Indicador"},
        markers=True
    )
    fig_tendencia.update_layout(
    xaxis_type='date',
    yaxis_type='linear',
    legend_title_text=''
)
    fig_tendencia.update_yaxes(tickformat=".1f", ticksuffix="%")
    st.plotly_chart(fig_tendencia, use_container_width=True)

# Cria uma nova coluna só com o texto formatado para o gráfico

with col_dir:
    st.subheader("Inadimplência por Tipo de Cliente")

    df_tpc_pf = df_tpc_atual[df_tpc_atual['tipo_cliente'] == 'PF'].sort_values('data_referencia')
    df_tpc_pj = df_tpc_atual[df_tpc_atual['tipo_cliente'] == 'PJ'].sort_values('data_referencia')

    fig_tpc = go.Figure()

    fig_tpc.add_trace(go.Scatter(
        x=df_tpc_pf["data_referencia"],
        y=df_tpc_pf["indice_inadimplencia_perc"],
        mode='lines+markers+text',
        text=df_tpc_pf["indice_inadimplencia_perc"],
        texttemplate='%{text:.1f}%',
        textposition='top center',
        name="PF",
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))

    fig_tpc.add_trace(go.Scatter(
        x=df_tpc_pj["data_referencia"],
        y=df_tpc_pj["indice_inadimplencia_perc"],
        mode='lines+markers+text',
        text=df_tpc_pj["indice_inadimplencia_perc"],
        texttemplate='%{text:.1f}%',
        textposition='bottom center',
        name="PJ",
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=8)
    ))

    fig_tpc.update_layout(
        title="Inadimplência: PF x PJ",
        xaxis_title="Data",
        yaxis_title="Over90 (%)",
        legend_title_text="Tipo Cliente",
        height=500,
        hovermode="x unified"
    )

    fig_tpc.update_yaxes(tickformat=".1f", ticksuffix="%")

    st.plotly_chart(fig_tpc, use_container_width=True)

st.divider()
st.subheader(f"Inadimplência por Estado ({data_selecionada})")
geo_atual = df_geo_atual[df_geo_atual['data_referencia'] == data_selecionada]


fig_geo = go.Figure()
fig_geo.add_trace(go.Bar(
    y=geo_atual["sigla_uf"],
    x=geo_atual["indice_inadimplencia_perc"],
    orientation='h',
    textposition='inside',
    texttemplate='%{x:.1f}%',
    marker=dict(
        color=geo_atual["indice_inadimplencia_perc"],
        colorscale="Reds",                            
        showscale=True                                
    )
))


fig_geo.update_layout(
    xaxis_title="Inadimplência (%)",
    yaxis_title="UF",
    height=600,
    yaxis={'categoryorder':'total ascending'}
)
fig_geo.update_xaxes(tickformat=".1f", ticksuffix="%")
st.plotly_chart(fig_geo, use_container_width=True)

st.divider()
st.subheader(f"Perfil de Endividamento PF ({data_selecionada})")

perfil_atual = df_perfil_atual[df_perfil_atual['data_referencia'] == data_selecionada]
perfil_atual['total_curto_prazo_formatado'] = perfil_atual['total_curto_prazo'].apply(format_abreviacao)
perfil_atual['total_longo_prazo_formatado'] = perfil_atual['total_longo_prazo'].apply(format_abreviacao)


fig_perfil = go.Figure()


fig_perfil.add_trace(go.Bar(
    y=perfil_atual["faixa_rendimento_porte"],
    x=perfil_atual["total_curto_prazo"],
    text=perfil_atual["total_curto_prazo_formatado"],
    name="Curto Prazo",
    orientation='h',
    textposition='inside',
    marker_color='#1f77b4'
))


fig_perfil.add_trace(go.Bar(
    y=perfil_atual["faixa_rendimento_porte"],
    x=perfil_atual["total_longo_prazo"],
    text=perfil_atual["total_longo_prazo_formatado"],
    name="Longo Prazo",
    orientation='h',
    textposition='inside',
    marker_color='#ff7f0e'
))


fig_perfil.update_layout(
    barmode='stack',
    title="Curto Prazo vs Longo Prazo por Faixa de Rendimento",
    xaxis_title="Volume (R$)",
    yaxis_title="Faixa de Rendimento",
    legend_title_text="Prazo",
    height=500
)


st.plotly_chart(fig_perfil, use_container_width=True)

st.divider()
st.subheader(f"Performance das Modalidades de Crédito ({data_selecionada})")


modalidade_atual = df_mod_atual[df_mod_atual['data_referencia'] == data_selecionada].copy()


modalidade_atual = modalidade_atual.sort_values(by='carteira_ativa_total', ascending=False)


modalidade_atual['saldo_formatado'] = modalidade_atual['carteira_ativa_total'].apply(format_abreviacao)

fig_combo = make_subplots(specs=[[{"secondary_y": True}]])


fig_combo.add_trace(
    go.Bar(
        x=modalidade_atual['modalidade_credito'],
        y=modalidade_atual['carteira_ativa_total'],
        text=modalidade_atual['saldo_formatado'],
        textposition='outside',
        name="Saldo Ativo (R$)",
        marker_color='#1f77b4',
        opacity=0.8
    ),
    secondary_y=False,
)


fig_combo.add_trace(
    go.Scatter(
        x=modalidade_atual['modalidade_credito'],
        y=modalidade_atual['indice_inadimplencia_perc'],
        name="Inadimplência (%)",
        mode='lines+markers',
        line=dict(color='#d62728', width=3),
        marker=dict(size=8)
    ),
    secondary_y=True,
)

fig_combo.update_layout(
    title_text="Saldo Contratado vs. Inadimplência por Modalidade",
    xaxis_title="Modalidade de Crédito",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    height=700
)


fig_combo.update_yaxes(title_text="Volume (R$)", secondary_y=False, showgrid=False, showticklabels=False)


fig_combo.update_yaxes(title_text="Inadimplência (%)", secondary_y=True, showgrid=False, tickformat=".1f", ticksuffix="%")

st.plotly_chart(fig_combo, use_container_width=True)

st.divider()

st.divider()
st.subheader(f"Inadimplência por Ocupação ({data_selecionada})")


fig_ocup = go.Figure()
fig_ocup.add_trace(go.Bar(
    y=df_ocup_atual["natureza_ocupacao"],
    x=df_ocup_atual["indice_inadimplencia_perc"],
    orientation='h',
    textposition='inside',
    texttemplate='%{x:.1f}%',
    marker=dict(
        color=df_ocup_atual["indice_inadimplencia_perc"],
        colorscale="Reds",                            
        showscale=True                                
    )
))


fig_ocup.update_layout(
    xaxis_title="Inadimplência (%)",
    yaxis_title="Ocupação",
    height=600,
    yaxis={'categoryorder':'total ascending'}
)
fig_ocup.update_xaxes(tickformat=".1f", ticksuffix="%")
st.plotly_chart(fig_ocup, use_container_width=True)