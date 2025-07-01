from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import hashlib
import time
from collections import defaultdict, deque

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost", "http://127.0.0.1"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Configurações do sistema anti-bot
BOT_DETECTION_CONFIG = {
    'MAX_REQUESTS_PER_MINUTE': 50,
    'MAX_FAILED_LOGINS': 5,
    'BLOCK_DURATION_MINUTES': 15,
    'MIN_FORM_FILL_TIME': 1,  # segundos
    'MIN_MOUSE_MOVEMENTS': 3,
    'MIN_KEYSTROKES': 5
}

# Estruturas de dados em memória para tracking
request_tracker = defaultdict(lambda: deque(maxlen=100))
failed_attempts = defaultdict(int)
blocked_ips = {}
user_behavior_cache = {}

DATA_FILES = {
    'users': 'data/users.json',
    'products': 'data/products.json',
    'orders': 'data/orders.json',
    'access_logs': 'data/access_logs.json',
    'blocked_ips': 'data/blocked_ips.json',
    'bot_detections': 'data/bot_detections.json'
}

def ensure_data_directory():
    """Garante que o diretório data existe"""
    os.makedirs('data', exist_ok=True)

def load_json_file(filename):
    """Carrega dados de um arquivo JSON"""
    ensure_data_directory()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_json_file(filename, data):
    """Salva dados em um arquivo JSON"""
    ensure_data_directory()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def get_client_ip():
    """Obtém o IP real do cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def log_access(ip, endpoint, success=True, details=None):
    """Registra um acesso no log"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'ip': ip,
        'endpoint': endpoint,
        'success': success,
        'user_agent': request.headers.get('User-Agent', ''),
        'details': details or {}
    }
    
    logs = load_json_file(DATA_FILES['access_logs'])
    logs.append(log_entry)
    
    # Manter apenas os últimos 10000 logs
    if len(logs) > 10000:
        logs = logs[-10000:]
    
    save_json_file(DATA_FILES['access_logs'], logs)

def is_ip_blocked(ip):
    """Verifica se um IP está bloqueado"""
    blocked_data = load_json_file(DATA_FILES['blocked_ips'])
    
    for blocked_entry in blocked_data:
        if blocked_entry['ip'] == ip:
            block_time = datetime.fromisoformat(blocked_entry['blocked_until'])
            if datetime.now() < block_time:
                return True, blocked_entry['reason']
            else:
                # Remove IPs expirados
                blocked_data.remove(blocked_entry)
                save_json_file(DATA_FILES['blocked_ips'], blocked_data)
    
    return False, None

def block_ip(ip, reason, duration_minutes=None):
    """Bloqueia um IP por um período"""
    if duration_minutes is None:
        duration_minutes = BOT_DETECTION_CONFIG['BLOCK_DURATION_MINUTES']
    
    blocked_until = datetime.now() + timedelta(minutes=duration_minutes)
    
    blocked_data = load_json_file(DATA_FILES['blocked_ips'])
    
    # Remove entrada anterior se existir
    blocked_data = [b for b in blocked_data if b['ip'] != ip]
    
    blocked_data.append({
        'ip': ip,
        'reason': reason,
        'blocked_at': datetime.now().isoformat(),
        'blocked_until': blocked_until.isoformat()
    })
    
    save_json_file(DATA_FILES['blocked_ips'], blocked_data)
    
    # Log da detecção de bot
    bot_detections = load_json_file(DATA_FILES['bot_detections'])
    bot_detections.append({
        'timestamp': datetime.now().isoformat(),
        'ip': ip,
        'reason': reason,
        'blocked_duration_minutes': duration_minutes
    })
    save_json_file(DATA_FILES['bot_detections'], bot_detections)

def analyze_request_pattern(ip):
    """Analisa padrões de requisição para detectar bots"""
    now = time.time()
    
    # Adiciona timestamp atual
    request_tracker[ip].append(now)
    
    # Verifica requisições por minuto
    recent_requests = [t for t in request_tracker[ip] if now - t < 60]
    
    if len(recent_requests) > BOT_DETECTION_CONFIG['MAX_REQUESTS_PER_MINUTE']:
        return True, f"Muitas requisições por minuto: {len(recent_requests)}"
    
    # Verifica padrões regulares (intervalos muito consistentes)
    if len(recent_requests) >= 10:
        intervals = []
        for i in range(1, len(recent_requests)):
            intervals.append(recent_requests[i] - recent_requests[i-1])
        
        # Se mais de 80% dos intervalos são muito similares (±0.5s), é suspeito
        if len(intervals) > 5:
            avg_interval = sum(intervals) / len(intervals)
            similar_intervals = sum(1 for i in intervals if abs(i - avg_interval) < 0.5)
            if similar_intervals / len(intervals) > 0.8 and avg_interval < 10:
                return True, f"Padrão de acesso muito regular: {avg_interval:.2f}s"
    
    return False, None

