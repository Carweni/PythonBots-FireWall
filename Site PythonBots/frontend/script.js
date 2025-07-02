document.addEventListener('DOMContentLoaded', () => {
    userBehavior.formStartTime = Date.now();
    const path = window.location.pathname.split('/').pop() || 'index.html';
    
    if (path === 'index.html' || path === '') {
        inicializarPaginaPrincipal();
    } else if (path === 'cadastro.html') {
        document.getElementById('cadastro-form').addEventListener('submit', cadastrarUsuario);
    } else if (path === 'login.html') {
        document.getElementById('login-form').addEventListener('submit', logarUsuario);
    } else if (path === 'carrinho.html') {
        inicializarPaginaCarrinho();
    }
});

// --- FUNÇÕES DA PÁGINA PRINCIPAL ---
function inicializarPaginaPrincipal() {
    carregarProdutos();
    atualizarContadorCarrinho();
    atualizarStatusLogin();
}

function carregarProdutos() {
    const container = document.getElementById('product-list');
    container.innerHTML = '<p>Carregando produtos...</p>';

    fetch('http://localhost:5500/api/products')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar produtos');
            }
            return response.json();
        })
        .then(produtos => {
            container.innerHTML = '';
            produtos.forEach(produto => {
                container.innerHTML += `
                    <div class="product-card">
                        <img src="${produto.imagem_url}" alt="${produto.nome}">
                        <h3>${produto.nome}</h3>
                        <p>R$ ${produto.preco.toFixed(2)}</p>
                        <button onclick="adicionarAoCarrinho(${produto.id})">Adicionar ao Carrinho</button>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error('Erro:', error);
            container.innerHTML = `<p class="error">${error.message}</p>`;
        });
}

function atualizarStatusLogin() {
    const userStatusEl = document.getElementById('user-status');
    
    if (!userStatusEl) return;
    
    try {
        const usuarioLogado = JSON.parse(sessionStorage.getItem('usuarioLogado'));

        if (usuarioLogado) {
            userStatusEl.innerHTML = `
                <span>Olá, ${usuarioLogado.nome}!</span>
                <button id="logout-button" onclick="logout()">Sair</button>
            `;
        } else {
            userStatusEl.innerHTML = `
                <a href="login.html">Login</a>
                <a href="cadastro.html">Cadastro</a>
            `;
        }
    } catch (error) {
        console.error('Erro ao atualizar status de login:', error);
        userStatusEl.innerHTML = `
            <a href="login.html">Login</a>
            <a href="cadastro.html">Cadastro</a>
        `;
    }
}

function cadastrarUsuario(event) {
    event.preventDefault();
    
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    const messageEl = document.getElementById('message');

    // Coletar dados de comportamento do usuário
    const behaviorData = {
        formFillTime: (Date.now() - userBehavior.formStartTime) / 1000,
        mouseMovements: userBehavior.mouseMovements,
        keyStrokes: userBehavior.keyStrokes,
        fieldFocusTimes: userBehavior.focusTimes,
    };

    // Enviar para o backend Flask
    fetch('http://localhost:5500/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nome: nome,
            email: email,
            senha: senha,
            behavior: behaviorData
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        messageEl.style.color = 'green';
        messageEl.textContent = 'Cadastro realizado! Redirecionando para o login...';
        setTimeout(() => window.location.href = 'login.html', 2000);
    })
    .catch(error => {
        console.error('Erro:', error);
        messageEl.style.color = 'red';
        messageEl.textContent = error.error || 'Erro ao cadastrar usuário';
        
        // Se for um erro de bot detectado, pode adicionar tratamento especial
        if (error.error && error.error.includes('Comportamento suspeito')) {
            // Pode redirecionar ou mostrar mensagem específica
            messageEl.textContent += '. Por favor, preencha o formulário como um humano.';
        }
    });
}

function logarUsuario(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    const messageEl = document.getElementById('message');

    // Coletar dados de comportamento
    const behaviorData = {
        formFillTime: (Date.now() - userBehavior.formStartTime) / 10000,
        mouseMovements: userBehavior.mouseMovements,
        keyStrokes: userBehavior.keyStrokes,
        fieldFocusTimes: userBehavior.focusTimes
    };

    fetch('http://localhost:5500/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            senha: senha,
            behavior: behaviorData
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        // Armazena o usuário logado
        sessionStorage.setItem('usuarioLogado', JSON.stringify(data.user));
        
        messageEl.style.color = 'green';
        messageEl.textContent = 'Login bem-sucedido! Redirecionando...';
        setTimeout(() => window.location.href = 'index.html', 1000);
    })
    .catch(error => {
        console.error('Erro:', error);
        messageEl.style.color = 'red';
        messageEl.textContent = error.error || 'Erro ao fazer login';
    });
}

function logout() {
    sessionStorage.removeItem('usuarioLogado');
    window.location.href = 'index.html';
}

// --- FUNÇÕES DO CARRINHO MELHORADAS ---
function getCarrinho() {
    return JSON.parse(localStorage.getItem('carrinho')) || [];
}

function salvarCarrinho(carrinho) {
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    atualizarContadorCarrinho();
}

function adicionarAoCarrinho(produtoId) {
    // Verificar se há muitas adições rápidas
    const now = Date.now();
    const lastAdd = localStorage.getItem('lastAddToCart') || 0;
    
    if (now - lastAdd < 1000) {
        alert('Por favor, espere um momento antes de adicionar mais itens.');
        return;
    }
    
    localStorage.setItem('lastAddToCart', now);

    // Primeiro buscar os produtos da API
    fetch('http://localhost:5500/api/products')
        .then(response => response.json())
        .then(produtos => {
            const produto = produtos.find(p => p.id === produtoId);
            if (produto) {
                const carrinho = getCarrinho();
                
                // Verifica se o produto já existe no carrinho
                const itemExistente = carrinho.find(item => item.id === produtoId);
                
                if (itemExistente) {
                    itemExistente.quantidade += 1;
                } else {
                    carrinho.push({
                        ...produto,
                        quantidade: 1
                    });
                }
                
                salvarCarrinho(carrinho);
                
                // Atualizar a exibição do carrinho se estiver na página certa
                if (window.location.pathname.includes('carrinho.html')) {
                    inicializarPaginaCarrinho();
                }
                
                // Mostrar feedback visual
                mostrarNotificacao(`${produto.nome} adicionado ao carrinho!`);
            }
        })
        .catch(error => {
            console.error('Erro ao buscar produtos:', error);
        });
}

function alterarQuantidade(produtoId, delta) {
    const carrinho = getCarrinho();
    const item = carrinho.find(item => item.id === produtoId);
    
    if (item) {
        item.quantidade += delta;
        
        if (item.quantidade <= 0) {
            removerDoCarrinho(produtoId);
        } else {
            salvarCarrinho(carrinho);
            inicializarPaginaCarrinho();
        }
    }
}

function removerDoCarrinho(produtoId) {
    const carrinho = getCarrinho();
    const novoCarrinho = carrinho.filter(item => item.id !== produtoId);
    salvarCarrinho(novoCarrinho);
    inicializarPaginaCarrinho();
    mostrarNotificacao('Produto removido do carrinho');
}

function limparCarrinho() {
    if (confirm('Tem certeza que deseja limpar todo o carrinho?')) {
        localStorage.removeItem('carrinho');
        atualizarContadorCarrinho();
        inicializarPaginaCarrinho();
    }
}

function atualizarContadorCarrinho() {
    const contador = document.getElementById('cart-count');
    if (contador) {
        const carrinho = getCarrinho();
        const totalItens = carrinho.reduce((total, item) => total + item.quantidade, 0);
        contador.textContent = totalItens;
    }
}

function inicializarPaginaCarrinho() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    const carrinho = getCarrinho();
    let total = 0;

    if (carrinho.length === 0) {
        container.innerHTML = `
            <div class="carrinho-vazio">
                <p>Seu carrinho está vazio.</p>
                <a href="index.html" class="btn-continuar-comprando">Continuar Comprando</a>
            </div>
        `;
        totalEl.textContent = '0.00';
        return;
    }

    container.innerHTML = `
        <div class="carrinho-header">
            <button onclick="limparCarrinho()" class="btn-limpar-carrinho">Limpar Carrinho</button>
        </div>
    `;
    
    carrinho.forEach(item => {
        const subtotal = item.preco * item.quantidade;
        total += subtotal;
        
        container.innerHTML += `
            <div class="cart-item">
                <div class="item-info">
                    <img src="${item.imagem_url}" alt="${item.nome}" class="item-image">
                    <div class="item-details">
                        <h4>${item.nome}</h4>
                        <p class="item-price">R$ ${item.preco.toFixed(2)} cada</p>
                    </div>
                </div>
                <div class="item-controls">
                    <div class="quantity-controls">
                        <button onclick="alterarQuantidade(${item.id}, -1)" class="btn-quantity">-</button>
                        <span class="quantity">${item.quantidade}</span>
                        <button onclick="alterarQuantidade(${item.id}, 1)" class="btn-quantity">+</button>
                    </div>
                    <div class="item-subtotal">R$ ${subtotal.toFixed(2)}</div>
                    <button onclick="removerDoCarrinho(${item.id})" class="btn-remover">Remover</button>
                </div>
            </div>
        `;
    });

    totalEl.textContent = total.toFixed(2);
    
    // Adiciona evento ao botão de checkout
    const checkoutBtn = document.getElementById('checkout-button');
    if (checkoutBtn) {
        checkoutBtn.onclick = finalizarCompra;
    }
}

function finalizarCompra() {
    const messageEl = document.getElementById('checkout-message');
    const usuarioLogado = JSON.parse(sessionStorage.getItem('usuarioLogado'));

    if (!usuarioLogado) {
        messageEl.style.color = 'red';
        messageEl.textContent = 'Você precisa fazer login para finalizar a compra!';
        return;
    }

    const carrinho = getCarrinho();
    if (carrinho.length === 0) {
        messageEl.style.color = 'red';
        messageEl.textContent = 'Seu carrinho está vazio.';
        return;
    }

    // Coletar dados de comportamento
    const behaviorData = {
        formFillTime: (Date.now() - userBehavior.formStartTime) / 1000,
        mouseMovements: userBehavior.mouseMovements,
        keyStrokes: userBehavior.keyStrokes
    };

    const total = carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0);

    fetch('http://localhost:5500/api/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_email: usuarioLogado.email,
            items: carrinho,
            total: total,
            behavior: behaviorData
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        messageEl.style.color = 'green';
        messageEl.textContent = `Compra finalizada com sucesso, ${usuarioLogado.nome}! Nº do pedido: ${data.order_id}`;

        // Limpa o carrinho
        localStorage.removeItem('carrinho');
        atualizarContadorCarrinho();
        
        // Atualiza a exibição
        setTimeout(() => inicializarPaginaCarrinho(), 2000);
    })
    .catch(error => {
        console.error('Erro:', error);
        messageEl.style.color = 'red';
        messageEl.textContent = error.error || 'Erro ao finalizar compra';
    });
}

function mostrarNotificacao(mensagem) {
    // Cria elemento de notificação
    const notificacao = document.createElement('div');
    notificacao.className = 'notificacao';
    notificacao.textContent = mensagem;
    
    // Adiciona ao body
    document.body.appendChild(notificacao);
    
    // Remove após 3 segundos
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.parentNode.removeChild(notificacao);
        }
    }, 3000);
}

// Objeto para armazenar timestamps e eventos
const userBehavior = {
    formStartTime: Date.now(),
    focusTimes: {},
    mouseMovements: 0,
    lastMouseMove: null,
    keyStrokes: 0
};

document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', (e) => {
        userBehavior.focusTimes[e.target.id] = Date.now();
    });
});

document.addEventListener('mousemove', () => {
    userBehavior.mouseMovements++;
    userBehavior.lastMouseMove = Date.now();
});

document.addEventListener('keydown', () => {
    userBehavior.keyStrokes++;
});