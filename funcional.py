from PIL import Image
import pyautogui
import pytesseract


#Tirar print
screenshot = pyautogui.screenshot()

#Salvar imagem
screenshot.save("screenshot.png")

#Identificar texto a imagem
texto = pytesseract.image_to_string(screenshot, lang="por")  # Português


#Traduzir o texto da imagem


#Apresentar o texto e a imagem
print(texto)



# Exibir a imagem
screenshot.show()


