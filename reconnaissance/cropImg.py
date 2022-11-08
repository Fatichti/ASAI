import cv2


PATH_DATA_FOLDER = "/home/fabienpi/Documents/UV_ASAI/data/"
MAIN_IMG_NAME = "mainCrop.png"
SUB_IMG_NAME = "templatev2.png"


ref_point = []
crop = False
firstTouchMouse = True
eventLbtnDown = False





def shape_selection(event, x, y, flags, param):
    global ref_point, crop, firstTouchMouse, eventLbtnDown

    if event == cv2.EVENT_LBUTTONDOWN:
        print("Btn down")
        ref_point = [(x, y)]
        eventLbtnDown = True
        

    elif event == cv2.EVENT_LBUTTONUP:
        print("Btn up")
        eventLbtnDown = False
        cv2.rectangle(image, ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("image", image)

    elif event == cv2.EVENT_MOUSEMOVE:
        cloneRect = image.copy()
        if eventLbtnDown:
            print("Mouse moove")
            print("(x,y) = ", (x,y))
            if firstTouchMouse:
                ref_point.append((x, y))
                firstTouchMouse = False
            else:
                ref_point[1] = (x, y)
            cv2.rectangle(cloneRect, ref_point[0], ref_point[1], (0, 255, 0), 2)
            cv2.imshow("image", cloneRect)



def create_crop():
    image = cv2.imread(PATH_DATA_FOLDER + MAIN_IMG_NAME)
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", shape_selection)

    while True:
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("r"):
            image = clone.copy()
        elif key == ord("c"):
            break

    return ref_point, clone


def save_crop(ref_point, clone):
    if len(ref_point) == 2:
        crop_img = clone[ref_point[0][1]:ref_point[1][1], ref_point[0][0]:ref_point[1][0]]
        cv2.imshow("crop_img", crop_img)
        cv2.waitKey(0)
        cv2.imwrite(PATH_DATA_FOLDER + SUB_IMG_NAME)
    else:
        print("Error : Image bad cropped, please try again")
    cv2.destroyAllWindows()


coordImg, previousImgTemplate = create_crop()
save_crop(coordImg, previousImgTemplate)