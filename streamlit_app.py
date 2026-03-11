import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import pytz

# ------------------------------
# CONFIGURAÇÃO DO APP
# ------------------------------
st.set_page_config(
    page_title="Sorteio Solidário – Igreja",
    layout="wide"
)

st.title("SORTEIO IMPERDÍVEL! GANHE R$150,00 NO PIX!")
st.markdown("Compre apenas 1 número por R$5,00 e concorra!")
st.markdown("Data do Sorteio: 29/03/2026 às 21:15")
st.markdown("Participe e contribua com a obra!")

# ------------------------------
# CONEXÃO SUPABASE
# ------------------------------
url = "https://sntufmgelyresbetbfkh.supabase.co"
key = "sb_publishable_fKLNEk6sD3XSlx3zkDnPzw_XoWbXczs"

supabase = create_client(url, key)

# ------------------------------
# FUSO HORÁRIO BRASIL
# ------------------------------
fuso_brasil = pytz.timezone("America/Sao_Paulo")

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

    agora = datetime.now(fuso_brasil)

    supabase.table("numeros").update({
        "nome": nome,
        "data": agora.strftime("%d/%m/%Y %H:%M"),
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

    st.info(f"Vendidos: {vendidos} | Arrecadado: R${arrecadado} | Restantes: {restantes}")


# ------------------------------
# GERAR PDF
# ------------------------------
def gerar_pdf(numeros):

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)

    y = 800

    c.setFont("Helvetica", 10)

    c.drawString(50, y, "Relatório Completo - Sorteio Solidário")
    y -= 30

    for n in numeros:

        linha = f"Número: {n['numero']} | Nome: {n['nome'] if n['nome'] else '-'} | Status: {n['status']} | Data: {n['data'] if n['data'] else '-'}"

        c.drawString(50, y, linha)

        y -= 20

        if y < 50:
            c.showPage()
            y = 800

    c.save()

    buffer.seek(0)

    return buffer


# ------------------------------
# ABAS
# ------------------------------
tab1, tab2, tab3 = st.tabs(["Lista de Números", "Comprar Número", "Cancelar Venda"])

# ------------------------------
# ABA 1 - LISTA
# ------------------------------
with tab1:

    st.subheader("Escolha seu número!")

    numeros = get_numeros()

    # números disponíveis
    disponiveis = [n["numero"] for n in numeros if n["status"] == "Disponível"]

    st.markdown("### Números Disponíveis")
    st.write(disponiveis)

    colunas = 10

    for i in range(0, 100, colunas):

        cols = st.columns(colunas)

        for j, col in enumerate(cols):

            idx = i + j

            if idx < len(numeros):

                n = numeros[idx]

                with col:

                    cor = "green" if n["status"] == "Disponível" else "red"

                    st.markdown(f"### {n['numero']}")
                    st.markdown(n["nome"] if n["nome"] else "-")
                    st.markdown(f"R${n['valor']}")
                    st.markdown(n["data"] if n["data"] else "-")
                    st.markdown(f":{cor}[{n['status']}]")

    contadores()

    st.markdown("### Baixar relatório completo")

    pdf = gerar_pdf(numeros)

    st.download_button(
        label="Baixar tabela completa em PDF",
        data=pdf,
        file_name="relatorio_sorteio.pdf",
        mime="application/pdf"
    )

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
st.markdown("WhatsApp: 73 98857-3787 – Falar com Rogério")
