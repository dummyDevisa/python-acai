# Python Açaí - Geocoding Script

Script Python para geocodificação reversa de coordenadas geográficas usando a API do Google Maps.

## Pré-requisitos

1.  **Python 3.x** instalado
2.  **API Key do Google Maps** com a **Geocoding API** habilitada

## Configuração

1.  **Clone o repositório** e navegue até a pasta do projeto.

2.  **Configure a API Key**:
    ```bash
    cp .env.example .env
    ```
    Abra o arquivo `.env` e substitua `your_api_key_here` pela sua chave da API do Google Maps:
    ```env
    GOOGLE_MAPS_API_KEY=AIzaSy...
    ```

3.  **Crie o ambiente virtual e instale as dependências**:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

## Executando o Script

```bash
python process_locations.py
```

### O que esperar
- O script carrega o arquivo CSV com os dados de localização dos pontos de açaí.
- Processa ~1700 registros com um delay de 0.1s entre requisições para respeitar limites da API.
- **Saída**: `output_enderecos.xlsx` com uma nova coluna `Endereço_Google`.

## Estrutura do Projeto

```
python-acai/
├── .env.example          # Template para configuração da API Key
├── .gitignore            # Arquivos ignorados pelo Git
├── requirements.txt      # Dependências Python
├── process_locations.py  # Script principal
├── README.md             # Este arquivo
└── *.csv                 # Arquivo de dados (não versionado)
```

## Troubleshooting

- **API Key Error**: Se aparecer "WARNING: Valid Google Maps API Key not found", verifique se renomeou `.env.example` para `.env` e adicionou sua chave.
- **Rate Limit**: Se o script parar frequentemente, o limite da API pode ter sido atingido. Verifique suas cotas no Google Cloud Console.

## Custos Estimados

Com o plano gratuito ($200 de crédito), processar ~1700 registros custa aproximadamente $8.50 (a $5/1000 requisições).
