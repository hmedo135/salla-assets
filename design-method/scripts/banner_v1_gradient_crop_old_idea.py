from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
base=Image.open('cover_base.png').convert('RGB')
F=lambda s:ImageFont.truetype('almarai.ttf',s)
top=np.array(base.getpixel((60,60)),float); mid=np.array(base.getpixel((60,700)),float)
def make(W,H,prod_w,prod_y,texts,out):
    bg=np.zeros((H,W,3),np.float32)
    for y in range(H): bg[y,:]=top*(1-y/H)+mid*(y/H)
    yy,xx=np.mgrid[0:H,0:W]
    bg=np.clip(bg+np.exp(-(((xx-prod_w*.5)/(prod_w*.9))**2+((yy-H*.55)/(H*.7))**2))[...,None]*np.array([10,40,60]),0,255)
    c=Image.fromarray(bg.astype(np.uint8))
    crop=base.crop((110,380,1500,1470)); sc=prod_w/crop.width
    crop=crop.resize((int(crop.width*sc),int(crop.height*sc)),Image.LANCZOS)
    m=Image.new('L',crop.size,0); ins=int(prod_w*0.07); ImageDraw.Draw(m).rectangle([-60,ins,crop.width-ins,crop.height-ins],fill=255)
    m=m.filter(ImageFilter.GaussianBlur(int(prod_w*0.06)))
    c.paste(crop,(0,prod_y),m)
    d=ImageDraw.Draw(c)
    for (x,y,s,size,col) in texts:
        d.text((x,y),s,font=F(size),fill=col,anchor='rm',direction='rtl',language='ar')
    c.save(out+'.png'); return c
white=(255,255,255); ice=(190,230,245)
# desktop 728x90 @2x
make(1456,180,230,0,[(1420,68,"ساعة النداء الفورية",70,white),(1420,132,"اضغط الريموت ويصل التنبيه فورًا .. بدون شريحة أو إنترنت",34,ice)],'bn_desktop')
# mobile 390x195 @2x
make(780,390,330,(390-259)//2+20,[(750,120,"ساعة النداء",64,white),(750,190,"الفورية",64,white),(750,265,"اضغط الريموت ويصل التنبيه",27,ice),(750,300,"فورًا .. بدون شريحة أو إنترنت",27,ice)],'bn_mobile')
# combined preview
a=Image.open('bn_desktop.png');b=Image.open('bn_mobile.png')
P=Image.new('RGB',(1456,180+20+390),(245,245,245));P.paste(a,(0,0));P.paste(b,(0,200))
P.save('bn_prev.jpg',quality=90)
