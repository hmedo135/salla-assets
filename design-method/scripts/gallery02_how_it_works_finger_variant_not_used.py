import cv2, numpy as np, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(5); np.random.seed(5)
W=H=1600
src=cv2.imread('cover_base.png'); rem=cv2.imread('rem.png',0); wat=cv2.imread('wat.png',0)
hsv=cv2.cvtColor(src,cv2.COLOR_BGR2HSV)
ant=np.zeros(rem.shape,np.uint8); r=(392,445,440,590)
sub=(hsv[r[1]:r[3],r[0]:r[2],1]<90)&(hsv[r[1]:r[3],r[0]:r[2],2]>110)
ant[r[1]:r[3],r[0]:r[2]]=sub*255
rem=np.maximum(rem,cv2.dilate(ant,np.ones((3,3),np.uint8)))
def soft(m):
    m=cv2.erode(m,np.ones((3,3),np.uint8)); return cv2.GaussianBlur(m,(0,0),1.6).astype(np.float32)/255
F=lambda s:ImageFont.truetype('almarai.ttf',s)

# ---------- background (same family as banner/cover) ----------
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
c0=np.array([70,40,6],np.float32); c1=np.array([135,80,14],np.float32)  # BGR
t=(yy/H)[...,None]*0.75+(xx/W)[...,None]*0.1
bg=c0*(1-t)+c1*t
for gx,gy,s in ((1130,600,520),(470,640,520)):
    glow=np.exp(-(((xx-gx)/s)**2+((yy-gy)/(s*0.8))**2))[...,None]
    bg=bg+glow*np.array([85,65,8],np.float32)
n=cv2.GaussianBlur(np.random.rand(H,W).astype(np.float32),(0,0),42)
cy=H*0.62+np.sin(xx/W*4.0)*H*0.05
band=np.exp(-((yy-cy)/(H*0.17))**2)
streak=cv2.GaussianBlur(np.clip((band*1.2+(n-0.5)*1.6)-0.25,0,1),(0,0),7)
bg=bg*(1-streak[...,None]*0.45)+np.array([190,170,40],np.float32)*streak[...,None]*0.45
base=Image.fromarray(np.clip(bg,0,255).astype(np.uint8)[:,:,::-1]).convert('RGBA')

# ---------- decor: stars/dots in corners ----------
ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
for _ in range(120):
    x=random.randint(0,W); y=random.randint(0,H)
    if 330<y<1000 and 120<x<1480: continue
    r=random.randint(3,11); a=random.randint(110,220)
    if random.random()<.55:
        od.line([(x-r,y),(x+r,y)],fill=(255,255,255,a),width=2); od.line([(x,y-r),(x,y+r)],fill=(255,255,255,a),width=2)
    else: od.ellipse([x-r/3,y-r/3,x+r/3,y+r/3],fill=(255,255,255,a))
base=Image.alpha_composite(base,ov)

# ---------- products ----------
arr=np.array(base).astype(np.float32)
def put(m,box,height,cx,base_y):
    x0,y0,x1,y1=box; sc=height/(y1-y0)
    crop=src[y0:y1,x0:x1].astype(np.float32); mm=soft(m)[y0:y1,x0:x1]
    cw,ch=int((x1-x0)*sc),int((y1-y0)*sc)
    crop=cv2.resize(crop,(cw,ch),interpolation=cv2.INTER_AREA); mm=cv2.resize(mm,(cw,ch),interpolation=cv2.INTER_AREA)
    px=int(cx-cw/2); py=int(base_y-ch)
    sh=np.zeros((H,W),np.float32); cv2.ellipse(sh,(px+cw//2,py+ch),(int(cw*.46),int(ch*.04)),0,0,360,1,-1)
    sh=cv2.GaussianBlur(sh,(0,0),12)*0.55; arr[:,:,:3]*=(1-sh[...,None])
    arr[py:py+ch,px:px+cw,:3]=arr[py:py+ch,px:px+cw,:3]*(1-mm[...,None])+crop[:,:,::-1]*mm[...,None]
    return px,py,cw,ch
# remote on the RIGHT (parent), watch on the LEFT (student)  -> RTL reading flow
rp=put(rem,(330,430,730,1260),560,1175,980)
wp=put(wat,(780,490,1430,1280),400,425,980)
im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)[:,:,:3]).convert('RGBA')

