def show_wait_destroy(winname, img):
    imS = cv2.resize(img, (960, 540))
    cv2.imshow(winname, imS)
    cv2.moveWindow(winname, 500, 0)
    cv2.waitKey(0)
    cv2.destroyWindow(winname)