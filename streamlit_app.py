import streamlit as st
from supabase import create_client
from datetime import datetime
import pytz
import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ------------------------------
# CONFIGURAÇÃO
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
# SUPABASE
# ------------------------------

url = "https://sntufmgelyresbetbfkh.supabase.co"
key = "sb_publishable_fKLNEk6sD3XSlx3zkDnPzw_XoWbXczs"

supabase = create_client(url, key)

# ------------------------------
# FUSO HORÁRIO
# ------------------------------

fuso = pytz.timezone("America/Sao_Paulo")

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

    agora = datetime.now(fuso)

    supabase.table("numeros").update({

        "nome": nome,
        "data": agora.strftime("%d/%m/%Y %H:%M"),
        "status": "VENDIDO"

    }).eq("numero", numero).execute()

    st.success(f"Número {numero} vendido para {nome}!")


def cancelar_venda(numero, senha):

    if senha != "pfe123":
        st.error("Senha incorreta!")
        return

    supabase.table("numeros").update({

        "nome": None,
        "data": None,
        "status": "Disponível"

    }).eq("numero", numero).execute()

    st.success(f"Venda do número {numero} cancelada!")


def contadores():

    response = supabase.table("numeros").select("*").eq("status", "VENDIDO").execute()

    vendidos = len(response.data)

    arrecadado = vendidos * 5

    restantes = 100 - vendidos

    st.info(f"Vendidos: {vendidos} | Arrecadado: R${arrecadado} | Restantes: {restantes}")


# ------------------------------
# GERAR PDF TABELA
# ------------------------------

def gerar_pdf(numeros):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    dados = [["Número", "Nome", "Valor", "Data", "Status"]]

    for n in numeros:

        dados.append([

            n["numero"],
            n["nome"] if n["nome"] else "-",
            n["valor"],
            n["data"] if n["data"] else "-",
            n["status"]

        ])

    tabela = Table(dados)

    tabela.setStyle(TableStyle([

        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN",(0,0),(-1,-1),"CENTER")

    ]))

    elementos = [tabela]

    doc.build(elementos)

    buffer.seek(0)

    return buffer


# ------------------------------
# GERAR PDF VENDIDOS
# ------------------------------

def gerar_pdf_vendidos(numeros):

    vendidos = [n for n in numeros if n["status"] == "VENDIDO"]

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    dados = [["Número", "Nome", "Valor", "Data", "Status"]]

    for n in vendidos:

        dados.append([

            n["numero"],
            n["nome"],
            n["valor"],
            n["data"],
            n["status"]

        ])

    tabela = Table(dados)

    tabela.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(0,0),(-1,-1),"CENTER")

    ]))

    elementos = [tabela]

    doc.build(elementos)

    buffer.seek(0)

    return buffer


# ------------------------------
# ABAS
# ------------------------------

tab1, tab2, tab3 = st.tabs(["Lista de Números","Comprar Número","Cancelar Venda"])


# ------------------------------
# LISTA
# ------------------------------

with tab1:

    st.subheader("Escolha seu número")

    numeros = get_numeros()

    disponiveis = [n["numero"] for n in numeros if n["status"] == "Disponível"]

    st.markdown("### Números disponíveis")

    st.write(disponiveis)

    colunas = 10

    for i in range(0,100,colunas):

        cols = st.columns(colunas)

        for j,col in enumerate(cols):

            idx = i + j

            if idx < len(numeros):

                n = numeros[idx]

                with col:

                    cor = "green" if n["status"]=="Disponível" else "red"

                    st.markdown(f"### {n['numero']}")

                    st.markdown(n["nome"] if n["nome"] else "-")

                    st.markdown(f"R${n['valor']}")

                    st.markdown(n["data"] if n["data"] else "-")

                    st.markdown(f":{cor}[{n['status']}]")

    contadores()

    st.markdown("### Baixar relatórios")

    pdf = gerar_pdf(numeros)

    st.download_button(

        "Baixar tabela completa em PDF",
        pdf,
        "tabela_sorteio.pdf",
        "application/pdf"

    )

    pdf_vendidos = gerar_pdf_vendidos(numeros)

    st.download_button(

        "Baixar apenas números vendidos",
        pdf_vendidos,
        "numeros_vendidos.pdf",
        "application/pdf"

    )


# ------------------------------
# COMPRAR
# ------------------------------

with tab2:

    st.subheader("Comprar número")

    numero_compra = st.number_input("Número (1-100)",min_value=1,max_value=100,step=1)

    nome_compra = st.text_input("Nome do comprador")

    senha_compra = st.text_input("Senha",type="password")

    if st.button("Efetuar venda"):

        if not nome_compra:

            st.error("Informe o nome")

        else:

            vender_numero(numero_compra,nome_compra,senha_compra)


# ------------------------------
# CANCELAR
# ------------------------------

with tab3:

    st.subheader("Cancelar venda")

    numero_cancel = st.number_input("Número para cancelar",min_value=1,max_value=100,step=1,key="cancel")

    senha_cancel = st.text_input("Senha",type="password",key="senha_cancel")

    if st.button("Cancelar venda"):

        cancelar_venda(numero_cancel,senha_cancel)


# ------------------------------
# RODAPÉ
# ------------------------------

st.markdown("---")
st.markdown("WhatsApp: 73 98857-3787 – Falar com Rogério")
