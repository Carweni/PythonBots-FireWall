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
        formFillTime: (Date.now() - userBehavior.formStartTime) / 1000,
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


// --- FUNÇÕES DO CARRINHO ---
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
                carrinho.push(produto);
                salvarCarrinho(carrinho);
                
                // Atualizar a exibição do carrinho se estiver na página certa
                if (window.location.pathname.includes('carrinho.html')) {
                    inicializarPaginaCarrinho();
                }
            }
        })
        .catch(error => {
            console.error('Erro ao buscar produtos:', error);
        });
}

function atualizarContadorCarrinho() {
    const contador = document.getElementById('cart-count');
    if (contador) {
        contador.textContent = getCarrinho().length;
    }
}

function inicializarPaginaCarrinho() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    const carrinho = getCarrinho();
    let total = 0;

    container.innerHTML = carrinho.length === 0 ? '<p>Seu carrinho está vazio.</p>' : '';
    
    carrinho.forEach(item => {
        container.innerHTML += `
            <div class="cart-item">
                <span>${item.nome}</span>
                <span>R$ ${item.preco.toFixed(2)}</span>
            </div>
        `;
        total += item.preco;
    });

    totalEl.textContent = total.toFixed(2);
    document.getElementById('checkout-button').addEventListener('click', finalizarCompra);
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

    fetch('http://localhost:5500/api/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_email: usuarioLogado.email,
            items: carrinho,
            total: carrinho.reduce((sum, item) => sum + item.preco, 0),
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