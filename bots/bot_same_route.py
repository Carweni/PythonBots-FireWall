import time
import requests

IP = "http://localhost:5500"
ROTA = "/api/login"  # ou /login.html
INTERVALO = 5  # segundos entre requisições
REPETICOES = 50

for i in range(REPETICOES):
    print(f"🔁 [{i+1}] Enviando requisição para {ROTA}...")
    try:
        response = requests.post(IP + ROTA, json={
            "email": "fake@bot.com",
            "senha": "errada",
            "behavior": {
                "formFillTime": 0.2,
                "mouseMovements": 0,
                "keyStrokes": 2
            }
        })
        print(f"🧾 Código de resposta: {response.status_code}")
    except Exception as e:
        print("Erro:", e)
    
    time.sleep(INTERVALO)
