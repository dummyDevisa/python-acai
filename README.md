# Projeto Açaí no Ponto - Georreferenciamento e Análise

Este projeto contém ferramentas para processar, enriquecer e visualizar dados de localização de pontos de venda de açaí em Belém, originários do cadastro realizado por Agentes Comunitários de Saúde (ACSs) na iniciativa "Açaí no Ponto".

## Funcionalidades

1.  **Geocodificação Reversa:** Converte coordenadas geográficas (Latitude/Longitude) em endereços completos usando a Google Maps API.
2.  **Tratamento de Endereços:** "Limpa" e estrutura os endereços retornados pelo Google em colunas separadas (Logradouro, Número, Bairro, CEP, Município, Estado).
3.  **Geração de Relatório Web:** Compila um relatório administrativo e a tabela de dados em uma página HTML interativa (com busca e paginação), pronta para publicação (GitHub Pages).

## Estrutura do Projeto

*   `process_locations.py`: Script principal que consulta a API do Google.
*   `parse_addresses.py`: Script que estrutura os endereços textuais em colunas.
*   `generate_site.py`: Gera o arquivo `index.html` com o relatório e os dados.
*   `Relatorio_Projeto_Acai.md`: O texto do relatório administrativo.
*   `requirements.txt`: Dependências do Python.

## Como Executar

### 1. Configuração Inicial

Certifique-se de ter o Python instalado.

```bash
# Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Instale as dependências
pip install -r requirements.txt

# Configure a chave de API
# Renomeie .env.example para .env e adicione sua GOOGLE_MAPS_API_KEY
```

### 2. Executar o Processamento

Siga a ordem dos scripts para gerar o resultado final:

**Passo 1: Obter Endereços (Geocoding)**
Lê o CSV original e consulta a API do Google.
```bash
python process_locations.py
```
*Gera: `output_enderecos.xlsx`*

**Passo 2: Tratar e Estruturar Dados**
Separa o endereço completo em colunas (Rua, Bairro, CEP, etc).
```bash
python parse_addresses.py
```
*Gera: `output_enderecos_tratado.xlsx`*

**Passo 3: Gerar Site/Relatório**
Cria uma página HTML com o relatório e a tabela de dados.
```bash
python generate_site.py
```
*Gera: `index.html`*

## Contexto

Este trabalho foi desenvolvido para atender uma demanda da **Gerência da Casa do Açaí / Vigilância Sanitária de Belém**, visando transformar dados brutos de localização em informações úteis para fiscalização e integração futura com o sistema **Visabelem.net**.
