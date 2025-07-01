import time
import pyautogui
import pygetwindow as gw

DELAY = 0.5  # tempo entre ações (em segundos)
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
        return False
    
    # Navega para a página de login:
    pyautogui.hotkey('ctrl', 'l')  # Foca na barra de endereço.
    time.sleep(0.25)
    pyautogui.write('http://localhost:5500/login.html')
    pyautogui.press('enter')
    time.sleep(DELAY * 3)  # Espera a página carregar.
    
    # Preenche o email:
    pyautogui.press('tab', presses=2)  # Navega até o campo e-mail.
    time.sleep(0.25)
    pyautogui.write(CREDENCIAIS['email'])
    time.sleep(0.25)
    
    # Preenche a senha:
    pyautogui.press('tab')  # Navega para o campo senha.
    time.sleep(0.25)
    pyautogui.write(CREDENCIAIS['senha'])
    time.sleep(0.25)
    
    # Submete o formulário:
    pyautogui.press('enter')
    time.sleep(DELAY * 3)  # Espera o login ser processado.
    print("Login realizado com sucesso!")
    return True

if __name__ == "__main__":
    fazer_login()