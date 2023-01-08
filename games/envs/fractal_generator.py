from PIL import Image, ImageDraw
import numpy as np


class FractorMapGenerator:

    def __init__(self, rand: np.random, width: int, height: int, p=.55) -> None:
        self.rand = rand

        self.width = width
        self.height = height
        self.p = p

    def generateMap(self) -> np.ndarray:
        img_size = (self.width + self.height) / 2
        size_ratio = 5
        freq_ratio = img_size * 20

        self.img = Image.new(mode='rgba', color=(127, 127, 127, 255), size=(self.width, self.height))

        # for i in range(5):
        #     circle_size = size_ratio * (i + 1)
        #     total_circle = freq_ratio / ((i + 1) * 2)

        #     for _ in range(int(total_circle)):
        #         color = [0, 0, 0, 255] if self.rand.rand() > self.p else [0, 255, 255, 255]

        #         center = (self.rand.randint(self.width), self.rand.randint(self.height))
        #         self.img = cv2.circle(self.img, center=center, radius=int(circle_size), color=color)

        #         break

        self.saveImg()

    def saveImg(self, i=0):
        self.img.save('temp.png')
