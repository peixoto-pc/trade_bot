import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timedelta

def baixar_dados(acao, periodo='2y'):
    """Baixa dados com tratamento robusto de erros"""
    try:
        # Tenta baixar os dados algumas vezes em caso de falha
        for tentativa in range(3):
            try:
                dados = yf.download(
                    acao, 
                    period=periodo, 
                    interval='1d', 
                    progress=False,
                    auto_adjust=True
                )
                
                if dados is None or dados.empty:
                    print(f"Tentativa {tentativa + 1}: Sem dados para {acao}")
                    continue
                    
                # Verifica se temos as colunas necessárias
                colunas_necessarias = ['Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in dados.columns.get_level_values(0) for col in colunas_necessarias):
                    print(f"Tentativa {tentativa + 1}: Dados incompletos para {acao}")
                    continue
                
                # Simplifica as colunas se forem multiíndice
                if isinstance(dados.columns, pd.MultiIndex):
                    dados.columns = dados.columns.get_level_values(0)
                
                # Verifica se temos dados recentes
                ultima_data = dados.index[-1]
                if (pd.Timestamp.now() - ultima_data).days > 5:  # mais de 5 dias sem dados
                    print(f"Aviso: Últimos dados de {acao} são de {ultima_data.date()}")
                
                return dados
                
            except Exception as e:
                print(f"Tentativa {tentativa + 1} falhou para {acao}: {e}")
                time.sleep(2)  # Espera 2 segundos antes da próxima tentativa
                
        print(f"Todas as tentativas falharam para {acao}")
        return None
        
    except Exception as e:
        print(f"Erro ao baixar {acao}: {e}")
        return None

def calcular_rsi(df):
    """Calcula RSI manualmente"""
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14, min_periods=1).mean()  # min_periods para evitar NaN
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)  # Preencher valores NaN com 50 (neutro)

def calcular_macd(df):
    """Calcula MACD manualmente"""
    ema12 = df['Close'].ewm(span=12, adjust=False, min_periods=1).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False, min_periods=1).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False, min_periods=1).mean()
    hist = macd - signal
    return macd, signal, hist

def calcular_bollinger_bands(df, window=20, num_std=2):
    """Calcula Bandas de Bollinger"""
    sma = df['Close'].rolling(window=window, min_periods=1).mean()
    std = df['Close'].rolling(window=window, min_periods=1).std()
    upper_band = sma + (std * num_std).fillna(0)
    lower_band = sma - (std * num_std).fillna(0)
    return sma, upper_band, lower_band

def calcular_volume_relativo(df, window=20):
    """Calcula volume relativo"""
    volume_ma = df['Volume'].rolling(window=window, min_periods=1).mean()
    volume_ma = volume_ma.replace(0, 1)  # Evita divisão por zero
    return df['Volume'] / volume_ma

def calcular_adx(df, periodo=14):
    """
    Calcula o ADX (Average Directional Index)
    Retorna uma Series com os valores do ADX
    """
    try:
        # True Range
        tr1 = df['High'] - df['Low']
        tr2 = abs(df['High'] - df['Close'].shift())
        tr3 = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # +DM e -DM
        up_move = df['High'].diff()
        down_move = df['Low'].shift() - df['Low']
        
        # Filtra movimentos positivos e negativos
        pos_dm = pd.Series(0, index=df.index)
        neg_dm = pd.Series(0, index=df.index)
        
        pos_dm.loc[up_move > down_move] = up_move.loc[up_move > down_move]
        pos_dm.loc[up_move < 0] = 0
        
        neg_dm.loc[down_move > up_move] = down_move.loc[down_move > up_move]
        neg_dm.loc[down_move < 0] = 0
        
        # Suavização
        tr14 = tr.ewm(alpha=1/periodo, min_periods=periodo).mean()
        pos_dm14 = pos_dm.ewm(alpha=1/periodo, min_periods=periodo).mean()
        neg_dm14 = neg_dm.ewm(alpha=1/periodo, min_periods=periodo).mean()
        
        # +DI14 e -DI14
        pos_di14 = 100 * pos_dm14 / tr14
        neg_di14 = 100 * neg_dm14 / tr14
        
        # Calcula ADX
        dx = 100 * abs(pos_di14 - neg_di14) / (pos_di14 + neg_di14)
        adx = dx.ewm(alpha=1/periodo, min_periods=periodo).mean()
        
        # Garante que retornamos uma Series
        return pd.Series(adx, name='ADX')
        
    except Exception as e:
        print(f"Erro no cálculo do ADX: {e}")
        return pd.Series(0, index=df.index, name='ADX')

