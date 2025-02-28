# Analisador de Artigos Científicos

## Descrição
Ferramenta de análise inteligente de artigos científicos utilizando IA generativa.

## Requisitos
- Python 3.8+
- Bibliotecas:
  - streamlit
  - langchain
  - openai
  - PyMuPDF
  - tiktoken

## Instalação
1. Clone o repositório
2. Crie um ambiente virtual
```bash
python -m venv venv
```

3. Ative o ambiente virtual
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Instale as dependências
```bash
pip install -r requirements.txt
```

## Execução
```bash
streamlit run app.py
```

## Uso
1. Faça upload de um artigo em PDF
2. Aguarde a análise
3. Visualize ou baixe o relatório gerado

## Configurações
- Chave da OpenAI deve ser configurada como variável de ambiente ou no código

## Limitações
- Suporte apenas para PDFs com texto selecionável
- Qualidade da análise depende do modelo de IA

## Contribuições
Pull requests são bem-vindos. Para mudanças importantes, abra uma issue primeiro.