# ---------- finger pressing the red button ----------
box=(330,430,730,1260); sc_r=560/(box[3]-box[1])
reg=hsv[box[1]:box[3],box[0]:box[2]]
red=(((reg[...,0]<8)|(reg[...,0]>170))&(reg[...,1]>140)&(reg[...,2]>120)).astype(np.uint8)
n_,l_,s_,c_=cv2.connectedComponentsWithStats(red)
k=1+np.argmax(s_[1:,4]); bxs,bys=c_[k]
bx=rp[0]+bxs*sc_r; by=rp[1]+bys*sc_r
print('button at',bx,by)
SS=2
fl=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); fd=ImageDraw.Draw(fl)
ang=np.radians(38)                     # finger comes from lower-right toward the button
ux,uy=np.cos(ang),np.sin(ang)          # direction from tip backwards
tipx,tipy=bx+ux*92,by+uy*92            # fingertip hovering just above the button (about to press)
fw=150; fl_len=620
def cap(d,tx,ty,wd,ln,col):
    # capsule from tip backwards
    nx,ny=-uy,ux
    pts=[(tx+nx*wd/2,ty+ny*wd/2),(tx+nx*wd/2+ux*ln,ty+ny*wd/2+uy*ln),(tx-nx*wd/2+ux*ln,ty-ny*wd/2+uy*ln),(tx-nx*wd/2,ty-ny*wd/2)]
    d.polygon([(x*SS,y*SS) for x,y in pts],fill=col)
    d.ellipse([(tx-wd/2)*SS,(ty-wd/2)*SS,(tx+wd/2)*SS,(ty+wd/2)*SS],fill=col)
# soft contact shadow on the remote
shl=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); sd_=ImageDraw.Draw(shl)
cap(sd_,tipx+26,tipy+40,fw,fl_len,(0,10,30,95))
shl=shl.filter(ImageFilter.GaussianBlur(14*SS))
cap(fd,tipx,tipy,fw,fl_len,(224,172,138,255))                 # base skin
cap(fd,tipx-6,tipy-10,fw*0.80,fl_len,(240,193,160,255))         # light top
# nail
nx_,ny_=-uy,ux
ncx,ncy=tipx+ux*34-nx_*(fw*0.0),tipy+uy*34
nl=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); nd=ImageDraw.Draw(nl)
nd.ellipse([(ncx-46)*SS,(ncy-30)*SS,(ncx+46)*SS,(ncy+30)*SS],fill=(247,214,198,255),outline=(206,150,122,255),width=3*SS)
nl=nl.rotate(-38,center=(ncx*SS,ncy*SS),resample=Image.BICUBIC)
fl=Image.alpha_composite(fl,nl)
# cuff / sleeve hint at the far end
sx,sy=tipx+ux*(fl_len-40),tipy+uy*(fl_len-40)
cd=ImageDraw.Draw(fl)
fl=fl.resize((W,H),Image.LANCZOS); shl=shl.resize((W,H),Image.LANCZOS)
im=Image.alpha_composite(im,shl); im=Image.alpha_composite(im,fl)
# press burst around the button
pb=Image.new('RGBA',(W,H),(0,0,0,0)); pd_=ImageDraw.Draw(pb)
for i,(r,a) in enumerate(((52,235),(78,170),(104,110))):
    pd_.ellipse([bx-r,by-r,bx+r,by+r],outline=(255,224,90,a),width=7)
for a_ in range(0,360,45):
    if 25<a_<105: continue          # keep clear where the finger is
    r0,r1=112,150; ca,sa=np.cos(np.radians(a_)),np.sin(np.radians(a_))
    pd_.line([(bx+ca*r0,by+sa*r0),(bx+ca*r1,by+sa*r1)],fill=(255,224,90,230),width=8)
im=Image.alpha_composite(im,pb)

# ---------- signal waves between them (from remote toward watch) ----------
wv=Image.new('RGBA',(W,H),(0,0,0,0)); wd=ImageDraw.Draw(wv)
ox,oy=rp[0]-15,rp[1]+rp[3]*0.25
for i,rad in enumerate((90,150,210,270)):
    a=int(235-i*45)
    wd.arc([ox-rad,oy-rad,ox+rad,oy+rad],150,210,fill=(255,255,255,a),width=9)
