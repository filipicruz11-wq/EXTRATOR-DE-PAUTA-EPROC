import streamlit as st
import re

# Configuração da página
st.set_page_config(page_title="Extrator Judiciário", layout="wide")

def tratar_multiplos_nomes(nome_bruto):
    """
    Mantém apenas o primeiro nome e adiciona 'E OUTROS' 
    se houver vírgulas ou indicadores de multiplicidade.
    """
    nome_limpo = nome_bruto.strip().upper()
    
    # Se houver vírgula ou ponto e vírgula, indica múltiplos nomes
    if ',' in nome_limpo or ';' in nome_limpo:
        # Pega tudo antes da primeira vírgula/ponto e vírgula
        primeiro_nome = re.split(r'[,;]', nome_limpo)[0].strip()
        return f"{primeiro_nome} E OUTROS"
    
    return nome_limpo

def extrair_dados_pauta_judicial(texto_pauta):
    # Regex ajustado para ser um pouco mais flexível na captura dos blocos
    padrao = r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})/SP.*?Autor\s+(.*?)\s*-\s*RECLAMANTE.*?X.*?Réu\s+(.*?)\s*-\s*RECLAMADO"
    blocos = re.findall(padrao, texto_pauta, re.DOTALL)
    resultados = []

    for num_processo, nome_ativo, nome_passivo in blocos:
        # Aplicando a nova lógica de "E OUTROS"
        requerente = tratar_multiplos_nomes(nome_ativo)
        requerido = tratar_multiplos_nomes(nome_passivo)
        
        item = (
            f"FEITO N.º - {num_processo}.\n"
            f"REQUERENTE/RECLAMANTE - {requerente}.\n"
            f"REQUERIDO/RECLAMADO - {requerido}."
        )
        resultados.append(item)
    return "\n\n\n".join(resultados)

def gerar_rtf(texto):
    conteudo_rtf = texto.replace('\n', '\\par\n')
    cabecalho = r"{\rtf1\ansi\ansicpg1252\deff0{\fonttbl{\f0\fswiss\fcharset0 Arial;}}"
    configuracoes = r"\f0\fs24\sa0\sl240\slmult1 " 
    rtf_final = cabecalho + configuracoes + conteudo_rtf + "}"
    return rtf_final.encode('latin-1', errors='ignore')

# --- Interface ---
st.title("⚖️ Extrator de Pauta Araçatuba")

texto_entrada = st.text_area("COLE A PAUTA BRUTA ABAIXO:", height=250)

if st.button("GERAR TEXTO FORMATADO"):
    if texto_entrada.strip():
        resultado = extrair_dados_pauta_judicial(texto_entrada)
        if resultado:
            st.success("Dados processados com a regra 'E OUTROS'!")
            st.text_area("PRÉ-VISUALIZAÇÃO:", value=resultado, height=300)
            dados_rtf = gerar_rtf(resultado)
            st.download_button(
                label="📥 BAIXAR ARQUIVO .RTF",
                data=dados_rtf,
                file_name="pauta_formatada.rtf",
                mime="application/rtf"
            )
        else:
            st.error("Padrão não encontrado. Verifique se o texto colado contém as marcações RECLAMANTE/RECLAMADO.")
    else:
        st.warning("O campo está vazio.")
