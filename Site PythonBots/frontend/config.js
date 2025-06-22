// Configurações da aplicação
const CONFIG = {
    API_BASE: 'http://localhost:5500/api',
    STORAGE_KEYS: {
        USER: 'carbel_user',
        CART: 'carbel_cart'
    },
    SERVER_CHECK_INTERVAL: 30000, // 30 segundos
    MESSAGE_TIMEOUT: 5000 // 5 segundos
};

// Variáveis globais
let currentUser = null;
let cart = [];
let products = [];