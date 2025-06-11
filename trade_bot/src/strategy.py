import pandas as pd
import numpy as np
from config import PARAMS

def gerar_sinais(dados):
    """Gera sinais com múltiplos critérios e tratamento robusto de índices"""
    if dados is None or dados.empty:
        return None
        
    try:
        df = dados.copy()
        
        # Verifica colunas necessárias
        colunas_necessarias = [
            'momentum_rsi', 'trend_macd', 'trend_macd_signal', 'trend_macd_hist',
            'trend_sma_fast', 'trend_sma_slow', 'trend_bb_upper', 'trend_bb_lower',
            'volume_rel', 'Close'
        ]
        
        for col in colunas_necessarias:
            if col not in df.columns:
                raise ValueError(f"Coluna obrigatória {col} não encontrada")
        
        # Tornar ADX opcional
        adx_disponivel = 'trend_adx' in df.columns
        
        # 1. Criar condições como Series temporárias com mesmo índice
        rsi_sobrevendido = (df['momentum_rsi'] < PARAMS['rsi_compra'])
        rsi_sobrecomprado = (df['momentum_rsi'] > PARAMS['rsi_venda'])
        
        macd_cruzamento = (df['trend_macd'] > df['trend_macd_signal'])
        macd_cruzamento_negativo = (df['trend_macd'] < df['trend_macd_signal'])
        
        macd_hist_positivo = (df['trend_macd_hist'] > 0)
        macd_hist_negativo = (df['trend_macd_hist'] < 0)
        
        media_curta_acima = (df['trend_sma_fast'] > df['trend_sma_slow'])
        media_curta_abaixo = (df['trend_sma_fast'] < df['trend_sma_slow'])
        
        abaixo_bb = (df['Close'] < df['trend_bb_lower'])
        acima_bb = (df['Close'] > df['trend_bb_upper'])
        
        volume_alto = (df['volume_rel'] > PARAMS['volume_min'])
        
        # ADX é opcional
        if adx_disponivel:
            tendencia_forte = (df['trend_adx'] > PARAMS['adx_min'])
            tendencia_forte_venda = (df['trend_adx'] > PARAMS['adx_min'])
        else:
            # Criar Series de True com mesmo índice
            tendencia_forte = pd.Series(True, index=df.index)
            tendencia_forte_venda = pd.Series(True, index=df.index)
            print("ADX não disponível, ignorando critério de tendência forte")
        
        # 2. Garantir alinhamento de todos os índices
        condicoes = [
            rsi_sobrevendido, macd_cruzamento, macd_hist_positivo, 
            media_curta_acima, abaixo_bb, volume_alto, tendencia_forte,
            rsi_sobrecomprado, macd_cruzamento_negativo, macd_hist_negativo,
            media_curta_abaixo, acima_bb, volume_alto, tendencia_forte_venda
        ]
        
        # Alinhar todas as condições
        for i in range(len(condicoes)):
            condicoes[i], _ = condicoes[i].align(df, axis=0, copy=False)
            condicoes[i].fillna(False, inplace=True)
        
        # Separar condições novamente após alinhamento
        (rsi_sobrevendido, macd_cruzamento, macd_hist_positivo, 
         media_curta_acima, abaixo_bb, volume_alto, tendencia_forte,
         rsi_sobrecomprado, macd_cruzamento_negativo, macd_hist_negativo,
         media_curta_abaixo, acima_bb, volume_alto_venda, tendencia_forte_venda) = condicoes
        
        # 3. Sinais com múltiplas confirmações
        df['Sinal'] = 0  # Neutro
        
        # Compra Forte: Todos os critérios positivos
        compra_forte = (rsi_sobrevendido & macd_cruzamento & macd_hist_positivo & 
                        media_curta_acima & abaixo_bb & volume_alto & tendencia_forte)
        
        # Compra Moderada: Pelo menos 5 critérios positivos
        compra_moderada = (
            rsi_sobrevendido.astype(int) + 
            macd_cruzamento.astype(int) + 
            macd_hist_positivo.astype(int) + 
            media_curta_acima.astype(int) + 
            abaixo_bb.astype(int) + 
            volume_alto.astype(int) + 
            tendencia_forte.astype(int)
        ) >= 5
        
        # Venda Forte: Todos os critérios negativos
        venda_forte = (rsi_sobrecomprado & macd_cruzamento_negativo & macd_hist_negativo & 
                       media_curta_abaixo & acima_bb & volume_alto_venda & tendencia_forte_venda)
        
        # Venda Moderada: Pelo menos 5 critérios negativos
        venda_moderada = (
            rsi_sobrecomprado.astype(int) + 
            macd_cruzamento_negativo.astype(int) + 
            macd_hist_negativo.astype(int) + 
            media_curta_abaixo.astype(int) + 
            acima_bb.astype(int) + 
            volume_alto_venda.astype(int) + 
            tendencia_forte_venda.astype(int)
        ) >= 5
        
        # Atribuição de sinais
        df.loc[compra_forte, 'Sinal'] = 2  # Compra Forte
        df.loc[compra_moderada & ~compra_forte, 'Sinal'] = 1  # Compra Moderada
        df.loc[venda_forte, 'Sinal'] = -2  # Venda Forte
        df.loc[venda_moderada & ~venda_forte, 'Sinal'] = -1  # Venda Moderada
        
        # Sinal final considerando múltiplas confirmações
        sinais = pd.DataFrame(index=df.index)
        sinais['Sinal'] = 0  # 0=Neutro, 1=Compra, -1=Venda
        
        # Validar tendência com ADX e médias móveis
        tendencia_alta = (df['trend_sma_fast'] > df['trend_sma_slow']) & (df['trend_adx'] > PARAMS['adx_min'])
        tendencia_baixa = (df['trend_sma_fast'] < df['trend_sma_slow']) & (df['trend_adx'] > PARAMS['adx_min'])
        
        # Condições de volume
        volume_relevante = df['volume_rel'] > PARAMS['volume_min']
        
        # Condições de RSI
        rsi_sobrevendido = df['momentum_rsi'] < PARAMS['rsi_compra']
        rsi_sobrecomprado = df['momentum_rsi'] > PARAMS['rsi_venda']
        
        # Condições de Bollinger Bands
        preco_na_banda_inferior = df['Close'] <= df['trend_bb_lower']
        preco_na_banda_superior = df['Close'] >= df['trend_bb_upper']
        
        # Sinais de compra
        sinais.loc[
            tendencia_alta & 
            volume_relevante & 
            rsi_sobrevendido & 
            preco_na_banda_inferior, 'Sinal'] = 1
            
        # Sinais de venda
        sinais.loc[
            tendencia_baixa & 
            volume_relevante & 
            rsi_sobrecomprado & 
            preco_na_banda_superior, 'Sinal'] = -1
            
        # Combinar sinais
        df['Sinal'] = sinais['Sinal'].combine(df['Sinal'], lambda x, y: x if x != 0 else y)
        
        return df
        
    except Exception as e:
        print(f"Erro ao gerar sinais: {e}")
        import traceback
        traceback.print_exc()
        return None