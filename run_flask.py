#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configurar os caminhos
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))
logger.debug(f"Python path: {sys.path}")

# Configurar variáveis de ambiente para o Flask
os.environ['FLASK_APP'] = 'trade_bot.src.web.server'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

if __name__ == '__main__':
    try:
        from trade_bot.src.web.server import app
        logger.info(f"Server starting at http://localhost:5000")
        logger.info(f"Static folder: {app.static_folder}")
        logger.info(f"Template folder: {app.template_folder}")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor: {e}", exc_info=True)
