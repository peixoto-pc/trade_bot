from data_pipeline import calcular_adx, baixar_dados
import pandas as pd

# Teste com dados reais
print("Testando cálculo do ADX...")
dados = baixar_dados('PETR4.SA')
if dados is not None:
    dados['trend_adx'] = calcular_adx(dados)
    
    if dados['trend_adx'] is not None:
        print("ADX calculado com sucesso!")
        print("Últimos valores de ADX:")
        print(dados[['Close', 'trend_adx']].tail())
    else:
        print("Falha ao calcular ADX")
else:
    print("Falha ao baixar dados")