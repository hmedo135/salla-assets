from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
base=Image.open('cover_base.png').convert('RGB')   # 1600x1600
W,H=1600,600
F=lambda s:ImageFont.truetype('almarai.ttf',s)
# background: vertical blue gradient sampled from base top
top=np.array(base.getpixel((60,60)),float); mid=np.array(base.getpixel((60,700)),float)
bg=np.zeros((H,W,3),np.float32)
for y in range(H):
    t=y/H; bg[y,:]=top*(1-t)+mid*t
# slight horizontal glow
yy,xx=np.mgrid[0:H,0:W]
glow=np.exp(-(((xx-420)/520)**2+((yy-330)/260)**2))[...,None]
bg=np.clip(bg+glow*np.array([10,40,60]),0,255)
canvas=Image.fromarray(bg.astype(np.uint8))
# product crop (remote+watch+podium), scaled to banner height
crop=base.crop((110,380,1500,1470))
sc=640/crop.width
crop=crop.resize((int(crop.width*sc),int(crop.height*sc)),Image.LANCZOS)
m=Image.new('L',crop.size,0); d=ImageDraw.Draw(m)
d.rectangle([40,40,crop.width-40,crop.height-40],fill=255)
m=m.filter(ImageFilter.GaussianBlur(38))
canvas.paste(crop,(10,(H-crop.height)//2+20),m)
d=ImageDraw.Draw(canvas)
def t(xy,s,f,fill,anchor='rm'): d.text(xy,s,font=f,fill=fill,anchor=anchor,direction='rtl',language='ar')
t((W-70,190),"ساعة النداء الفورية",F(100),(255,255,255))
t((W-70,295),"اضغط الريموت .. وتوصل الإشارة لساعة الشخص فورًا",F(38),(190,230,245))
t((W-70,350),"بدون شريحة ولا إنترنت ولا اشتراكات",F(34),(190,230,245))
# button
bw,bh=320,84; bx=W-70-bw; by=420
d.rounded_rectangle([bx,by,bx+bw,by+bh],radius=42,fill=(200,30,45))
t((bx+bw//2,by+bh//2-2),"اطلبها الآن",F(44),(255,255,255),'mm')
canvas.save('banner.jpg',quality=92)
canvas.resize((1000,375),Image.LANCZOS).save('banner_prev.jpg',quality=88)
