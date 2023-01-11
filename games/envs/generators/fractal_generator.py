from games.envs.generators.map_generator import MapGenerator
from PIL import Image, ImageDraw, ImageFilter
import numpy as np


class FractorMapGenerator(MapGenerator):

    def __init__(self, rand: np.random, width: int, height: int, props: dict, p=0.55) -> None:
        super().__init__(rand, width, height, props, p)

    def generateMap(self) -> np.ndarray:
        img_size = (self.width + self.height) / 2
        size_ratio = 1
        freq_ratio = img_size * 5

        self.img = Image.new(mode='RGB', color=(127, 127, 127), size=(self.height, self.width))
        draw = ImageDraw.Draw(self.img, 'RGBA')

        for i in range(5):
            circle_size = size_ratio * (i + 1)
            total_circle = freq_ratio / ((i + 1) * 2)

            for _ in range(int(total_circle)):
                color = (0, 0, 0, 127) if self.rand.rand() > self.p else (255, 255, 255, 127)
                c = (self.rand.randint(self.height), self.rand.randint(self.width))

                x1 = c[0] - circle_size
                y1 = c[1] - circle_size
                x2 = c[0] + circle_size
                y2 = c[1] + circle_size

                draw.ellipse([x1, y1, x2, y2], fill=color)

            self.saveImg(i)

        self.img = self.img.filter(ImageFilter.BLUR)
        self.saveImg(5)

        self.img = self.__pixelate(0.5)
        self.saveImg(6)

        self.img = self.img.convert('L')
        self.saveImg(7)

        self.img = self.__thresholding()
        self.saveImg(8)
        
        X = np.array(self.img)
        
        X[X == 0] = 1
        X[X == 255] = 0
                
        return X

    def saveImg(self, i=0):
        self.img.save(f'temp/temp_{i}.png')

    def __pixelate(self, amount):
        img = self.img.copy()

        new_dims = [int(a * amount) for a in img.size]

        return img.resize(new_dims).resize(self.img.size, resample=4)

    def __thresholding(self):
        img = self.img.copy()

        for x in range(img.width):
            for y in range(img.height):
                val = img.getpixel((x, y))

                img.putpixel((x, y), 0 if val > 127 else 255)

        return img
