# Configurações gerais
PERIODO_DADOS = "2y"
MIN_PERIODOS = 50

# Lista de ações para monitorar
#ACOES = ["PETR4.SA"]

# Configurações de análise técnica
RSI_PERIODO = 14
RSI_SOBRECOMPRADO = 70
RSI_SOBREVENDIDO = 30

# Médias móveis
SMA_RAPIDA = 20
SMA_LENTA = 50

# Configurações de tendência
ADX_PERIODO = 14
ADX_LIMITE = 25  # Força mínima da tendência

# Configurações de volume
VOLUME_MIN = 1.5  # Volume mínimo em relação à média

# Configurações de Bollinger Bands
BB_PERIODO = 20
BB_DESVIO = 2

# Configurações da estratégia
PARAMS = {
    # RSI
    'rsi_compra': 35,
    'rsi_venda': 70,
    
    # Médias Móveis
    'media_rapida': 20,
    'media_lenta': 50,
    
    # Volume
    'volume_min': 1.5,  # Volume 50% acima da média
    
    # ADX
    'adx_min': 25,  # Valor mínimo para considerar tendência forte
    'usar_adx': False  # Desativado até resolvermos os problemas
}

# Lista de ações
ACOES = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'WEGE3.SA', 'MGLU3.SA', 'LREN3.SA', 'BBAS3.SA', 'BPAC11.SA']