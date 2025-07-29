import numpy as nb
import cv2

img = cv2.imread("tradutor/manga.jpg")

cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

borda = cv2.Laplacian(cinza,cv2.CV_8U)

_, binario = cv2.threshold(borda, 100, 255, cv2.THRESH_BINARY_INV)

#cv2.imshow("sem nada", img)
#cv2.imshow("cinza", cinza)
cv2.imshow("bordabin", borda)
cv2.imshow("preto e branco", binario)


cv2.waitKey(0)