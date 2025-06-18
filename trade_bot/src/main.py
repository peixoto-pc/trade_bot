import time
from trade_bot.src.data_pipeline import baixar_dados, processar_dados
from trade_bot.src.strategy import gerar_sinais
from trade_bot.config import ACOES, ADX_LIMITE, RSI_SOBRECOMPRADO, RSI_SOBREVENDIDO, VOLUME_MIN
from trade_bot.src.visualizacao import plotar_analiseime
import schedule
import pandas as pd
from datetime import datetime
from .data_pipeline import baixar_dados, processar_dados
from .strategy import gerar_sinais
from ..config import ACOES, ADX_LIMITE, RSI_SOBRECOMPRADO, RSI_SOBREVENDIDO, VOLUME_MIN
from .visualizacao import plotar_analise

def gerar_recomendacao(acao):
    """Gera recomendação com tratamento completo de erros"""
    try:
        # Aumentar o período de dados para garantir quantidade suficiente
        periodo_ajustado = "2y"  # Usar 2 anos de dados históricos
        dados = baixar_dados(acao, periodo=periodo_ajustado)
        
        if dados is None or dados.empty:
            print(f"Erro: Dados não disponíveis para {acao}")
            return f"Erro: Dados não disponíveis para {acao}", None
        
        # Processar dados com quantidade mínima de períodos
        processados = processar_dados(dados, min_periodos=50)
        if processados is None:
            print(f"Erro: Dados insuficientes para análise de {acao}")
            return f"Erro: Dados insuficientes para análise de {acao}", None
            
        # GERAR SINAIS
        com_sinais = gerar_sinais(processados)
        if com_sinais is None or com_sinais.empty:
            return f"Erro: Falha ao gerar sinais para {acao}", None
            
        # Garante que estamos pegando o último valor escalar
        ultimo_sinal = com_sinais['Sinal'].iloc[-1]
        preco_atual = float(com_sinais['Close'].iloc[-1])  # Conversão explícita para float
        
        if ultimo_sinal == 1:
            return f"COMPRAR {acao} a R${preco_atual:.2f}", com_sinais
        elif ultimo_sinal == -1:
            return f"VENDER {acao} a R${preco_atual:.2f}", com_sinais
        else:
            return f"MANTER {acao} - Neutro (R${preco_atual:.2f})", com_sinais
            
        # Extração segura dos valores
        ultimo_sinal = int(com_sinais['Sinal'].iloc[-1])
        preco_atual = float(com_sinais['Close'].iloc[-1])
        rsi_atual = com_sinais['momentum_rsi'].iloc[-1]
        volume_rel = com_sinais['volume_rel'].iloc[-1]
        adx_atual = com_sinais['trend_adx'].iloc[-1] if 'trend_adx' in com_sinais.columns else 0
        
        # Determinar força do sinal
        if abs(ultimo_sinal) == 2:
            intensidade = "FORTE"
        elif abs(ultimo_sinal) == 1:
            intensidade = "MODERADO"
        else:
            intensidade = "NEUTRO"
        
        # Formatar mensagem
        if ultimo_sinal > 0:
            return f"COMPRA {intensidade} {acao} a R${preco_atual:.2f} (RSI: {rsi_atual:.1f}, Vol: {volume_rel:.1f}x, ADX: {adx_atual:.1f})", com_sinais
        elif ultimo_sinal < 0:
            return f"VENDA {intensidade} {acao} a R${preco_atual:.2f} (RSI: {rsi_atual:.1f}, Vol: {volume_rel:.1f}x, ADX: {adx_atual:.1f})", com_sinais
        else:
            return f"MANTER {acao} - Neutro (R${preco_atual:.2f}, RSI: {rsi_atual:.1f})", com_sinais
            
    except Exception as e:
        print(f"Erro ao processar {acao}: {str(e)}")
        return f"Erro ao processar {acao}: {str(e)}", None

def validar_sinal(dados, sinal):
    """Validação adicional do sinal"""
    if sinal == 0:
        return True
        
    # Pegar últimos valores
    rsi = dados['momentum_rsi'].iloc[-1]
    volume = dados['volume_rel'].iloc[-1]
    adx = dados['trend_adx'].iloc[-1]
    
    # Validações adicionais
    if sinal > 0:  # Compra
        return (
            rsi < RSI_SOBRECOMPRADO and
            volume > VOLUME_MIN and
            adx > ADX_LIMITE
        )
    else:  # Venda
        return (
            rsi > RSI_SOBREVENDIDO and
            volume > VOLUME_MIN and
            adx > ADX_LIMITE
        )

def monitorar_acoes():
    print(f"\n{datetime.now()}: Analisando ações...")
    for acao in ACOES:
        recomendacao, dados = gerar_recomendacao(acao)
        print(recomendacao)
        
        # Salvar gráfico de análise
        if dados is not None and not dados.empty:
            plotar_analise(dados, acao)

def main():
    # Teste inicial
    monitorar_acoes()
    
    # Agendamento (opcional)
    schedule.every().hour.do(monitorar_acoes)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\nErro durante o monitoramento: {str(e)}")
    finally:
        print("Encerrando bot de trading...")

if __name__ == "__main__":
    main()