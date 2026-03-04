import streamlit as st
from supabase import create_client
from datetime import datetime

# ------------------------------
# CONFIGURAÇÃO DO APP
# ------------------------------
st.set_page_config(
    page_title="Sorteio Solidário – Igreja",
    layout="wide"
)

st.title(" SORTEIO IMPERDÍVEL! GANHE R$150,00 NO PIX!")
st.markdown("Compre apenas 1 número por R$5,00 e concorra!")
st.markdown(" Data do Sorteio: 29/03/2026 às 21:15")
st.markdown(" Participe e contribua com a obra!")

# ------------------------------
# CONEXÃO SUPABASE
# ------------------------------
url = "https://sntufmgelyresbetbfkh.supabase.co"
key = "sb_publishable_fKLNEk6sD3XSlx3zkDnPzw_XoWbXczs"

supabase = create_client(url, key)

# ------------------------------
# FUNÇÕES
# ------------------------------
def get_numeros():
    response = supabase.table("numeros").select("*").order("numero").execute()
    return response.data


def vender_numero(numero, nome, senha):
    if senha != "pfe123":
        st.error("Senha incorreta!")
        return

    response = supabase.table("numeros").select("status").eq("numero", numero).execute()

    if not response.data:
        st.error("Número inválido!")
        return

    if response.data[0]["status"] == "VENDIDO":
        st.warning("Número já vendido!")
        return

    supabase.table("numeros").update({
        "nome": nome,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "VENDIDO"
    }).eq("numero", numero).execute()

    st.success(f"Número {numero} vendido para {nome} com sucesso!")


def cancelar_venda(numero, senha):
    if senha != "pfe123":
        st.error("Senha incorreta!")
        return

    supabase.table("numeros").update({
        "nome": None,
        "data": None,
        "status": "Disponível"
    }).eq("numero", numero).execute()

    st.success(f"Venda do número {numero} cancelada com sucesso!")


def contadores():
    response = supabase.table("numeros").select("*").eq("status", "VENDIDO").execute()
    vendidos = len(response.data)
    arrecadado = vendidos * 5
    restantes = 100 - vendidos

    st.info(f" Vendidos: {vendidos} |  Arrecadado: R${arrecadado} |  Restantes: {restantes}")


# ------------------------------
# ABAS
# ------------------------------
tab1, tab2, tab3 = st.tabs([" Lista de Números", " Comprar Número", " Cancelar Venda"])

# ------------------------------
# ABA 1 - LISTA
# ------------------------------
with tab1:
    st.subheader("Escolha seu número!")

    numeros = get_numeros()
    colunas = 10

    for i in range(0, 100, colunas):
        cols = st.columns(colunas)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(numeros):
                n = numeros[idx]
                with col:
                    st.markdown(f"**{n['numero']}**")
                    st.markdown(n['nome'] if n['nome'] else "-")
                    st.markdown(f"R${n['valor']}")
                    st.markdown(n['data'] if n['data'] else "-")
                    st.markdown(f"**{n['status']}**")

    contadores()

# ------------------------------
# ABA 2 - COMPRAR
# ------------------------------
with tab2:
    st.subheader("Comprar Número")

    numero_compra = st.number_input("Número (1-100)", min_value=1, max_value=100, step=1)
    nome_compra = st.text_input("Nome do comprador")
    senha_compra = st.text_input("Senha", type="password")

    if st.button("Efetuar Venda"):
        if not nome_compra:
            st.error("Informe o nome!")
        else:
            vender_numero(numero_compra, nome_compra, senha_compra)

# ------------------------------
# ABA 3 - CANCELAR
# ------------------------------
with tab3:
    st.subheader("Cancelar Venda")

    numero_cancel = st.number_input("Número para cancelar", min_value=1, max_value=100, step=1, key="cancel")
    senha_cancel = st.text_input("Senha", type="password", key="senha_cancel")

    if st.button("Cancelar Venda"):
        cancelar_venda(numero_cancel, senha_cancel)

# ------------------------------
# RODAPÉ
# ------------------------------
st.markdown("---")
st.markdown(" WhatsApp: 73 98857-3787 – Falar com Rogério")
