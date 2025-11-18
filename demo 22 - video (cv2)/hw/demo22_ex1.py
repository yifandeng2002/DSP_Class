import numpy as np 
import cv2

cap = cv2.VideoCapture(0)

#high-pass filter kernel
kernel = np.array([[0, -1, 0],
                   [-1, 4, -1],
                   [0, -1, 0]])
while True:
    ok, frame = cap.read()
    
    if not ok:
        break
    
    # apply high-pass filter
    edges = cv2.filter2D(frame, -1, kernel)
    
    cv2.imshow('Edge Detection', edges)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()