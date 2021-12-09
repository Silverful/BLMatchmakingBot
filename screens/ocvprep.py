import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io
import base64
import binascii


def erode(image):
    kernel = np.ones((2, 1), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


def dilate(image):
    kernel = np.ones((2, 2), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


def thresholding(image, low=70, high=90):
    return cv2.threshold(image, low, high, cv2.THRESH_BINARY_INV)[1]


def remove_noise(image):
    return cv2.medianBlur(image, 5)


def make_gray(image):
    temp = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    temp = cv2.cvtColor(temp, cv2.COLOR_GRAY2RGB)
    return temp


def isbright(image, dim=100, thresh=0.5):
    image = image[:, :image.shape[1] * 2 // 5]
    image = cv2.resize(image, (dim, dim))
    L, A, B = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    L = L/np.max(L)
    return np.mean(L)


def change_contrast(image):
    img = image

    # -----Converting image to LAB Color model-----------------------------------
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)

    # -----Splitting the LAB image to different channels-------------------------
    l, a, b = cv2.split(lab)

    # -----Applying CLAHE to L-channel-------------------------------------------
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    cl = clahe.apply(l)

    # -----Merge the CLAHE enhanced L-channel with the a and b channel-----------
    limg = cv2.merge((cl, a, b))

    # -----Converting image from LAB Color model to RGB model--------------------
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return final


def is_dead(image):
    gr = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    player_name = gr[:, :gr.shape[1] * 2 // 5]
    bright = cv2.minMaxLoc(player_name)[1]
    if bright > 160:
        return False
    else:
        return True


def contrast(img, contrast =1.7, brightness = 1.0):
    im = Image.fromarray(img)
    enchancer = ImageEnhance.Brightness(im)
    output = enchancer.enhance(brightness)
    enchancer = ImageEnhance.Contrast(output)
    output = enchancer.enhance(contrast)
    numpy_image = np.array(output)
    ocv_image = numpy_image
    return ocv_image


def old_find_box(img, indent=4, dig_h=60, step=1, bottom=False):

    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    upper_row = 0
    left_col = 0
    right_col = 0
    bottom_row = 0

    for y in range(indent, img.shape[0], step):
        for x in range(indent, img.shape[1], step):
            if img[y, x] == 0:
                upper_row = y
                break
        else:
            continue
        break

    if upper_row == 0:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    if bottom:
        for y in reversed(range(indent, img.shape[0], step)):
            for x in range(indent, img.shape[1], step):
                if img[y, x] == 0:
                    bottom_row = y
                    break
            else:
                continue
            break
        img = img[upper_row - indent: bottom_row + indent]
    else:
        img = img[upper_row - indent: upper_row + dig_h + indent]

    for x in range(indent, img.shape[1], step):
        for y in range(indent, img.shape[0], step):
            if img[y, x] == 0:
                left_col = x
                break
        else:
            continue
        break

    for x in reversed(range(indent, img.shape[1], step)):
        for y in range(indent, img.shape[0], step):
            if img[y, x] == 0:
                right_col = x
                break
        else:
            continue
        break

    img = img[:, left_col - indent: right_col + indent]
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img


def fullprep(img, scale=4, thresh=100):
    img = make_gray(img)
    if scale > 1:
        img = cv2.resize(img, [img.shape[1] * scale, img.shape[0] * scale])
    img = cv2.bilateralFilter(img, 4, 40, 60)
    img = contrast(img, contrast=3)
    img = thresholding(img, thresh, 255)
    #img = find_boxe(img, len=159)
    img = remove_noise(img)
    return img


def bytes_to_img(bytes_data):
    data = io.BytesIO(bytes_data)
    im = Image.open(data)
    numpy_image = np.array(im)

    return numpy_image

#ocvprep.fullprep(self.screen)
def gray_image3(x,resize,blur):
    img = x
    if resize == 1:
        img = cv2.resize(img, None, fx=2, fy=2)  # scale = 2
    if resize == 2:
        img = cv2.resize(img, None, fx=4, fy=4)  # scale = 4
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_filter = cv2.bilateralFilter(gray, 1, 1, 20)
    thresh = cv2.threshold(img_filter, 0, 256, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    final = cv2.bitwise_not(thresh)
    if blur == 1:
        final = cv2.GaussianBlur(final, (1, 1), 0)

    return final


def find_box(img, indent=5, diglen=60, bottom=False):
    img = np.array(img)

    #bottom = True if diglen == 0 else False

    upper_row = None
    left_col = None
    right_col = None
    bottom_row = None

    for index, row in enumerate(img):
        if 0 in row:
            upper_row = index
            break
    if upper_row < 0:
        return img
    if upper_row < indent:
        upper_row = indent

    if bottom:
        for index, row in enumerate(np.flip(img, axis=0)):
            if 0 in row:
                bottom_row = img.shape[0] - index
                break
        img = img[upper_row - indent: bottom_row + indent]

    else:
        img = img[upper_row - indent: upper_row + diglen + indent]

    img = img.transpose(1, 0, 2)

    for index, col in enumerate(img):
        if 0 in col:
            left_col = index
            break
    if left_col < indent:
        left_col = indent

    for index, col in enumerate(np.flip(img, axis=0)):
        if 0 in col:
            right_col = img.shape[0] - index
            break

    img = img[left_col - indent: right_col + indent]
    img = img.transpose(1, 0, 2)

    return img
