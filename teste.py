import streamlit as st
import re

def extrair_dados_pauta_judicial(texto_pauta):
    # Nova Regex para capturar: Processo, Autor e Réu com base no novo padrão
    # Busca o número, ignora o Juizo, captura o nome até o traço/função
    padrao = r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})/SP.*?Autor\s+(.*?)\s*-\s*RECLAMANTE.*?X.*?Réu\s+(.*?)\s*-\s*RECLAMADO"
    
    blocos = re.findall(padrao, texto_pauta, re.DOTALL)
    
    resultados = []

    for num_processo, nome_ativo, nome_passivo in blocos:
        # Limpeza simples para garantir que não fiquem espaços extras
        nome_ativo = nome_ativo.strip().upper()
        nome_passivo = nome_passivo.strip().upper()

        # Montagem do texto exatamente como você solicitou
        item = (
            f"FEITO N.º - {num_processo}.\n"
            f"REQUERENTE/RECLAMANTE - {nome_ativo}.\n"
            f"REQUERIDO/RECLAMADO - {nome_passivo}."
        )
        resultados.append(item)
    
    return "\n\n\n".join(resultados)

def gerar_rtf(texto):
    # Mantendo sua lógica de RTF original
    conteudo_rtf = texto.replace('\n', '\\par\n')
    cabecalho = r"{\rtf1\ansi\ansicpg1252\deff0{\fonttbl{\f0\fswiss\fcharset0 Arial;}}"
    configuracoes = r"\f0\fs24\sa0\sl240\slmult1 " 
    rtf_final = cabecalho + configuracoes + conteudo_rtf + "}"
    return rtf_final.encode('latin-1', errors='ignore')

# --- Interface Streamlit (Mantida original) ---
st.set_page_config(page_title="Extrator Judiciário", layout="wide")

st.title("⚖️ Extrator de Pauta Araçatuba")

texto_entrada = st.text_area("COLE A PAUTA BRUTA ABAIXO:", height=250)

if st.button("GERAR TEXTO FORMATADO"):
    if texto_entrada.strip():
        resultado = extrair_dados_pauta_judicial(texto_entrada)
        
        if resultado:
            st.success("Dados processados com sucesso!")
            
            # Exibição na tela
            st.text_area("PRÉ-VISUALIZAÇÃO:", value=resultado, height=300)
            
            # Gerar arquivo para download
            dados_rtf = gerar_rtf(resultado)
            
            st.download_button(
                label="📥 BAIXAR ARQUIVO .RTF",
                data=dados_rtf,
                file_name="pauta_formatada.rtf",
                mime="application/rtf"
            )
        else:
            st.error("Nenhum processo encontrado no novo padrão informado.")
    else:
        st.warning("O campo está vazio.")