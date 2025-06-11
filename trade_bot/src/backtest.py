import matplotlib.pyplot as plt

def executar_backtest(dados):
    dados['Retorno_Strategy'] = dados['Retorno'] * dados['Sinal'].shift(1)
    dados['Retorno_Acum'] = (1 + dados['Retorno']).cumprod()
    dados['Retorno_Strategy_Acum'] = (1 + dados['Retorno_Strategy']).cumprod()
    return dados

def plotar_resultados(dados, acao):
    plt.figure(figsize=(12,6))
    plt.plot(dados['Retorno_Acum'], label='Buy & Hold')
    plt.plot(dados['Retorno_Strategy_Acum'], label='Estratégia')
    plt.title(f'Desempenho: {acao}')
    plt.legend()
    plt.savefig(f'resultados_{acao.split(".")[0]}.png')
    plt.close()