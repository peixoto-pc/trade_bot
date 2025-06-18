from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, time

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           static_folder=os.path.join(os.path.dirname(__file__), 'static'),
           template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# Configurações do horário do pregão
HORA_ABERTURA = time(10, 0)  # 10:00
HORA_FECHAMENTO = time(17, 55)  # 17:55

def is_mercado_aberto():
    """Verifica se o mercado está aberto"""
    agora = datetime.now()
    hora_atual = agora.time()
    
    # Verifica se é dia útil (0 = Segunda, 6 = Domingo)
    if agora.weekday() >= 5:  # Sábado ou Domingo
        return False
        
    return HORA_ABERTURA <= hora_atual <= HORA_FECHAMENTO

# Configurar CORS e outras configurações importantes
@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

from trade_bot.config import ACOES

# Lista de ações monitoradas
ACOES_TESTE = ACOES

def get_stock_data(symbol):
    """Função para obter dados de ações"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1d')
        if not hist.empty:
            # Calcula indicadores técnicos
            rsi = np.random.randint(30, 70)  # Simula RSI por enquanto
            adx = np.random.randint(20, 40)  # Simula ADX por enquanto
            
            mercado_aberto = is_mercado_aberto()
            
            # Determina recomendação baseada nos indicadores
            if not mercado_aberto:
                recommendation = 'MERCADO FECHADO'
            elif rsi < 30 and adx > 25:
                recommendation = 'COMPRAR'
            elif rsi > 70 and adx > 25:
                recommendation = 'VENDER'
            else:
                recommendation = 'MANTER'
            
            return {
                'symbol': symbol,
                'price': float(hist['Close'].iloc[-1]),
                'rsi': rsi,
                'adx': adx,
                'recommendation': recommendation,
                'date': hist.index[-1].strftime('%Y-%m-%d %H:%M:%S'),
                'market_status': 'ABERTO' if mercado_aberto else 'FECHADO'
            }
    except Exception as e:
        logger.error(f"Erro ao buscar dados para {symbol}: {e}", exc_info=True)
    return None

def get_historical_data(symbol):
    """Obtém dados históricos para o gráfico"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1mo', interval='1d')  # Último mês com dados diários
        if not hist.empty:
            # Converte os preços para lista mantendo 2 casas decimais
            precos = [round(float(price), 2) for price in hist['Close'].tolist()]
            # Formata as datas para o padrão brasileiro
            datas = [data.strftime('%d/%m/%Y') for data in hist.index]
            
            return {
                'datas': datas,
                'precos': precos,
                'min': min(precos),
                'max': max(precos),
                'variacao': round((precos[-1] - precos[0]) / precos[0] * 100, 2)
            }
    except Exception as e:
        logger.error(f"Erro ao buscar histórico para {symbol}: {e}", exc_info=True)
        return None

@app.route('/')
def index():
    """Página inicial com dashboard"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Erro ao renderizar template: {e}", exc_info=True)
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/analise/<acao>')
def analise_acao(acao):
    """API endpoint para análise de uma ação específica"""
    data = get_stock_data(acao)
    if data is None:
        return jsonify({'erro': 'Falha ao buscar dados'}), 400
    return jsonify(data)

@app.route('/api/acoes')
def lista_acoes():
    """API endpoint para listar todas as ações monitoradas"""
    return jsonify({'acoes': ACOES_TESTE})

@app.route('/api/historico/<acao>')
def historico_acao(acao):
    """API endpoint para obter dados históricos de uma ação"""
    if acao not in ACOES_TESTE:
        return jsonify({'erro': 'Ação não encontrada'}), 404
    
    dados = get_historical_data(acao)
    if dados is None:
        return jsonify({'erro': 'Falha ao buscar dados históricos'}), 400
    
    return jsonify(dados)

@app.route('/api/stocks')
def get_stocks():
    try:
        results = []
        for symbol in ACOES_TESTE:
            data = get_stock_data(symbol)
            if data:
                results.append(data)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro ao obter dados das ações: {e}", exc_info=True)
        return jsonify({'error': 'Erro ao obter dados das ações'}), 500

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    try:
        data = get_stock_data(symbol)
        if data:
            return jsonify(data)
        return jsonify({'error': 'Ação não encontrada'}), 404
    except Exception as e:
        logger.error(f"Erro ao obter dados da ação {symbol}: {e}", exc_info=True)
        return jsonify({'error': 'Erro ao obter dados da ação'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
