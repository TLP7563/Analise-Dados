import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análise de Vendas - JMartins", layout="wide")
st.markdown("""
            <style>
            div[data-testid="metric-container"] {
            background-color: #112240;
            border: 1px solid #233554;
            padding:15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            </style>
            """, unsafe_allow_html=True)

st.markdown("""
            <style>
            .titulo-centralizado {
            text-align: center;
            font-size: 3rem;
            font-weight: 700;
            margim-bottom: 2rem;
            color: #E6F1FF;
            }
            div[data-testid="metric-container"] {
            background-color: #112240;
            border: 1px solid #233554;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
            }
            </style>
            """, unsafe_allow_html=True)
st.markdown('<h1 class="titulo-centralizado">Análise de Vendas - JMartins</h1>', unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    df = pd.read_excel("vendas_jmartins.xlsx")
    df['Data_Hora'] = pd.to_datetime(df['Data_Hora'])
    df['Mes_Ano'] = df['Data_Hora'].dt.strftime('%m/%Y ')
    df['Hora'] = df['Data_Hora'].dt.hour
    df = df[df['Mes_Ano'] != '06/2026']
    return df

df = carregar_dados()

st.sidebar.image("https://cdn-icons-png.claticon.com/512/2800/2800118.png",width=100)
st.sidebar.header("Filtros de Análise")

with st.sidebar.form("filtros_form"):
    meses = ["Todos"] + list(df['Mes_Ano'].unique())
    mes_selecionado = st.selectbox("Selecione o Mês/Ano", meses)
    btn_pesquisar = st.form_submit_button("Aplicar Filtro", use_container_width=True)

if mes_selecionado != "Todos":
    df_filtrado = df[df['Mes_Ano'] == mes_selecionado]
else:
    df_filtrado = df

st.markdown("Visão Geral das Vendas")
col1, col2, col3 = st.columns(3)

faturamento_total = df_filtrado['Valor_Total'].sum()
ticket_medio = df_filtrado['Valor_Total'].mean()
total_vendas = len(df_filtrado)

col1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
col2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("Total de Vendas", f"{total_vendas}")

st.divider()

col_esquerda, col_direita = st.columns(2)

with col_esquerda:
        st.markdown("Top 10 Produtos Mais Vendidos")
        top_produtos = df_filtrado.groupby('Produto')['Valor_Total'].sum().reset_index()
        top_produtos = top_produtos.sort_values('Valor_Total', ascending=False).head(10)

        fig_produtos = px.bar(top_produtos, x='Valor_Total', y='Produto', orientation='h',
                              labels={'Valor_Total': 'Faturamento (R$)', 'Produto': 'Produto'},
                              color = 'Valor_Total', color_continuous_scale='Teal',
                              template='plotly_dark')
        fig_produtos.update_layout(yaxis={'categoryorder':'total ascending'},
                                   plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_produtos, use_container_width=True)

        with col_direita:
            st.markdown("Horário de Pico de Vendas")
            vendas_hora = df_filtrado.groupby('Hora').size().reset_index(name='Qtd_Vendas')

            fig_horas = px.bar(vendas_hora, x='Hora', y='Qtd_Vendas',
                               labels={'Hora': 'Horário do Dia', 'Qtd_Vendas': 'Número de Vendas'},
                               color='Qtd_Vendas', color_continuous_scale='Oranges',
                               template='plotly_dark')
            fig_horas.update_xaxes(tickmode='linear', tick0=0, dtick=1)
            fig_horas.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_horas, use_container_width=True)

        st.divider()
        st.markdown("Produtos com Baixo Estoque Estimado")
        st.info("Essa análise é baseada na quantidade média vendida por produto.")
        alerta_estoque = top_produtos[['Produto']].head(5).copy()
        alerta_estoque['Ação Reomendada'] = "Repor Estoque"
        st.table(alerta_estoque)