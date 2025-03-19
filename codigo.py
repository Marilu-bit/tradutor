from PIL import Image

#Tesseract
import pytesseract
img = Image.open("teste.png")
texto = pytesseract.image_to_string(img, lang="por")  # Português
print(texto)

#Pillow

#img = Image.open("teste.png")
#Exibir
#img.show()

#Redimencionar
img_resized = img.resize((300, 300))
img_resized.show()



#Tesseract OCR, OCR.space e Pillow