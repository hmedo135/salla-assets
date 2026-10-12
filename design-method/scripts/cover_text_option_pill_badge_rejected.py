from PIL import Image, ImageDraw, ImageFont, ImageFilter
im=Image.open('cover_base.png').convert('RGBA'); W,H=im.size
F=lambda s:ImageFont.truetype('almarai.ttf',s)
def txt(d,xy,t,f,fill,anchor='mm'):
    d.text(xy,t,font=f,fill=fill,anchor=anchor,direction='rtl',language='ar',features=['-liga'] if False else None)
# darken top slightly for legibility
g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
for y in range(0,520):
    gd.line([(0,y),(W,y)],fill=(0,25,50,int(110*(1-y/520))))
im=Image.alpha_composite(im,g)
# top pill: store wordmark
pill=Image.new('RGBA',(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pill)
pw,ph=560,96; x0=(W-pw)//2; y0=50
pd.rounded_rectangle([x0,y0,x0+pw,y0+ph],radius=48,fill=(255,255,255,235))
pd.rounded_rectangle([x0,y0,x0+pw,y0+ph],radius=48,outline=(0,77,115,255),width=4)
im=Image.alpha_composite(im,pill); d=ImageDraw.Draw(im)
txt(d,(W//2+110,y0+ph//2-2),"ناس كارت",F(54),(0,77,115,255))
d.text((W//2-120,y0+ph//2),"NC",font=F(60),fill=(0,77,115,255),anchor='mm')
d.line([(W//2-20,y0+22),(W//2-20,y0+ph-22)],fill=(0,77,115,160),width=3)
d.text((W//2-210,y0+ph//2+2),"NAS",font=F(1),fill=(0,0,0,0))
# title with shadow
sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
txt(sd,(W//2,265),"ساعة النداء الفورية",F(170),(0,20,40,230))
sh=sh.filter(ImageFilter.GaussianBlur(10))
im=Image.alpha_composite(im,sh); d=ImageDraw.Draw(im)
txt(d,(W//2,258),"ساعة النداء الفورية",F(170),(255,255,255,255))
# badge
bf=F(54); t="حصري لدى ناس كارت"
bb=d.textbbox((0,0),t,font=bf,direction='rtl',language='ar'); bw=bb[2]-bb[0]+110; bh=96
bx=(W-bw)//2; by=380
b=Image.new('RGBA',(W,H),(0,0,0,0)); bd=ImageDraw.Draw(b)
bd.rounded_rectangle([bx,by,bx+bw,by+bh],radius=48,fill=(200,30,45,255))
bd.rounded_rectangle([bx,by,bx+bw,by+bh],radius=48,outline=(255,255,255,255),width=4)
im=Image.alpha_composite(im,b); d=ImageDraw.Draw(im)
txt(d,(W//2,by+bh//2-2),t,bf,(255,255,255,255))
im.convert('RGB').save('cover.jpg',quality=93)
im.convert('RGB').resize((800,800),Image.LANCZOS).save('cover_prev.jpg',quality=90)
