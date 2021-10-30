from PIL import Image, ImageDraw, ImageFont
import string, random 
from random import randint


class Captcha(object):
    """
    Generate captcha images and get their key for verification purposes.
    """
    
    def __init__(self, length):
        self.getit = lambda : (random.randrange(5, 85),random.randrange(5, 55))
        self.colors = ['black','red','blue','green',(64, 107, 76),(0, 87, 128),(0, 3, 82)]
        self.fill_color = [(64, 107, 76),(0, 87, 128),(0, 3, 82),(191, 0, 255),(72, 189, 0),(189, 107, 0),(189, 41, 0)]
        self.FONT_PATH = './fonts'
        self.CACHE_PATH = '../cache'
        self.length = length
        
    def random_string(self):
        s = string.ascii_uppercase + string.ascii_lowercase + string.digits
        random_string = ''.join(random.choices(s, k=self.length))
        return random_string
    
    def gen_captcha_img(self):
        ranint1 = str(randint(0,999999999999999))
        img = Image.new('RGB', (90, 60), color='white')
        draw = ImageDraw.Draw(img)
        captcha_str = self.random_string()
        text_colors = random.choice(self.colors)
        font_name = self.FONT_PATH + '/sansitaswashed.ttf'
        font = ImageFont.truetype(font_name, 18)
        draw.text((20,20), captcha_str, fill=text_colors, font=font)
        for i in range(5,random.randrange(6, 10)):
            draw.line((self.getit(), self.getit()), fill=random.choice(self.fill_color), width=random.randrange(1,3))
        for i in range(10,random.randrange(11, 20)):
            draw.point((self.getit(), self.getit(), self.getit(), self.getit(), self.getit(), self.getit(), self.getit(), self.getit(), self.getit(), self.getit()), fill=random.choice(self.colors))
        img = img.resize((310,207))
        img.save(self.CACHE_PATH + '/captcha_' + ranint1 +'.png')
        return {'captcha_key': captcha_str, 'captcha_img_path': self.CACHE_PATH + '/captcha_' + ranint1 +'.png'}