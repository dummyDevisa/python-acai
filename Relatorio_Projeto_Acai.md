# Relatório Técnico-Administrativo: Georreferenciamento Casa do Açaí

**Para:** Coordenação da Vigilância Sanitária / Gerência da Casa do Açaí  
**De:** Daniel Santos  
**Assunto:** Recuperação de endereços da base "Açaí no Ponto" e estratégia para o Visabelem.net

---

## 1. Objeto
Atendendo à solicitação da Gerência da Casa do Açaí, foi realizado o processamento da base de dados do projeto **"Açaí no Ponto"** — iniciativa firmada entre MPPA, Prefeitura de Belém e UFPA.

Embora as estimativas oficiais do projeto apontassem para a existência de cerca de **8.000 batedores artesanais** na capital, a base de dados consolidada nesta etapa conteve aproximadamente **1.700 registros** com coordenadas geográficas coletadas pelos Agentes Comunitários de Saúde (ACSs). O trabalho técnico consistiu em converter essas coordenadas em endereços textuais estruturados (logradouro, bairro e CEP) para viabilizar o uso administrativo desses dados.

## 2. Execução
Para o processamento, utilizou-se a API da Google Cloud Platform (Google Maps), validando a tecnologia de georreferenciamento reverso.

**Resultado:** A base de ~1.700 estabelecimentos foi enriquecida com endereços precisos. Contudo, a disparidade entre o quantitativo esperado (8.000) e o coletado (1.700) evidencia a necessidade de estratégias mais abrangentes para alcançar a totalidade do setor.

## 3. Integração Estratégica ao Sistema Visabelem.net
O Visabelem.net (em homologação, piloto previsto para 2026) será a ferramenta chave para cobrir a lacuna de dados identificada. Diferente da ação pontual com ACSs, o novo sistema permitirá o **cadastramento contínuo e descentralizado** por múltiplos atores:

1.  **Auto-Cadastro pelo Usuário:** O próprio batedor/manipulador de alimentos poderá cadastrar seu estabelecimento. O sistema facilitará esse processo convertendo automaticamente o endereço digitado em coordenadas (e vice-versa), removendo barreiras técnicas.
2.  **Cadastro e Fiscalização (Agentes VISA):** Fiscais e Agentes de Vigilância Sanitária terão ferramentas móveis para cadastrar e validar pontos "in loco" (geo-localização em 1 clique) durante as rotinas diárias, ampliando gradualmente a base até o patamar estimado de 8 mil pontos.
3.  **Roteirização Inteligente:** Funcionalidade para criar rotas otimizadas de inspeção, aumentando a produtividade das equipes de campo.

## 4. Custos Estimados de Infraestrutura
Para suportar essa operação expandida (até 10.000 requisições mensais), os custos operacionais projetados são:

| Item | Descrição | Estimativa de Custo |
| :--- | :--- | :--- |
| **Google Maps Platform** | Serviços de mapas, geocodificação e rotas. | *Coberto pelo crédito gratuito mensal da plataforma ($200 USD) para o volume estimado.* |
| **Servidor VPS e Domínio** | Hospedagem da aplicação, banco de dados e endereço web. | **~R$ 400,00 anuais** (aprox. R$ 33,50/mês) |

**Observação:** O custo da API do Google Maps é variável conforme o uso. Dentro da margem de 10.000 requisições mensais simples, o valor tende a permanecer coberto pela faixa gratuita do serviço.

Atenciosamente,

**Daniel Santos**