def processar_dados(dados, min_periodos=30):
    """
    Processa os dados com validações e cálculos de indicadores técnicos
    
    Args:
        dados: DataFrame com dados históricos
        min_periodos: Número mínimo de períodos necessários (default: 30)
    """
    try:
        if dados is None or dados.empty:
            return None
            
        # Cria cópia para evitar warnings do pandas
        df = dados.copy()
        
        # Simplifica o índice e as colunas
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Se as colunas são multiíndice, pega apenas o primeiro nível
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Debug
        #print(f"Quantidade inicial de dados: {len(df)}")
        #print(f"Colunas iniciais: {df.columns.tolist()}")
        
        # Verifica quantidade mínima de dados
        if len(df) < min_periodos:
            print(f"Aviso: Apenas {len(df)} períodos disponíveis (mínimo: {min_periodos})")
            return None
        
        print("Calculando indicadores técnicos...")
        
        # Médias móveis (SMA)
        df['trend_sma_fast'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['trend_sma_slow'] = df['Close'].rolling(window=50, min_periods=1).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = loss.replace(0, np.inf)  # Evita divisão por zero
        rs = gain / loss
        df['momentum_rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['Close'].ewm(span=12, adjust=False, min_periods=1).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False, min_periods=1).mean()
        df['trend_macd'] = ema12 - ema26
        df['trend_macd_signal'] = df['trend_macd'].ewm(span=9, adjust=False, min_periods=1).mean()
        df['trend_macd_hist'] = df['trend_macd'] - df['trend_macd_signal']
        
        # Bollinger Bands
        sma20 = df['Close'].rolling(window=20, min_periods=1).mean()
        std20 = df['Close'].rolling(window=20, min_periods=1).std()
        df['trend_bb_upper'] = sma20 + (std20 * 2)
        df['trend_bb_lower'] = sma20 - (std20 * 2)
        
        # Volume e indicadores de volume
        df['volume_ma20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
        volume_ma = df['volume_ma20'].replace(0, 1)  # Evita divisão por zero
        df['volume_rel'] = df['Volume'] / volume_ma
        
        print("Calculando ADX...")
        try:
            # True Range
            tr1 = df['High'] - df['Low']
            tr2 = abs(df['High'] - df['Close'].shift())
            tr3 = abs(df['Low'] - df['Close'].shift())
            tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            
            # Directional Movement
            up_move = df['High'].diff()
            down_move = df['Low'].shift() - df['Low']
            
            pos_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
            neg_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
            
            # Suavização
            periodo = 14
            tr14 = tr.ewm(alpha=1/periodo, min_periods=periodo).mean()
            pos_dm14 = pos_dm.ewm(alpha=1/periodo, min_periods=periodo).mean()
            neg_dm14 = neg_dm.ewm(alpha=1/periodo, min_periods=periodo).mean()
            
            # Directional Indicators
            pos_di14 = 100 * pos_dm14 / tr14
            neg_di14 = 100 * neg_dm14 / tr14
            
            # ADX
            dx = 100 * abs(pos_di14 - neg_di14) / (pos_di14 + neg_di14)
            df['trend_adx'] = dx.ewm(alpha=1/periodo, min_periods=periodo).mean()
            
        except Exception as e:
            print(f"Erro no cálculo do ADX: {e}")
            df['trend_adx'] = 0
        
        # Remove linhas com valores NaN
        df = df.dropna()
        
        # Debug
        #print(f"Quantidade de dados após processamento: {len(df)}")
        #print(f"Colunas disponíveis: {df.columns.tolist()}")
        
        # Verifica novamente após processamento
        if len(df) < min_periodos:
            print(f"Aviso: Dados insuficientes após processamento ({len(df)} períodos)")
            return None
            
        return df
        
    except Exception as e:
        print(f"Erro no processamento dos dados: {str(e)}")
        import traceback
        traceback.print_exc()
        return None