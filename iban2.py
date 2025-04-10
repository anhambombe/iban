import streamlit as st
import pandas as pd
import schwifty

# Configuração da página
st.set_page_config(page_title="IBAN", page_icon="✔", layout="centered")

# Ocultar menu e rodapé do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Estilos personalizados
st.markdown("""
    <style>
    .big-number {
        font-size: 72px;
        color: #ff4b4b;
        font-weight: bold;
        text-align: center;
    }
    .congrats {
        font-size: 36px;
        color: green;
        text-align: center;
        margin-top: 20px;
    }
    .big-text {
        font-size: 24px;
        color: #ff6347;  /* Cor vibrante: Tom de laranja/vermelho */
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Função de validação
def validate_schwifty(iban_str):
    try:
        schwifty.IBAN(iban_str)  # Se não lançar erro, é válido
        return "Válido"
    except:
        return "Inválido"

def formatados (iban):
    try:
        f=schwifty.IBAN(iban).formatted
        return f
    except:
        return "Não é possivel identificar o codigo do país"


def pais (iban):
    try:
        n=schwifty.IBAN(iban).country.name
        return n
    except:
        return "Não é possivel identificar o codigo do país"


# Interface do Streamlit
#st.title(":rainbow[Validadação de IBAN]")
st.markdown("<h1 style='text-align: center;'> Validadação de IBAN </h1>", unsafe_allow_html=True)

# Texto alterado com a classe 'big-text'
st.markdown("<p class='big-text'>Carrega seus dados em um arquivo xlsx, xls, csv, txt!</p>", unsafe_allow_html=True)

# Upload do arquivo
uploaded_file = st.file_uploader(":rainbow[Carregue o arquivo aqui]👇", type=["xlsx", "xls", "csv", "txt"])
col1, col2=st.columns(2)

if uploaded_file:
    with col1:
        # Permitir que o usuário defina a linha dos cabeçalhos
        header_row = st.number_input("Digite o número da linha do cabeçalho (começando em 0)", min_value=0, value=0, step=1)
    
    # Identificar o formato do arquivo e carregá-lo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, header=header_row)
    elif uploaded_file.name.endswith(".txt"):
        df = pd.read_csv(uploaded_file, delimiter="\t", header=header_row)  # Assumindo tabulação como separador
    else:
        xls = pd.ExcelFile(uploaded_file)
        with col2:
            sheet_name = st.selectbox("Selecione a planilha", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name, header=header_row)
    
    # Tentar identificar automaticamente a coluna de IBAN
    possiveis_nomes = ["IBAN", "Iban", "iban"]
    coluna_iban = next((col for col in df.columns if any(nome in col for nome in possiveis_nomes)), None)
    
    # Permitir que o usuário selecione a coluna caso a detecção automática falhe
    if not coluna_iban:
        coluna_iban = st.selectbox("Selecione a coluna contendo os IBANs", df.columns)
    
    if coluna_iban:
        df['Formato'] = df[coluna_iban].apply(formatados)
        df['Pais'] = df[coluna_iban].apply(pais)
        df['Validação'] = df[coluna_iban].apply(validate_schwifty)

        
        # Exibir a tabela com os resultados
        st.write("### Resultados da Validação")
        st.dataframe(df)
        col1, col2=st.columns(2)
        # Opção para baixar o arquivo atualizado
        with col1:
            file_type = st.radio("Escolha o formato do arquivo para download", ["xlsx", "csv", "txt"], horizontal=True)
        
        if file_type == "xlsx":
            output_file = "dados_validacao.xlsx"
            df.to_excel(output_file, index=False)
        elif file_type == "csv":
            output_file = "dados_validacao.csv"
            df.to_csv(output_file, index=False)
        else:
            output_file = "dados_validacao.txt"
            df.to_csv(output_file, index=False, sep="\t")
        
        with open(output_file, "rb") as f:
            with col2:
                st.download_button(":rainbow[Baixar resultados]", f, file_name=output_file)
    else:
        st.error("Por favor, selecione uma coluna contendo os IBANs.")
