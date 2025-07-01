import random
import time
import pyautogui
import pygetwindow as gw

# Configurações
DELAY = 1  # tempo entre ações (em segundos)
CREDENCIAIS = {
    'email': 'a1@gmail.com',
    'senha': 'a'
}

def focar_navegador():
    """Foca na janela do navegador onde o site está aberto"""
    try:
        # Lista de navegadores comuns
        navegadores = ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave']
        
        for nav in navegadores:
            try:
                janela = gw.getWindowsWithTitle(nav)[0]
                if janela:
                    janela.activate()
                    time.sleep(DELAY)
                    return True
            except IndexError:
                continue
        
        print("Navegador não encontrado. Certifique-se de que o site está aberto em Chrome, Firefox, Edge, Opera ou Brave.")
        return False
    except Exception as e:
        print(f"Erro ao focar no navegador: {e}")
        return False

def fazer_login():
    """Realiza o login no site"""
    if not focar_navegador():
        return
    
    # Navega para a página de login
    pyautogui.hotkey('ctrl', 'l')  # Foca na barra de endereço
    time.sleep(0.5)
    pyautogui.write('http://localhost:5500/login.html')
    pyautogui.press('enter')
    time.sleep(DELAY * 3)  # Espera a página carregar
    
    # Preenche o email
    pyautogui.press('tab', presses=2)  # Navega até o campo email
    time.sleep(0.5)
    pyautogui.write(CREDENCIAIS['email'])
    time.sleep(0.5)
    
    # Preenche a senha
    pyautogui.press('tab')  # Navega para o campo senha
    time.sleep(0.5)
    pyautogui.write(CREDENCIAIS['senha'])
    time.sleep(0.5)
    
    # Submete o formulário
    pyautogui.press('enter')
    time.sleep(DELAY * 3)  # Espera o login ser processado
    print("Tentativa de login realizada.")

def adicionar_ao_carrinho(produto_ids, quantidade_aleatoria=True):
    """
    Adiciona produtos ao carrinho de forma aleatória
    """
    if not focar_navegador():
        return
    
    # Navega para a página principal
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    pyautogui.write('http://localhost:5500')
    pyautogui.press('enter')
    time.sleep(DELAY * 3)
    
    # Decide quantos produtos adicionar
    if quantidade_aleatoria:
        num_produtos = random.randint(1, len(produto_ids))
        produtos_selecionados = random.sample(produto_ids, num_produtos)
    else:
        produtos_selecionados = produto_ids
    
    print(f"Tentando adicionar {len(produtos_selecionados)} produtos ao carrinho...")
    
    # Posiciona no primeiro produto
    pyautogui.moveTo(500, 400)  # Ajuste estas coordenadas conforme necessário
    time.sleep(1)
    
    for produto_id in produtos_selecionados:
        try:
            # Clica no botão (ajuste o número de tabs conforme necessário)
            pyautogui.press('tab', presses=int(produto_id)*5)  # Aproximação
            time.sleep(0.5)
            pyautogui.press('space')
            time.sleep(DELAY)
            
            print(f"Produto ID {produto_id} - ação realizada")
            
        except Exception as e:
            print(f"Erro ao adicionar produto {produto_id}: {e}")
            continue

    print(f"Processo concluído! {len(produtos_selecionados)} produtos foram adicionados ao carrinho.")

if __name__ == "__main__":
    # Lista de IDs de produtos disponíveis
    TODOS_PRODUTOS_IDS = [
        '1', '2', '3', '4', 
        '5', '6', '7', '8'
    ]
    fazer_login()
    # Adiciona produtos aleatoriamente (para adicionar todos, usar quantidade_aleatoria=False)
    adicionar_ao_carrinho(TODOS_PRODUTOS_IDS, quantidade_aleatoria=True)