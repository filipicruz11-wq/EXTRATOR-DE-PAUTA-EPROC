import streamlit as st
import re

# Configuração da página
st.set_page_config(page_title="Extrator Judiciário", layout="wide")

def tratar_nomes_judiciais(texto_nomes, sufixo_tipo):
    """
    Identifica se há múltiplos nomes baseados na repetição de '- RECLAMANTE' ou '- RECLAMADO'
    """
    # Procura por todos os nomes que vêm antes do traço identificador
    # Ex: Captura 'NOME' em 'NOME - RECLAMADO'
    padrao_nome = rf"(.*?)\s*-\s*{sufixo_tipo}"
    achados = re.findall(padrao_nome, texto_nomes, re.IGNORECASE)
    
    if not achados:
        return "NÃO IDENTIFICADO"
    
    primeiro_nome = achados[0].strip().upper()
    
    # Se houver mais de um item na lista, adiciona 'E OUTROS'
    if len(achados) > 1:
        return f"{primeiro_nome} E OUTROS"
    
    return primeiro_nome

def extrair_dados_pauta_judicial(texto_pauta):
    # Regex atualizado para capturar o BLOCO INTEIRO de autores e réus
    # Ele pega tudo entre 'Autor' e 'X', e entre 'Réu' e o próximo processo (ou fim do texto)
    padrao_bloco = r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})/SP.*?Autor\s+(.*?)\s+X\s+Réu\s+(.*?)(?=\d{7}-\d{2}\.\d{4}|\Z)"
    
    blocos = re.findall(padrao_bloco, texto_pauta, re.DOTALL)
    resultados = []

    for num_processo, bloco_autor, bloco_reu in blocos:
        # Processa os nomes dentro de cada bloco
        requerente = tratar_nomes_judiciais(bloco_autor, "RECLAMANTE")
        requerido = tratar_nomes_judiciais(bloco_reu, "RECLAMADO")
        
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
            st.success("Dados processados com sucesso!")
            st.text_area("PRÉ-VISUALIZAÇÃO:", value=resultado, height=300)
            dados_rtf = gerar_rtf(resultado)
            st.download_button(
                label="📥 BAIXAR ARQUIVO .RTF",
                data=dados_rtf,
                file_name="pauta_formatada.rtf",
                mime="application/rtf"
            )
        else:
            st.error("Não foi possível encontrar o padrão de processo. Verifique a formatação.")
    else:
        st.warning("O campo está vazio.")