wv=wv.filter(ImageFilter.GaussianBlur(0.8)); im=Image.alpha_composite(im,wv)
# dashed arrow along the bottom of the gap, pointing at the watch
ar=Image.new('RGBA',(W,H),(0,0,0,0)); ad=ImageDraw.Draw(ar)
y=1010; x_start=rp[0]-40; x_end=wp[0]+wp[2]+50
x=x_start
while x>x_end+30:
    ad.line([(x,y),(max(x-34,x_end+30),y)],fill=(255,210,70,255),width=9); x-=64
ad.polygon([(x_end,y),(x_end+46,y-30),(x_end+46,y+30)],fill=(255,210,70,255))
im=Image.alpha_composite(im,ar)

# ---------- text ----------
def shadow_text(img,xy,s,size,fill,anchor='mm'):
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.text((xy[0],xy[1]+6),s,font=F(size),fill=(0,15,35,210),anchor=anchor,direction='rtl',language='ar')
    sh=sh.filter(ImageFilter.GaussianBlur(7)); img=Image.alpha_composite(img,sh)
    ImageDraw.Draw(img).text(xy,s,font=F(size),fill=fill,anchor=anchor,direction='rtl',language='ar'); return img
im=shadow_text(im,(800,160),"كيف تعمل؟",150,(255,255,255,255))
im=shadow_text(im,(800,265),"ثلاث خطوات .. وتوصل الإشارة",54,(200,238,250,255))

# role chips with pointers
def chip(img,cx,cy,text,col):
    d=ImageDraw.Draw(img); f=F(50)
    bb=d.textbbox((0,0),text,font=f,direction='rtl',language='ar'); w=bb[2]-bb[0]+90; h=88
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    ld.rounded_rectangle([cx-w/2,cy-h/2,cx+w/2,cy+h/2],radius=44,fill=col)
    ld.rounded_rectangle([cx-w/2,cy-h/2,cx+w/2,cy+h/2],radius=44,outline=(255,255,255,255),width=4)
    img=Image.alpha_composite(img,lay)
    ImageDraw.Draw(img).text((cx,cy-2),text,font=f,fill=(255,255,255,255),anchor='mm',direction='rtl',language='ar'); return img
im=chip(im,rp[0]+rp[2]/2,rp[1]-60,"ولي الأمر",(200,30,45,255))
im=chip(im,wp[0]+wp[2]/2,wp[1]-40,"الطالب",(0,77,115,255))

# steps (3 cards, RTL: step 1 on the right)
steps=[("١","اضغط الزر","في الريموت"),("٢","تصل الإشارة","لاسلكياً"),("٣","يصدر الإنذار","في ساعة الطالب")]
cw_,ch_=440,250; gap=40; total=3*cw_+2*gap; x_right=(W+total)/2; y0=1120
lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
for i in range(3):
    xr=x_right-i*(cw_+gap); xl=xr-cw_
    ld.rounded_rectangle([xl,y0,xr,y0+ch_],radius=36,fill=(255,255,255,235))
    ld.ellipse([xr-40-86,y0+26,xr-40,y0+26+86],fill=(0,77,115,255))
im=Image.alpha_composite(im,lay); d=ImageDraw.Draw(im)
for i,(num,l1,l2) in enumerate(steps):
    xr=x_right-i*(cw_+gap)
    d.text((xr-40-43,y0+26+41),num,font=F(58),fill=(255,255,255,255),anchor='mm',direction='rtl',language='ar')
    d.text((xr-30,y0+150),l1,font=F(50),fill=(0,77,115,255),anchor='rm',direction='rtl',language='ar')
    d.text((xr-30,y0+208),l2,font=F(40),fill=(70,100,120,255),anchor='rm',direction='rtl',language='ar')

# footer pill
pill_t="بدون شريحة  •  بدون إنترنت  •  بدون اشتراكات"
bb=d.textbbox((0,0),pill_t,font=F(44),direction='rtl',language='ar'); pw=bb[2]-bb[0]+120
lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
ld.rounded_rectangle([W/2-pw/2,1430,W/2+pw/2,1430+92],radius=46,fill=(0,35,60,215))
ld.rounded_rectangle([W/2-pw/2,1430,W/2+pw/2,1430+92],radius=46,outline=(120,220,240,255),width=3)
im=Image.alpha_composite(im,lay); d=ImageDraw.Draw(im)
d.text((W/2,1430+44),pill_t,font=F(44),fill=(255,255,255,255),anchor='mm',direction='rtl',language='ar')
im.convert('RGB').save('img02.jpg',quality=94)
im.convert('RGB').resize((800,800),Image.LANCZOS).save('img02_prev.jpg',quality=90)
