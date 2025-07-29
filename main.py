import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Autenticação
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# Interface
st.set_page_config(page_title="Resumo Diário", layout="centered")
st.title("📊 Resumo Diário de Vendas")

# Botão para atualizar os dados
if st.button("🔄 Atualizar dados"):
    st.rerun()

# Acessa a planilha
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/11mnqSzsCTCihNHZx_VWrLBC_FXulQABNwDqfMGP0QK8/edit")
data = sheet.sheet1.get_all_records()
df = pd.DataFrame(data)

# Limpeza da coluna Valor
df["Valor"] = df["Valor"].astype(str)
df["Valor"] = df["Valor"].str.replace("R$", "", regex=False)
df["Valor"] = df["Valor"].str.replace(".", "", regex=False)
df["Valor"] = df["Valor"].str.replace(",", ".", regex=False)
df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

# Data de hoje
hoje = datetime.now().strftime("%Y-%m-%d")
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True).dt.strftime("%Y-%m-%d")
df_hoje = df[df["Data"] == hoje]

if df_hoje.empty:
    st.warning("Nenhum dado registrado hoje.")
else:
    total = df_hoje["Valor"].sum()
    por_forma = df_hoje.groupby("Forma")["Valor"].sum().reset_index()
    por_tipo = df_hoje.groupby("Tipo")["Valor"].sum().reset_index()

    st.markdown(f"### 📅 Data: **{datetime.now().strftime('%d/%m/%Y')}**")
    st.markdown(f"## 💰 Total do dia: R$ {total:.2f}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💳 Forma de Pagamento")
        st.dataframe(por_forma, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### 🧾 Tipo de Entrada")
        st.dataframe(por_tipo, use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("### 📋 Registros do Dia")
    st.dataframe(df_hoje, use_container_width=True, hide_index=True)

