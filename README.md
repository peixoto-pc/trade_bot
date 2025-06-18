# trade_bot

O **trade_bot** é um robô de análise técnica para ações da bolsa brasileira, desenvolvido em Python. Ele automatiza o monitoramento de ativos, gera recomendações de compra, venda ou manutenção e disponibiliza uma interface web moderna para acompanhamento em tempo real.

## Funcionalidades

1. **Dashboard Web em Tempo Real**
   - Interface web moderna e responsiva
   - Atualização automática a cada 5 minutos
   - Contador regressivo para próxima atualização
   - Status do mercado (aberto/fechado)
   - Cards interativos para cada ativo

2. **Análise Técnica Automatizada**
   - Coleta automática de dados via `yfinance`
   - Indicadores técnicos (RSI, ADX, Volume)
   - Recomendações baseadas em múltiplos indicadores
   - Validação de sinais em tempo real

3. **Monitoramento do Mercado**
   - Horário do pregão (10:00-17:55)
   - Identificação de dias úteis
   - Status em tempo real do mercado
   - Alertas visuais de mercado fechado

4. **Visualização de Dados**
   - Cards interativos por ação
   - Modal com detalhes técnicos
   - Indicadores visuais de recomendação
   - Histórico de preços e análises

## Interface Web

### Dashboard Principal
- **Cards de Ações**
  - Preço atual
  - Recomendação (COMPRAR/VENDER/MANTER)
  - Status do mercado
  - Última atualização

### Detalhes Técnicos
- **Modal Interativo**
  - Indicadores técnicos detalhados
  - RSI (Índice de Força Relativa)
  - ADX (Average Directional Index)
  - Histórico de preços

### Funcionalidades da Interface
- **Atualização Automática**
  - Contador regressivo
  - Refresh automático dos dados
  - Cache inteligente
  - Tratamento de erros

- **Design Responsivo**
  - Layout adaptativo
  - Cores intuitivas
  - Visual moderno
  - Feedback visual das operações

## Como Usar

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

3. **Inicie o servidor web**
   ```bash
   python run_flask.py
   ```

4. **Acesse a interface**
   - Abra seu navegador em `http://localhost:5000`
   - A interface será atualizada automaticamente
   - Acompanhe as recomendações em tempo real

## Estrutura do Projeto

```
trade_bot/
├── run_flask.py        # Inicialização do servidor web
├── pyproject.toml      # Configurações do Poetry
├── README.md          # Documentação
├── tests/             # Testes automatizados
└── trade_bot/         # Código principal
    ├── config.py      # Configurações gerais
    └── src/
        ├── main.py           # Core do bot
        ├── strategy.py       # Lógica de trading
        ├── backtest.py       # Sistema de backtesting
        ├── alert_system.py   # Sistema de alertas
        └── web/             # Interface web
            ├── server.py     # Servidor Flask
            ├── static/       # Arquivos estáticos
            │   ├── css/
            │   │   └── styles.css
            │   └── js/
            │       └── main.js
            └── templates/    # Templates HTML
                └── index.html
```

## Observações

- O bot é apenas para fins educacionais e de backtesting
- Não execute operações reais sem validação humana
- Configure corretamente o fuso horário do servidor
- Mantenha a página aberta para atualizações em tempo real

## Requisitos Técnicos

- Python 3.6+
- Flask
- yfinance
- pandas
- Bootstrap 5
- Navegador moderno com JavaScript habilitado

---

## Autor

Paulo Cesar Peixoto
