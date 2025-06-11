# trade_bot

O **trade_bot** é um robô de análise técnica para ações da bolsa brasileira, desenvolvido em Python. Ele automatiza o monitoramento de ativos, gera recomendações de compra, venda ou manutenção e salva gráficos de análise técnica, tudo de forma agendada e contínua.

## Como funciona

1. **Coleta de Dados**
   - O bot utiliza a biblioteca `yfinance` para baixar dados históricos de preços e volumes das ações configuradas.
   - O período padrão é de 2 anos, garantindo uma base robusta para análise.

2. **Processamento e Indicadores Técnicos**
   - Calcula indicadores clássicos como:
     - Médias móveis (curta e longa)
     - RSI (Índice de Força Relativa)
     - MACD
     - Bandas de Bollinger
     - ADX (Average Directional Index)
     - Volume relativo e média de volume

3. **Geração de Sinais**
   - A função de estratégia avalia os indicadores e gera sinais:
     - **1**: Compra
     - **-1**: Venda
     - **0**: Manter/Neutro
   - Os sinais são baseados em múltiplas confirmações, como tendência (médias móveis + ADX), volume acima da média, RSI em regiões de sobrevenda/sobrecompra e preço nas bandas de Bollinger.

4. **Validação dos Sinais**
   - Antes de recomendar uma operação, o bot valida se os critérios de força de tendência, volume e RSI estão de acordo com os parâmetros definidos.

5. **Recomendações e Visualização**
   - O bot imprime recomendações no terminal e salva gráficos de análise técnica para cada ativo monitorado.

6. **Execução Contínua e Agendamento**
   - O monitoramento é feito automaticamente a cada hora (ou outro intervalo configurado), graças ao agendador `schedule`.
   - O loop principal mantém o bot rodando continuamente, pronto para novas análises.

## Como usar

1. **Instale as dependências**
   
   Recomendado usar um ambiente virtual. Com `poetry`:
   ```bash
   poetry install
   ```
   Ou com `pip`:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure os parâmetros**
   - Edite o arquivo `config.py` para definir as ações a serem monitoradas e os parâmetros dos indicadores.

3. **Execute o bot**
   ```bash
   python trade_bot/src/main.py
   ```

4. **Resultados**
   - As recomendações aparecerão no terminal.
   - Os gráficos de análise serão salvos como arquivos PNG na pasta do projeto.

## Estrutura do Projeto

- `src/main.py` — Script principal, agendamento e orquestração
- `src/data_pipeline.py` — Download e processamento dos dados
- `src/strategy.py` — Lógica de geração de sinais
- `src/visualizacao.py` — Geração dos gráficos
- `config.py` — Parâmetros e lista de ativos
- `README.md` — Este arquivo

## Observações
- O bot é apenas para fins educacionais e de backtesting. Não execute operações reais sem validação humana.
- Para enviar alertas por e-mail, configure as variáveis no `.env` e ajuste o `alert_system.py`.

---

**Desenvolvido por Paulo Cesar Peixoto**
