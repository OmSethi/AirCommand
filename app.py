import cv2

videoCapture = cv2.VideoCapture(0)

if not videoCapture.isOpened():
    print("Camera could not open")
    exit()

while True:
    # reading a frame from the camera
    ret, frame = videoCapture.read()

    if not ret: 
        print("Error: Could not read frame")
        break

    frame = cv2.flip(frame, 1)  # horizontal flip
    cv2.imshow("Live Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

videoCapture.release()
cv2.destroyAllWindows()
