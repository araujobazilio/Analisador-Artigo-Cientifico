import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
import json
import re
import fitz  # PyMuPDF
from datetime import datetime

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da chave da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuração do modelo com verbose
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY,
    verbose=True
)

def extract_text_from_pdf(file):
    st.info("Processando o PDF...", icon="📄")
    try:
        # Salvar o arquivo temporariamente
        with open("temp.pdf", "wb") as f:
            f.write(file.getbuffer())
        
        # Abrir o PDF com PyMuPDF
        doc = fitz.open("temp.pdf")
        
        # Extrair texto de todas as páginas
        full_text = ""
        for page in doc:
            # Tentar extrair texto de diferentes maneiras
            page_text = page.get_text("text")
            
            # Se o texto estiver vazio, tentar extração de texto de blocos
            if not page_text.strip():
                page_text = page.get_text("blocks")
            
            full_text += page_text + "\n\n"
        
        # Fechar o documento
        doc.close()
        
        # Verificar se o texto extraído não está vazio
        if not full_text.strip():
            st.error("Não foi possível extrair texto do PDF. O arquivo pode estar em um formato não suportado.")
            return ""
        
        return full_text
    
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
        return ""
    finally:
        # Sempre tente remover o arquivo temporário
        try:
            os.remove("temp.pdf")
        except:
            pass

class ArticleAnalyzer:
    def __init__(self, text):
        self.text = text
        self.llm = llm

    def analyze_article(self):
        # Prompts para análise do artigo seguindo critérios acadêmicos
        prompts = [
            ("Metadados do Artigo", 
             "Extraia os metadados principais do artigo: título, autores, instituições, data de publicação e periódico."),
            
            ("Relevância e Contribuição", """
             Avalie os seguintes aspectos:
             1. Relevância e atualidade do tema
             2. Contribuição original para o conhecimento
             3. Potencial impacto na área
             4. Aplicabilidade dos resultados
             """),
            
            ("Clareza e Estrutura", """
             Analise a qualidade da redação e estrutura:
             1. Clareza e objetividade da linguagem
             2. Coerência na estrutura do texto
             3. Organização lógica das seções
             4. Qualidade dos elementos visuais (tabelas, figuras)
             """),
            
            ("Rigor Metodológico", """
             Avalie o rigor metodológico considerando:
             1. Detalhamento da metodologia
             2. Adequação dos métodos aos objetivos
             3. Possibilidade de replicação
             4. Técnicas estatísticas (se aplicável)
             5. Controle de variáveis
             """),
            
            ("Coerência da Pesquisa", """
             Analise a coerência entre:
             1. Objetivos propostos
             2. Hipóteses formuladas
             3. Resultados obtidos
             4. Conclusões apresentadas
             5. Alinhamento com a pergunta de pesquisa
             """),
            
            ("Fundamentação Teórica", """
             Avalie a revisão de literatura:
             1. Abrangência da revisão
             2. Atualidade das referências
             3. Crítica da literatura existente
             4. Contextualização do estudo
             5. Justificativa da pesquisa
             """),
            
            ("Qualidade das Referências", """
             Analise as referências quanto a:
             1. Credibilidade das fontes
             2. Atualidade das citações
             3. Pertinência ao tema
             4. Diversidade de fontes
             5. Adequação às normas acadêmicas
             """),
            
            ("Aspectos Éticos", """
             Verifique:
             1. Declaração de conflitos de interesse
             2. Aprovação ética (quando aplicável)
             3. Transparência nos dados
             4. Rigor nas citações
             5. Originalidade do trabalho
             """),
            
            ("Impacto e Aplicações", """
             Avalie:
             1. Relevância prática dos resultados
             2. Potencial de impacto acadêmico
             3. Implicações para políticas públicas
             4. Contribuições para a área
             5. Sugestões para pesquisas futuras
             """),
            
            ("Avaliação Final", """
             Forneça uma avaliação geral do artigo:
             1. Pontos fortes principais
             2. Limitações identificadas
             3. Nota geral (0-10)
             4. Recomendações para melhoria
             5. Conclusão sobre a qualidade geral
             """)
        ]
        
        # Gerar relatório
        report = "ANÁLISE DETALHADA DO ARTIGO CIENTÍFICO\n"
        report += "=" * 40 + "\n\n"
        
        for section_title, prompt in prompts:
            try:
                response = self.llm.invoke(f"{prompt}\n\nTexto do artigo:\n{self.text[:5000]}")
                report += f"\n{section_title}\n{'-' * len(section_title)}\n{response.content}\n"
            except Exception as e:
                report += f"\n{section_title}\n{'-' * len(section_title)}\nErro na análise: {str(e)}\n"
        
        return report

def create_report(analyzer):
    st.info("Iniciando análise completa...", icon="🔍")
    
    # Gerar relatório de texto
    report_text = analyzer.analyze_article()
    
    # Exibir relatório
    st.text_area("Relatório de Análise", report_text, height=600)
    
    return report_text

# Interface no Streamlit
st.set_page_config(page_title="Análise de Artigos Científicos", layout="wide")
st.title(" Análise Inteligente de Artigos Científicos")
st.write("Faça upload de um artigo em PDF para obter uma análise detalhada")

# Upload do PDF
uploaded_file = st.file_uploader("Envie um artigo em PDF", type=["pdf"])

if uploaded_file:
    # Extrair texto
    extracted_text = extract_text_from_pdf(uploaded_file)
    
    # Verificação adicional de texto
    if not extracted_text or len(extracted_text.strip()) < 50:
        st.error(" Falha na extração de texto do PDF")
        st.warning("""
        Possíveis razões:
        1. O PDF pode estar protegido contra cópia
        2. O documento pode ser uma imagem digitalizada
        3. O arquivo pode estar corrompido
        
        Sugestões:
        - Verifique se o PDF é legível
        - Tente converter o PDF para texto
        - Use um PDF com texto selecionável
        """)
    else:
        # Criar analisador
        analyzer = ArticleAnalyzer(extracted_text)
        
        # Gerar relatório
        report = create_report(analyzer)
        
        # Botão para download
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"relatorio_artigo_{timestamp}.txt"
        st.download_button(
            " Baixar Relatório Completo",
            data=report,
            file_name=report_name,
            mime="text/plain"
        )