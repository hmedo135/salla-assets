from PIL import Image, ImageDraw, ImageFont, ImageFilter
im=Image.open('cover_base.png').convert('RGBA'); W,H=im.size
F=lambda s:ImageFont.truetype('almarai.ttf',s)
g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
for y in range(0,520): gd.line([(0,y),(W,y)],fill=(0,25,50,int(110*(1-y/520))))
im=Image.alpha_composite(im,g)
def txt(d,xy,t,f,fill): d.text(xy,t,font=f,fill=fill,anchor='mm',direction='rtl',language='ar')
cy=358
sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
txt(sd,(W//2,cy+8),"ساعة النداء الفورية",F(150),(0,20,40,230)); sh=sh.filter(ImageFilter.GaussianBlur(10))
im=Image.alpha_composite(im,sh); d=ImageDraw.Draw(im)
txt(d,(W//2,cy),"ساعة النداء الفورية",F(150),(255,255,255,255))
# logo top-right corner on white rounded tile
lg=Image.open('logo_s.jpg').convert('RGB'); s=210
lg=lg.resize((s,int(s*lg.height/lg.width)),Image.LANCZOS)
pad=18; tw=s+2*pad; th=lg.height+2*pad; x=W-tw-50; y=45
tile=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(tile)
td.rounded_rectangle([x,y,x+tw,y+th],radius=36,fill=(255,255,255,255))
im=Image.alpha_composite(im,tile); im.paste(lg,(x+pad,y+pad))
im.convert('RGB').save('cover.jpg',quality=93)
im.convert('RGB').resize((800,800),Image.LANCZOS).save('cover_prev2.jpg',quality=90)