def analyze_form_behavior(behavior_data):
    """Analisa comportamento de preenchimento de formulário"""
    reasons = []
    
    # Verifica tempo de preenchimento
    if 'formFillTime' in behavior_data:
        fill_time = behavior_data['formFillTime']
        if fill_time < BOT_DETECTION_CONFIG['MIN_FORM_FILL_TIME']:
            reasons.append(f"Preenchimento muito rápido: {fill_time}s")
    
    # Verifica movimentos do mouse
    if 'mouseMovements' in behavior_data:
        if behavior_data['mouseMovements'] < BOT_DETECTION_CONFIG['MIN_MOUSE_MOVEMENTS']:
            reasons.append(f"Poucos movimentos do mouse: {behavior_data['mouseMovements']}")
    
    # Verifica teclas pressionadas vs movimentos do mouse
    if 'keyStrokes' in behavior_data and 'mouseMovements' in behavior_data:
        key_mouse_ratio = behavior_data['keyStrokes'] / max(behavior_data['mouseMovements'], 1)
        if key_mouse_ratio > 20:  # Muitas teclas, pouco mouse
            reasons.append(f"Proporção suspeita teclas/mouse: {key_mouse_ratio:.2f}")
    
    # Verifica sequência de tabs muito regular
    if 'fieldFocusTimes' in behavior_data:
        focus_times = list(behavior_data['fieldFocusTimes'].values())
        if len(focus_times) > 2:
            intervals = [focus_times[i] - focus_times[i-1] for i in range(1, len(focus_times))]
            if intervals and all(abs(i - intervals[0]) < 100 for i in intervals):  # Intervalos muito similares
                reasons.append("Sequência de foco muito regular")
    
    return reasons

@app.before_request
def before_request():
    """Middleware executado antes de cada requisição"""
    ip = get_client_ip()
    
    # Verifica se IP está bloqueado
    is_blocked, reason = is_ip_blocked(ip)
    if is_blocked:
        log_access(ip, request.endpoint, False, {'blocked_reason': reason})
        return jsonify({
            'error': 'Acesso bloqueado',
            'reason': 'Atividade suspeita detectada',
            'message': 'Tente novamente mais tarde'
        }), 403
    
    # Analisa padrões de requisição
    is_bot, bot_reason = analyze_request_pattern(ip)
    if is_bot:
        block_ip(ip, f"Padrão de bot detectado: {bot_reason}")
        log_access(ip, request.endpoint, False, {'bot_detection': bot_reason})
        return jsonify({
            'error': 'Acesso bloqueado',
            'reason': 'Comportamento automatizado detectado',
            'message': 'Tente novamente mais tarde'
        }), 403

@app.route('/')
def serve_index():
    """Serve a página principal"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos"""
    return send_from_directory('../frontend', filename)

@app.route('/api/products', methods=['GET'])
def get_products():
    ip = get_client_ip()
    log_access(ip, 'get_products', True)
    
    try:
        products = load_json_file(DATA_FILES['products'])
        if not products:
            raise FileNotFoundError
        return jsonify(products)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver inválido, retorna os produtos padrão
        default_products = [
            {"id": 1, "nome": "Notebook Gamer", "preco": 4599.90, "imagem_url": "https://via.placeholder.com/150/0000FF/FFFFFF?text=Notebook"},
            {"id": 2, "nome": "Mouse Sem Fio", "preco": 129.99, "imagem_url": "https://via.placeholder.com/150/FF0000/FFFFFF?text=Mouse"},
            {"id": 3, "nome": "Teclado Mecânico", "preco": 349.50, "imagem_url": "https://via.placeholder.com/150/008000/FFFFFF?text=Teclado"},
            {"id": 4, "nome": "Monitor 4K", "preco": 1899.00, "imagem_url": "https://via.placeholder.com/150/FFFF00/000000?text=Monitor"}
        ]
        save_json_file(DATA_FILES['products'], default_products)
        return jsonify(default_products)
    
