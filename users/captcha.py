from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO
from django.conf import settings


class Captcha:

    @staticmethod
    def get_background_color():
        COLORS = [(255, 228, 196), (240, 255, 240), (255, 228, 225), (255, 246, 143), (255, 236, 139),\
            (205, 201, 201), (255, 218, 185)]
        color = random.choice(COLORS)
        return color

    @staticmethod
    def get_font_color():
        COLORS = [(0, 100, 0), (255, 106, 106), (178, 34, 34), (148, 0, 211), (255, 127, 0),\
            (67, 110, 238), (54, 54, 54), (255, 127, 36)]
        color = random.choice(COLORS)
        return color

    @staticmethod
    def get_random_char():
        CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
        char = random.choice(CHARS)
        return char

    def draw_text(self, draw):
        captcha_string = ''
        NUM_CHAR = 6
        FONT_SIZE = 22

        # FONT = os.path.join(settings.BASE_DIR, 'static/fonts/msyh.ttf')
        FONT = '/var/www/shared/fonts/msyh.ttf'
        font = ImageFont.truetype(FONT, size=FONT_SIZE)
        for i in range(NUM_CHAR):
            char = self.get_random_char()
            draw.text((5+16*i, 0), char , self.get_font_color(), font=font)
            captcha_string += char
        return captcha_string

    def draw_line(self, draw, width, height):
        x1=random.randint(10, width)
        x2=random.randint(10, width)
        y1=random.randint(0, height)
        y2=random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=self.get_font_color())

    def draw_point(self, draw, width, height):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=self.get_font_color())

    def draw_arc(self, draw, width, height):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=self.get_font_color())

    def soil_pic(self, draw, width, height):
        '''噪点噪线'''
        NUM_LINE = 5
        NUM_POINT = 25
        NUM_ARC = 15
        for i in range(NUM_LINE):
            self.draw_line(draw, width, height)
        for i in range(NUM_POINT):
            self.draw_point(draw, width, height)
        for i in range(NUM_ARC):
            self.draw_arc(draw, width, height)

    def draw_captcha(self):
        WIDTH = 100
        HEIGHT = 30
        image = Image.new('RGB', (WIDTH, HEIGHT), self.get_background_color())
        draw = ImageDraw.Draw(image)
        captcha_string = self.draw_text(draw)
        self.soil_pic(draw, WIDTH, HEIGHT)
        return image, captcha_string

    def get_img_data(self, image):
        buf = BytesIO()
        image.save(buf, 'png')
        img_data = buf.getvalue()
        buf.close()
        return img_data

    def get_captcha(self):
        image, captcha_string = self.draw_captcha()
        img_data = self.get_img_data(image)
        return img_data, captcha_string
