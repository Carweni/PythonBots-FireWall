from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
import random
import json

# Configurações:
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Edge(service=Service(), options=options)

# Simula um comportamento mais humano, para ver se a firewall detecta:
def simular_comportamento():
    formFillTime = round(random.uniform(2.5, 5.0), 2)
    mouseMovements = random.randint(4, 10)
    keyStrokes = random.randint(6, 12)

    print(f"Simulando comportamento:")
    print(f"  • formFillTime: {formFillTime}s")
    print(f"  • mouseMovements: {mouseMovements}")
    print(f"  • keyStrokes: {keyStrokes}")

    return {
        "formFillTime": formFillTime,
        "mouseMovements": mouseMovements,
        "keyStrokes": keyStrokes
    }

try:
    # Acessa a página principal (onde ficam os produtos):
    driver.get("http://localhost:5500/index.html")
    time.sleep(3)

    # Adiciona o(s) produto(s) ao carrinho:
    botoes_adicionar = driver.find_elements(By.XPATH, "//button[contains(text(), 'Adicionar ao Carrinho')]")

    if not botoes_adicionar:
        raise Exception("Nenhum botão de 'Adicionar ao Carrinho' encontrado.")

    print(f"Encontrados {len(botoes_adicionar)} produtos. Adicionando o(s) primeiro(s)...")
    
    # Adiciona alguns produtos:
    for i in range(random.randint(2, len(botoes_adicionar)-4)):
        botoes_adicionar[i].click()
        time.sleep(1.5)

    # Vai para a página do carrinho:
    driver.get("http://localhost:5500/carrinho.html")
    time.sleep(2)

    # Injeta usuário logado diretamente no sessionStorage:
    usuario_fake = {
        "nome": "Usuário Teste",
        "email": "teste@teste.com"
    }
    script_usuario = f'sessionStorage.setItem("usuarioLogado", \'{json.dumps(usuario_fake)}\');'
    driver.execute_script(script_usuario)
    time.sleep(1)

    comportamento = simular_comportamento()
    script_comportamento = f'''
        window.userBehavior = {{
            formStartTime: Date.now() - {int(comportamento['formFillTime'] * 1000)},
            mouseMovements: {comportamento['mouseMovements']},
            keyStrokes: {comportamento['keyStrokes']}
        }};
    '''
    driver.execute_script(script_comportamento)
    time.sleep(1)

    # Clica no botão "Finalizar Compra":
    finalizar_btn = driver.find_element(By.ID, "checkout-button")
    finalizar_btn.click()
    print("Compra finalizada (botão clicado).")

    # Aguarda para visualizar resposta:
    time.sleep(5)

except Exception as e:
    print("Erro durante a automação:", e)

finally:
    driver.quit()
