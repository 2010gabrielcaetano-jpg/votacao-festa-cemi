import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

def init_db():
    conn = sqlite3.connect('votacao.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (id INTEGER PRIMARY KEY, nome TEXT, email TEXT UNIQUE, senha TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS propostas 
                 (id INTEGER PRIMARY KEY, titulo TEXT, descricao TEXT, autor_id INTEGER, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS votos 
                 (id INTEGER PRIMARY KEY, usuario_id INTEGER, proposta_id INTEGER, voto TEXT, UNIQUE(usuario_id, proposta_id))''')
    conn.commit()
    conn.close()

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

init_db()

st.set_page_config(page_title="Câmara 2ºD e 2ºE", page_icon="⚖️")
st.title("⚖️ Câmara Digital - Votação de Leis")

menu = st.sidebar.selectbox("Menu", ["Início", "Cadastro / Login", "Cadastrar Lei", "Votar", "Resultados"])

if menu == "Início":
    st.info("Sistema para criação e votação de propostas de leis da turma.")
    conn = sqlite3.connect('votacao.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM propostas")
    total_leis = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM votos")
    total_votos = c.fetchone()[0]
    col1, col2 = st.columns(2)
    col1.metric("Leis Propostas", total_leis)
    col2.metric("Votos Totais", total_votos)
    conn.close()

elif menu == "Cadastro / Login":
    st.subheader("1. Cadastrar Usuário")
    with st.form("cad"):
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Cadastrar Usuário"):
            try:
                conn = sqlite3.connect('votacao.db')
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome, email, hash_senha(senha)))
                conn.commit()
                st.success(f"Usuário {nome} cadastrado!")
                conn.close()
            except:
                st.error("E-mail já cadastrado!")
    
    st.divider()
    st.subheader("2. Fazer Login")
    email_l = st.text_input("E-mail do login")
    senha_l = st.text_input("Senha do login", type="password")
    if st.button("Entrar"):
        conn = sqlite3.connect('votacao.db')
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email_l, hash_senha(senha_l)))
        user = c.fetchone()
        if user:
            st.session_state['usuario_id'] = user[0]
            st.session_state['usuario_nome'] = user[1]
            st.success(f"Bem-vindo, {user[1]}!")
        else:
            st.error("Login ou senha inválidos")
        conn.close()

elif menu == "Cadastrar Lei":
    if 'usuario_id' not in st.session_state:
        st.warning("Você precisa fazer login primeiro!")
    else:
        st.subheader(f"Cadastrar Nova