@app.route('/api/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    ip = get_client_ip()
    data = request.json
    
    # Analisa comportamento para detectar bots
    behavior_data = data.get('behavior', {})
    bot_reasons = analyze_form_behavior(behavior_data)
    
    if bot_reasons:
        reason = f"Bot detectado no cadastro: {', '.join(bot_reasons)}"
        block_ip(ip, reason)
        log_access(ip, 'register', False, {'bot_reasons': bot_reasons})
        return jsonify({'error': 'Comportamento suspeito detectado'}), 403
    
    # Validações básicas
    required_fields = ['nome', 'email', 'senha']
    if not all(field in data for field in required_fields):
        log_access(ip, 'register', False, {'error': 'Campos obrigatórios faltando'})
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    
    users = load_json_file(DATA_FILES['users'])
    
    # Verifica se email já existe
    if any(user['email'] == data['email'] for user in users):
        log_access(ip, 'register', False, {'error': 'Email já existe'})
        return jsonify({'error': 'Este email já foi cadastrado'}), 400
    
    # Adiciona novo usuário
    new_user = {
        'id': len(users) + 1,
        'nome': data['nome'],
        'email': data['email'],
        'senha': hashlib.sha256(data['senha'].encode()).hexdigest(),  # Hash da senha
        'created_at': datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_json_file(DATA_FILES['users'], users)
    
    log_access(ip, 'register', True, {'user_email': data['email']})
    return jsonify({'message': 'Usuário cadastrado com sucesso'})

@app.route('/api/login', methods=['POST'])
def login():
    """Autentica um usuário"""
    ip = get_client_ip()
    data = request.json
    
    # Analisa comportamento para detectar bots
    behavior_data = data.get('behavior', {})
    bot_reasons = analyze_form_behavior(behavior_data)
    
    if bot_reasons:
        reason = f"Bot detectado no login: {', '.join(bot_reasons)}"
        block_ip(ip, reason)
        log_access(ip, 'login', False, {'bot_reasons': bot_reasons})
        return jsonify({'error': 'Comportamento suspeito detectado'}), 403
    
    users = load_json_file(DATA_FILES['users'])
    senha_hash = hashlib.sha256(data['senha'].encode()).hexdigest()
    
    user = next((u for u in users if u['email'] == data['email'] and u['senha'] == senha_hash), None)
    
    if user:
        # Reset contador de tentativas falhas
        failed_attempts[ip] = 0
        
        log_access(ip, 'login', True, {'user_email': data['email']})
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': {'nome': user['nome'], 'email': user['email']}
        })
    else:
        # Incrementa tentativas falhadas
        failed_attempts[ip] += 1
        
        if failed_attempts[ip] >= BOT_DETECTION_CONFIG['MAX_FAILED_LOGINS']:
            block_ip(ip, f"Muitas tentativas de login falhadas: {failed_attempts[ip]}")
        
        log_access(ip, 'login', False, {'failed_attempts': failed_attempts[ip]})
        return jsonify({'error': 'Email ou senha inválidos'}), 401

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Processa uma compra"""
    ip = get_client_ip()
    data = request.json
    
    # Analisa comportamento para detectar bots
    behavior_data = data.get('behavior', {})
    bot_reasons = analyze_form_behavior(behavior_data)
    
    if bot_reasons:
        reason = f"Bot detectado no checkout: {', '.join(bot_reasons)}"
        block_ip(ip, reason)
        log_access(ip, 'checkout', False, {'bot_reasons': bot_reasons})
        return jsonify({'error': 'Comportamento suspeito detectado'}), 403
    
    # Processa pedido
    orders = load_json_file(DATA_FILES['orders'])
    
    new_order = {
        'id': len(orders) + 1,
        'user_email': data.get('user_email'),
        'items': data.get('items', []),
        'total': data.get('total', 0),
        'created_at': datetime.now().isoformat(),
        'ip': ip
    }
    
    orders.append(new_order)
    save_json_file(DATA_FILES['orders'], orders)
    
    log_access(ip, 'checkout', True, {'order_id': new_order['id'], 'total': new_order['total']})
    return jsonify({'message': 'Compra finalizada com sucesso', 'order_id': new_order['id']})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Retorna estatísticas do sistema (endpoint admin)"""
    ip = get_client_ip()
    
    # Carrega dados
    logs = load_json_file(DATA_FILES['access_logs'])
    blocked_ips = load_json_file(DATA_FILES['blocked_ips'])
    bot_detections = load_json_file(DATA_FILES['bot_detections'])
    
    # Estatísticas básicas
    stats = {
        'total_requests': len(logs),
        'blocked_ips_count': len([b for b in blocked_ips if datetime.fromisoformat(b['blocked_until']) > datetime.now()]),
        'bot_detections_count': len(bot_detections),
        'recent_activity': logs[-20:] if logs else [],
        'top_blocked_reasons': {}
    }
    
    # Contagem de razões de bloqueio
    for detection in bot_detections:
        reason = detection['reason']
        stats['top_blocked_reasons'][reason] = stats['top_blocked_reasons'].get(reason, 0) + 1
    
    log_access(ip, 'admin_stats', True)
    return jsonify(stats)

if __name__ == '__main__':
    ensure_data_directory()
    print("Logs serão salvos em arquivos JSON na pasta 'data/'")
    print("Firewall anti-bot ativo com as seguintes proteções:")
    print(f"   • Máximo {BOT_DETECTION_CONFIG['MAX_REQUESTS_PER_MINUTE']} requisições/minuto")
    print(f"   • Máximo {BOT_DETECTION_CONFIG['MAX_FAILED_LOGINS']} tentativas de login")
    print(f"   • Tempo mínimo de preenchimento: {BOT_DETECTION_CONFIG['MIN_FORM_FILL_TIME']}s")
    print(f"   • Bloqueio por {BOT_DETECTION_CONFIG['BLOCK_DURATION_MINUTES']} minutos")
    app.run(debug=True, host='0.0.0.0', port=5500)