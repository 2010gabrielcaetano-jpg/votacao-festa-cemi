import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

def init_db():
    conn = sqlite3.connect('votacao.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nome TEXT, email TEXT UNIQUE, senha TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS propostas (id INTEGER PRIMARY KEY, titulo TEXT, descricao TEXT, autor_id INTEGER, data TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS votos (id INTEGER PRIMARY KEY, usuario_id INTEGER, proposta_id INTEGER, voto TEXT, UNIQUE(usuario_id, proposta_id))')
    conn.commit()
    conn.close()

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

init_db()
st.set_page_config(page_title="Camara 2D", page_icon="⚖️")
st.title("⚖️ Camara Digital - Votacao de Leis")

menu = st.sidebar.selectbox("Menu", ["Inicio", "Cadastro / Login", "Cadastrar Lei", "Votar", "Resultados"])

if menu == "Inicio":
    st.info("Sistema para votacao de leis da turma.")
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
    st.subheader("1. Cadastrar Usuario")
    with st.form("cad"):
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Cadastrar Usuario"):
            try:
                conn = sqlite3.connect('votacao.db')
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome, email, hash_senha(senha)))
                conn.commit()
                st.success("Cadastrado!")
                conn.close()
            except:
                st.error("E-mail ja existe")
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
            st.success("Bem-vindo!")
        else:
            st.error("Login invalido")
        conn.close()

elif menu == "Cadastrar Lei":
    if 'usuario_id' not in st.session_state:
        st.warning("Faca login primeiro!")
    else:
        nome_logado = st.session_state['usuario_nome']
        st.subheader("Cadastrar Nova Lei")
        st.write(f"Logado como: {nome_logado}")
        with st.form("lei"):
            titulo = st.text_input("Titulo da Lei")
            desc = st.text_area("Descricao detalhada")
            if st.form_submit_button("Cadastrar Lei"):
                conn = sqlite3.connect('votacao.db')
                c = conn.cursor()
                c.execute("INSERT INTO propostas (titulo,descricao,autor_id,data) VALUES (?,?,?,?)", (titulo, desc, st.session_state['usuario_id'], datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                st.success("Lei cadastrada!")
                conn.close()

elif menu == "Votar":
    if 'usuario_id' not in st.session_state:
        st.warning("Faca login!")
    else:
        conn = sqlite3.connect('votacao.db')
        c = conn.cursor()
        c.execute("SELECT p.id, p.titulo, p.descricao, u.nome FROM propostas p JOIN usuarios u ON p.autor_id = u.id")
        propostas = c.fetchall()
        if not propostas:
            st.info("Nenhuma lei cadastrada ainda.")
        for pid, titulo, desc, autor in propostas:
            with st.container(border=True):
                st.write(f"### {titulo}")
                st.write(f"Autor: {autor} | {desc}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("SIM", key=f"sim{pid}"):
                        try:
                            c.execute("INSERT INTO votos (usuario_id, proposta_id, voto) VALUES (?,?,?)", (st.session_state['usuario_id'], pid, "SIM"))
                            conn.commit()
                            st.success("Votou SIM!")
                        except:
                            st.error("Voce ja votou!")
                with col2:
                    if st.button("NAO", key=f"nao{pid}"):
                        try:
                            c.execute("INSERT INTO votos (usuario_id, proposta_id, voto) VALUES (?,?,?)", (st.session_state['usuario_id'], pid, "NAO"))
                            conn.commit()
                            st.success("Votou NAO!")
                        except:
                            st.error("Voce ja votou!")
        conn.close()

elif menu == "Resultados":
    st.subheader("Resultado da Votacao")
    conn = sqlite3.connect('votacao.db')
    c = conn.cursor()
    c.execute("SELECT id, titulo FROM propostas")
    todas = c.fetchall()
    for pid, titulo in todas:
        c.execute("SELECT COUNT(*) FROM votos WHERE proposta_id=? AND voto='SIM'", (pid,))
        sim = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM votos WHERE proposta_id=? AND voto='NAO'", (pid,))
        nao = c.fetchone()[0]
        total = sim + nao
        st.write(f"**{titulo}** - SIM: {sim} | NAO: {nao} | Total: {total}")
        if total > 0:
            st.progress(sim / total)
        st.divider()
    conn.close()
