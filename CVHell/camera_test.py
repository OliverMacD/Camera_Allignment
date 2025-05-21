import cv2

cam1 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cam2 = cv2.VideoCapture(2, cv2.CAP_DSHOW) 
cam3 = cv2.VideoCapture(3, cv2.CAP_DSHOW)
cam4 = cv2.VideoCapture(4, cv2.CAP_DSHOW)

# Display a photo from each camera
while True:
    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()
    ret3, frame3 = cam3.read()
    ret4, frame4 = cam4.read()

    if not ret1 or not ret2 or not ret3 or not ret4:
        print("Error: Could not read from one of the cameras.")
        break

    cv2.imshow('Camera 1', frame1)
    cv2.imshow('Camera 2', frame2)
    cv2.imshow('Camera 3', frame3)
    cv2.imshow('Camera 4', frame4)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break