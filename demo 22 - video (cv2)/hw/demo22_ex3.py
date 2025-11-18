import cv2
import numpy as np

img = cv2.imread('hw/image.jpg')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# green hue 35-85
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])

#mask
mask = cv2.inRange(hsv, lower_green, upper_green)
result = cv2.bitwise_and(img, img, mask=mask)

cv2.imwrite('hw/masked.jpg', mask)
cv2.imwrite('hw/detected.jpg', result)
print("Images: masked.jpg, detected.jpg")