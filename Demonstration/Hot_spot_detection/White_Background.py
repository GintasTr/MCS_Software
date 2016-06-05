from SimpleCV import *


class White_background:

    def __init__(self):
        self.NAME = "White_background.jpg"

    def create_white_background(self, width, height):
        number = 255
        image_list = [number]*width
        image_list = [image_list]*height
        np_list = np.array(image_list,np.uint8)
        cv2.imwrite(self.NAME, np_list)

    def get_white_background(self, width, height):
        simplecv_image = Image(self.NAME)
        simplecv_image = simplecv_image.crop(x = 0, y = 0,  w = width, h = height)
        return simplecv_image


# If called by itself:
if __name__ == '__main__':
    c = White_background()
    img = c.get_white_background(100,200)
    print img.width
    print img.height

