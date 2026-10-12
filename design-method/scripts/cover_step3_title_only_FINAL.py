from PIL import Image, ImageDraw, ImageFont, ImageFilter
im=Image.open('cover_base.png').convert('RGBA'); W,H=im.size
F=lambda s:ImageFont.truetype('almarai.ttf',s)
g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
for y in range(0,520): gd.line([(0,y),(W,y)],fill=(0,25,50,int(110*(1-y/520))))
im=Image.alpha_composite(im,g)
def txt(d,xy,t,f,fill): d.text(xy,t,font=f,fill=fill,anchor='mm',direction='rtl',language='ar')
cy=290
sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
txt(sd,(W//2,cy+8),"ساعة النداء الفورية",F(165),(0,20,40,230)); sh=sh.filter(ImageFilter.GaussianBlur(10))
im=Image.alpha_composite(im,sh); d=ImageDraw.Draw(im)
txt(d,(W//2,cy),"ساعة النداء الفورية",F(165),(255,255,255,255))
im.convert('RGB').save('cover.jpg',quality=93)
im.convert('RGB').resize((800,800),Image.LANCZOS).save('cover_prev2.jpg',quality=90)
