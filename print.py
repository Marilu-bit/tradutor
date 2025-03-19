from PIL import Image
import pyautogui
import pytesseract

# Captura a tela inteira
screenshot = pyautogui.screenshot()

# Salvar a imagem
screenshot.save("screenshot.png")

# Exibir a imagem
screenshot.show()