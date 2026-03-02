import streamlit as st
import sqlite3
from datetime import datetime

# ------------------------------
# Configurações iniciais do Streamlit
# ------------------------------
st.set_page_config(
    page_title="Sorteio Solidário – Igreja",
    layout="wide"
)

st.title("SORTEIO IMPERDÍVEL!GANHE R$150,00 NO PIX!")
st.markdown("Como participar:Compre apenas 1 número por R$5,00 e concorra! Data do Sorteio: 29/03/2026 ás 21:15 Participe e contribua com a obra! Cada número adquirido é uma semente plantada")

# ------------------------------
# Conexão com SQLite
# ------------------------------
conn = sqlite3.connect("sorteio_igreja.db", check_same_thread=False)
c = conn.cursor()

# Criação da tabela se não existir
c.execute("""
CREATE TABLE IF NOT EXISTS numeros (
    numero INTEGER PRIMARY KEY,
    nome TEXT,
    valor REAL DEFAULT 5.0,
    data TEXT,
    status TEXT DEFAULT 'Disponível'
)
""")
conn.commit()

# Inicializar 100 números se não existirem
for i in range(1, 101):
    c.execute("INSERT OR IGNORE INTO numeros (numero) VALUES (?)", (i,))
conn.commit()

# ------------------------------
# Funções principais
# ------------------------------
def get_numeros():
    c.execute("SELECT * FROM numeros ORDER BY numero")
    return c.fetchall()

def vender_numero(numero, nome, senha):
    if senha != "pfe123":
        st.error("Senha incorreta!")
        return
    c.execute("SELECT status FROM numeros WHERE numero=?", (numero,))
    status = c.fetchone()
    if not status:
        st.error("Número inválido!")
        return
    if status[0] == "VENDIDO":
        st.warning("Número já vendido!")
        return
    data_venda = "29/03/2026 21:15"
    c.execute("UPDATE numeros SET nome=?, data=?, status='VENDIDO' WHERE numero=?", (nome, data_venda, numero))
    conn.commit()
    st.success(f"Número {numero} vendido para {nome} com sucesso!")

def cancelar_venda(numero, senha):
    if senha != "pfe123":
        st.error("Senha incorreta!")
        return
    c.execute("SELECT status FROM numeros WHERE numero=?", (numero,))
    status = c.fetchone()
    if not status:
        st.error("Número inválido!")
        return
    if status[0] == "Disponível":
        st.warning("Número já está disponível!")
        return
    c.execute("UPDATE numeros SET nome=NULL, data=NULL, status='Disponível' WHERE numero=?", (numero,))
    conn.commit()
    st.success(f"Venda do número {numero} cancelada com sucesso!")

def contadores():
    c.execute("SELECT COUNT(*) FROM numeros WHERE status='VENDIDO'")
    vendidos = c.fetchone()[0]
    arrecadado = vendidos * 5
    restantes = 100 - vendidos
    st.info(f"Números vendidos: {vendidos} | Arrecadado: R${arrecadado} | Números restantes: {restantes}")

# ------------------------------
# Abas do App
# ------------------------------
tab1, tab2, tab3 = st.tabs([" Lista de Números", " Comprar Número", " Cancelar Venda"])

# ------------------------------
# Aba 1: Lista estilo Excel
# ------------------------------
with tab1:
    st.subheader("Compre o seu!")

    numeros = get_numeros()
    num_colunas = 10  # 10 números por linha para melhor visualização

    # Organizando os números em colunas
    for i in range(0, 100, num_colunas):
        cols = st.columns(num_colunas)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(numeros):
                numero, nome, valor, data, status = numeros[idx]
                with col:
                    st.markdown(f"**{numero}**")
                    st.markdown(f"{nome if nome else '-'}")
                    st.markdown(f"R${valor}")
                    st.markdown(f"{data if data else '-'}")
                    st.markdown(f"**{status}**")

    contadores()

# ------------------------------
# Aba 2: Comprar Número
# ------------------------------
with tab2:
    st.subheader("Comprar Número")
    numero_compra = st.number_input("Digite o número desejado (1-100)", min_value=1, max_value=100, step=1)
    nome_compra = st.text_input("Digite o nome do comprador")
    senha_compra = st.text_input("Digite a senha para confirmar", type="password")
    if st.button("Efetuar Venda"):
        if not nome_compra:
            st.error("Informe o nome do comprador!")
        else:
            vender_numero(numero_compra, nome_compra, senha_compra)

# ------------------------------
# Aba 3: Cancelar Venda
# ------------------------------
with tab3:
    st.subheader("Cancelar Venda")
    numero_cancel = st.number_input("Digite o número a cancelar", min_value=1, max_value=100, step=1, key="cancel")
    senha_cancel = st.text_input("Digite a senha para cancelar", type="password", key="senha_cancel")
    if st.button("Cancelar Venda"):
        cancelar_venda(numero_cancel, senha_cancel)

# ------------------------------
# Rodapé
# ------------------------------
st.markdown("---")
st.markdown(" WhatsApp: 73 98857-3787 – Falar com Rogério")
