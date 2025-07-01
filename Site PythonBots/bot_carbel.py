import random
from typing import List
import pyautogui
import time
import pygetwindow as gw

# Configurações
DELAY = 1  # tempo entre ações (em segundos)
CREDENCIAIS = {
    'email': 'a1@gmail.com',
    'senha': 'a'
}

def focar_navegador(titulo: str = 'Carbel') -> None:
    """Foca na janela do navegador"""
    try:
        navegador = gw.getWindowsWithTitle(titulo)[0]
        navegador.activate()
        time.sleep(DELAY)
    except IndexError:
        print(f"Janela com título '{titulo}' não encontrada")
        exit()

def selecionar_elemento_por_id(element_id: str) -> None:
    """Usa o menu de inspeção para selecionar elemento pelo ID"""
    # Abre o inspetor (Ctrl+Shift+I)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    time.sleep(DELAY)
    # Navega para a aba Elements
    pyautogui.hotkey('ctrl', 'shift', 'c')
    time.sleep(DELAY)
    # Abre o seletor de elementos
    pyautogui.write(f'document.getElementById("{element_id}")')
    pyautogui.press('enter')
    time.sleep(DELAY)
    # Fecha o inspetor
    pyautogui.hotkey('ctrl', 'shift', 'i')

def fazer_login() -> None:
    """Realiza o login usando o botão por ID"""
    focar_navegador()
    
    # Clica no botão de login via inspetor
    selecionar_elemento_por_id('botao_login')
    time.sleep(DELAY)
    
    # Preenche o email
    pyautogui.write(CREDENCIAIS['email'])
    time.sleep(DELAY/2)
    pyautogui.press('tab')  # navega para o campo senha
    
    # Preenche a senha
    pyautogui.write(CREDENCIAIS['senha'])
    time.sleep(DELAY/2)
    pyautogui.press('enter')
    time.sleep(DELAY * 3)

def adicionar_ao_carrinho(produto_ids: List[str], quantidade_aleatoria: bool = True) -> None:
    """
    Adiciona produtos ao carrinho de forma aleatória
    
    Args:
        produto_ids: Lista de IDs dos produtos
        quantidade_aleatoria: Se True, seleciona um número aleatório de produtos
    """
    focar_navegador()
    
    # Decide quantos produtos adicionar (entre 1 e o total disponível)
    if quantidade_aleatoria:
        num_produtos = random.randint(1, len(produto_ids))
        produtos_selecionados = random.sample(produto_ids, num_produtos)
    else:
        produtos_selecionados = produto_ids
    
    print(f"Adicionando {len(produtos_selecionados)} produtos ao carrinho...")
    
    for produto_id in produtos_selecionados:
        try:
            # Seleciona o botão do produto
            selecionar_elemento_por_id(produto_id)
            
            # Simula um clique
            pyautogui.press('space')
            time.sleep(DELAY)
            
            # Rola a página para o próximo produto
            pyautogui.scroll(-300)
            time.sleep(DELAY/2)
            
            print(f"Produto ID {produto_id} adicionado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao adicionar produto {produto_id}: {e}")
            continue

    print(f"Processo concluído! {len(produtos_selecionados)} produtos foram adicionados ao carrinho.")

if __name__ == "__main__":
    # Lista completa de IDs de produtos disponíveis
    TODOS_PRODUTOS_IDS = [
        '1', '2', '3', '4', 
        '5', '6', '7', '8'
    ]
    
    fazer_login()
    
    # Adiciona produtos aleatoriamente (para adicionar todos, usar quantidade_aleatoria=False)
    adicionar_ao_carrinho(TODOS_PRODUTOS_IDS, quantidade_aleatoria=True)