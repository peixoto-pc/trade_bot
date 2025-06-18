// Configurações
const UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutos em milissegundos
const API_BASE_URL = window.location.origin;

// Cache para armazenar os dados das ações
let acoesCache = new Map();
let proximaAtualizacao = Date.now() + UPDATE_INTERVAL;

// Função para formatar valores monetários
const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
};

// Função para formatar data/hora
const formatarData = (dataStr) => {
    return new Date(dataStr).toLocaleString('pt-BR');
};

// Função para obter classe do badge baseado na recomendação
const getRecomendacaoClass = (recomendacao) => {
    if (recomendacao === 'MERCADO FECHADO') {
        return 'bg-secondary';
    }
    switch (recomendacao) {
        case 'COMPRAR':
            return 'bg-success';
        case 'VENDER':
            return 'bg-danger';
        default:
            return 'bg-warning';
    }
};

// Função para formatar o tempo restante
const formatarTempoRestante = (ms) => {
    if (ms < 0) return '0:00';
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

// Função para atualizar o contador
function atualizarContador() {
    const tempoRestante = proximaAtualizacao - Date.now();
    const contadorEl = document.getElementById('contador-atualizacao');
    if (contadorEl) {
        contadorEl.textContent = formatarTempoRestante(tempoRestante);
    }
}

// Função para buscar dados de todas as ações
async function buscarTodasAcoes() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stocks`);
        if (!response.ok) throw new Error('Falha ao buscar dados');
        const dados = await response.json();
        // Atualizar próxima atualização
        proximaAtualizacao = Date.now() + UPDATE_INTERVAL;
        return dados;
    } catch (error) {
        console.error('Erro ao buscar dados das ações:', error);
        return [];
    }
}

// Função para buscar dados de uma ação específica
async function buscarDadosAcao(acao) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stock/${acao}`);
        if (!response.ok) throw new Error('Falha ao buscar dados');
        const dados = await response.json();
        acoesCache.set(acao, dados);
        return dados;
    } catch (error) {
        console.error(`Erro ao buscar dados para ${acao}:`, error);
        return null;
    }
}

// Função para atualizar um card de ação
function atualizarCardAcao(card, dados) {
    if (!dados) return;
    
    card.querySelector('.preco').textContent = formatarMoeda(dados.price);
    
    const recomendacaoEl = card.querySelector('.recomendacao');
    recomendacaoEl.textContent = dados.recommendation;
    recomendacaoEl.className = 'recomendacao badge ' + getRecomendacaoClass(dados.recommendation);
    
    card.querySelector('.ultima-atualizacao').textContent = formatarData(dados.date);
    
    // Atualizar classes de estilo baseado na recomendação
    const cardEl = card.querySelector('.card');
    cardEl.classList.remove('border-success', 'border-danger', 'border-warning', 'border-secondary');
    
    if (dados.recommendation === 'MERCADO FECHADO') {
        cardEl.classList.add('border-secondary');
        cardEl.classList.add('mercado-fechado');
    } else {
        cardEl.classList.remove('mercado-fechado');
        switch (dados.recommendation) {
            case 'COMPRAR':
                cardEl.classList.add('border-success');
                break;
            case 'VENDER':
                cardEl.classList.add('border-danger');
                break;
            default:
                cardEl.classList.add('border-warning');
        }
    }
}

// Função para criar um card de ação
function criarCardAcao(acao, dados) {
    const template = document.getElementById('acao-card-template');
    const clone = template.content.cloneNode(true);
    
    // Preencher dados básicos
    clone.querySelector('.card-title').textContent = acao;
    
    // Configurar modal
    const btnDetalhes = clone.querySelector('.btn-detalhes');
    btnDetalhes.setAttribute('data-acao', acao);
    btnDetalhes.addEventListener('click', async (event) => {
        event.preventDefault();
        const acaoSelecionada = event.target.getAttribute('data-acao');
        await abrirModalDetalhes(acaoSelecionada);
    });

    // Atualizar dados se disponíveis
    if (dados) {
        atualizarCardAcao(clone, dados);
    }
    
    return clone;
}

// Função para abrir modal de detalhes
async function abrirModalDetalhes(acao) {
    console.log('Abrindo modal para:', acao);
    const dados = await buscarDadosAcao(acao);
    if (!dados) {
        alert('Não foi possível carregar os dados da ação');
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('detalheModal'));
    document.getElementById('modalTitle').textContent = `Detalhes - ${acao}`;
    document.getElementById('modalPreco').textContent = formatarMoeda(dados.price);
    document.getElementById('modalRSI').textContent = dados.rsi;
    document.getElementById('modalADX').textContent = dados.adx;
    document.getElementById('modalRecomendacao').textContent = dados.recommendation;
    document.getElementById('modalUltimaAtualizacao').textContent = formatarData(dados.date);
    
    modal.show();
}

// Função principal para inicializar a aplicação
async function inicializarApp() {
    const container = document.querySelector('.acoes-container');
    
    // Carregar dados iniciais
    const dados = await buscarTodasAcoes();
    
    // Criar cards para cada ação
    dados.forEach(dadosAcao => {
        const card = criarCardAcao(dadosAcao.symbol, dadosAcao);
        container.appendChild(card);
        acoesCache.set(dadosAcao.symbol, dadosAcao);
    });
    
    // Configurar atualização automática
    setInterval(async () => {
        const novosDados = await buscarTodasAcoes();
        novosDados.forEach(dadosAcao => {
            const card = document.querySelector(`[data-acao="${dadosAcao.symbol}"]`).closest('.card-wrapper');
            atualizarCardAcao(card, dadosAcao);
            acoesCache.set(dadosAcao.symbol, dadosAcao);
        });
    }, UPDATE_INTERVAL);
    
    // Iniciar o contador regressivo
    setInterval(atualizarContador, 1000);
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', inicializarApp);
