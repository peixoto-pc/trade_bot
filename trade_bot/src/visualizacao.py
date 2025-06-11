import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def plotar_analise(dados, acao):
    """Cria um gráfico completo com todos os indicadores"""
    if dados is None or dados.empty:
        return
        
    fig, axs = plt.subplots(4, 1, figsize=(14, 12), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1, 1]})
    
    # Gráfico 1: Preço e Indicadores
    axs[0].plot(dados['Close'], label='Preço', color='black')
    axs[0].plot(dados['trend_sma_fast'], label='MM 20', color='blue', alpha=0.7)
    axs[0].plot(dados['trend_sma_slow'], label='MM 50', color='red', alpha=0.7)
    axs[0].plot(dados['trend_bb_upper'], label='BB Superior', color='gray', linestyle='--')
    axs[0].plot(dados['trend_bb_lower'], label='BB Inferior', color='gray', linestyle='--')
    
    # Marcadores de compra/venda
    compras = dados[dados['Sinal'] > 0]
    vendas = dados[dados['Sinal'] < 0]
    axs[0].scatter(compras.index, compras['Close'], color='green', marker='^', s=100, label='Compra')
    axs[0].scatter(vendas.index, vendas['Close'], color='red', marker='v', s=100, label='Venda')
    
    axs[0].set_title(f'Análise Técnica - {acao}')
    axs[0].legend()
    axs[0].grid(True)
    
    # Gráfico 2: Volume
    axs[1].bar(dados.index, dados['Volume'], color='blue', alpha=0.3)
    axs[1].plot(dados['volume_ma20'], color='red', label='Média Volume (20)')
    axs[1].set_ylabel('Volume')
    axs[1].grid(True)
    
    # Gráfico 3: RSI e ADX
    axs[2].plot(dados['momentum_rsi'], label='RSI', color='purple')
    axs[2].axhline(y=70, color='red', linestyle='--')
    axs[2].axhline(y=30, color='green', linestyle='--')
    
    if 'trend_adx' in dados.columns:
        axs[2].plot(dados['trend_adx'], label='ADX', color='orange')
        axs[2].axhline(y=25, color='gray', linestyle='--')
    
    axs[2].set_ylabel('Indicadores')
    axs[2].legend()
    axs[2].grid(True)
    
    # Gráfico 4: MACD
    axs[3].plot(dados['trend_macd'], label='MACD', color='blue')
    axs[3].plot(dados['trend_macd_signal'], label='Sinal', color='red')
    axs[3].bar(dados.index, dados['trend_macd_hist'], color=np.where(dados['trend_macd_hist'] > 0, 'green', 'red'))
    axs[3].axhline(y=0, color='black', linestyle='-')
    axs[3].set_ylabel('MACD')
    axs[3].legend()
    axs[3].grid(True)
    
    # Formatar eixos de data
    axs[3].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'analise_{acao.replace(".SA", "")}.png', dpi=300)
    plt.close()