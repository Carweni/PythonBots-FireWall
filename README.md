# PythonBots-FireWall

# Objetivo do Sistema:

Criar um sistema que detecta e bloqueia acessos maliciosos automatizados (bots/macros) com base em padrões de tráfego e ações automatizadas, considerando uma página de login e formulário de compra.  O sistema utiliza técnicas de análise de comportamento para diferenciar usuários humanos de bots.

# Funcionalidades

- Detecção de Bots: Analisa padrões de requisição e comportamento para identificar atividades automatizadas.

- Bloqueio de IPs: Bloqueia temporariamente IPs que exibem comportamento suspeito.

- Proteção de Formulários: Verifica tempo de preenchimento, movimentos do mouse e teclas pressionadas para detectar bots.

- Logs e Estatísticas: Registra todas as tentativas de acesso e fornece estatísticas para análise.

## Configurações de Segurança

O sistema utiliza as seguintes configurações padrão para detecção de bots:

- Máximo de requisições por minuto: 35
- Máximo de tentativas de login falhadas: 5
- Duração do bloqueio: 15 minutos
- Tempo mínimo de preenchimento de formulário: 0.5 segundos
- Mínimo de movimentos do mouse: 2
- Mínimo de teclas pressionadas: 5

# Como rodar o site

Este projeto utiliza **Flask** como backend.

## Passos para executar

1. Abra o terminal.
2. Navegue até a pasta onde está localizado o arquivo `app.py`.
3. Execute o comando abaixo:

```bash
python app.py
```

## Acesse o site no navegador pelo endereço:

http://localhost:5500

## Dependências

Certifique-se de que a biblioteca python Flask esteja instalada em sua máquina. Caso não esteja, é possível obtê-la por meio do comando:

```bash
pip install flask
```

# Bots

O projeto inclui três tipos de bots para testar o sistema de detecção:

- Bot de Login: Simula um login automatizado.
- Bot de Rota: Envia múltiplas requisições para uma mesma rota.
- Bot de Compra: Simula uma compra automatizada.

# Como rodar os bots

1. Abra o terminal.
2. Navegue até a pasta `bots`.
3. Escolha qual bot quer utilizar.

## Para rodar o Bot de Login

- Execute o comando abaixo:

```bash
python bot_login.py
```

## Para rodar o Bot de Rota

- Execute o comando abaixo:

```bash
python bot_same_route.py
```

## Para rodar o Bot de Compra

- Execute o comando abaixo:
```bash
python bot_shop.py
```

## Dependências

Certifique-se de que as bibliotecas python Selenium (para automação de navegador), Requests (para envio de requisições HTTP) e PyAutoGUI (para simulação de interações com interface gráfica) estejam instaladas em sua máquina. Caso não estejam, é possível obtê-las por meio do comando:

```bash
pip install selenium requests pyautogui pygetwindow
```
