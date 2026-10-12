import cv2, numpy as np, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(11); np.random.seed(11)
src=cv2.imread('cover_base.png'); rem=cv2.imread('rem.png',0); wat=cv2.imread('wat.png',0)
# antenna: low-saturation pixels in antenna rect
hsv=cv2.cvtColor(src,cv2.COLOR_BGR2HSV)
ant=np.zeros(rem.shape,np.uint8); r=(392,445,440,590)
sub=(hsv[r[1]:r[3],r[0]:r[2],1]<90)&(hsv[r[1]:r[3],r[0]:r[2],2]>110)
ant[r[1]:r[3],r[0]:r[2]]=sub*255
rem=np.maximum(rem,cv2.dilate(ant,np.ones((3,3),np.uint8)))
# soften: erode a bit to kill blue fringe, then blur
def soft(m): 
    m=cv2.erode(m,np.ones((3,3),np.uint8)); return cv2.GaussianBlur(m,(0,0),1.6).astype(np.float32)/255
objs=[(soft(rem),(330,430,730,1260)),(soft(wat),(780,490,1430,1280))]
F=lambda s:ImageFont.truetype('almarai.ttf',s)

def scene(W,H,ss,prod_h,prod_x,prod_base,text_blocks,title_blocks,out):
    w,h=W*ss,H*ss
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    # background: navy -> blue gradient + teal glow centred behind products
    c0=np.array([70,40,6],np.float32); c1=np.array([135,80,14],np.float32)   # BGR navy-ish
    t=(yy/h)[...,None]*0.6+(xx/w)[...,None]*0.15
    bg=c0*(1-t)+c1*t
    gx=prod_x*ss+prod_h*ss*0.66; gy=prod_base*ss-prod_h*ss*0.45
    glow=np.exp(-(((xx-gx)/(prod_h*ss*1.3))**2+((yy-gy)/(prod_h*ss*0.8))**2))[...,None]
    bg=bg+glow*np.array([95,75,10],np.float32)
    # paint stroke across the whole width (soft, teal)
    n=cv2.GaussianBlur(np.random.rand(h,w).astype(np.float32),(0,0),ss*7)
    cy=h*0.52+np.sin(xx/w*5.0)*h*0.06
    band=np.exp(-((yy-cy)/(h*0.2))**2)
    streak=np.clip((band*1.2+(n-0.5)*1.6)-0.25,0,1)
    streak=cv2.GaussianBlur(streak,(0,0),ss*1.2)
    bg=bg*(1-streak[...,None]*0.5)+np.array([190,170,40],np.float32)*streak[...,None]*0.5
    # signal rings behind watch
    ring=np.zeros((h,w),np.float32)
    rx=(prod_x+prod_h*1.05)*ss; ry=prod_base*ss-prod_h*ss*0.5
    for i,rad in enumerate((0.38,0.55,0.72,0.9)):
        cv2.circle(ring,(int(rx),int(ry)),int(prod_h*ss*rad),1.0-i*0.2,max(2,ss*2),cv2.LINE_AA)
    ring=cv2.GaussianBlur(ring,(0,0),ss*0.8)
    bg=bg+ring[...,None]*np.array([90,80,20],np.float32)*0.55
    # podium
    pcx=(prod_x+prod_h*0.66)*ss; pw=prod_h*ss*0.92; ph=prod_h*ss*0.15; pcy=prod_base*ss-ph*0.15
    pod=np.zeros((h,w),np.float32); cv2.ellipse(pod,(int(pcx),int(pcy)),(int(pw),int(ph)),0,0,360,1,-1,cv2.LINE_AA)
    rim=np.zeros((h,w),np.float32); cv2.ellipse(rim,(int(pcx),int(pcy+ph*0.35)),(int(pw*0.97),int(ph)),0,0,180,1,max(3,ss*3),cv2.LINE_AA)
    rimg=cv2.GaussianBlur(rim,(0,0),ss*3)
    bg=bg+rimg[...,None]*np.array([255,230,60],np.float32)*0.7
    podc=np.array([235,228,225],np.float32)*(0.82+0.18*np.clip((yy-(pcy-ph))/(2*ph),0,1))[...,None]
    pg=cv2.GaussianBlur(pod,(0,0),ss*0.8)[...,None]
    bg=bg*(1-pg)+podc*pg
    # stars / triangles / dots (avoid text zone handled by caller via x-limit)
    img=np.clip(bg,0,255)
    base=Image.fromarray(img.astype(np.uint8)[:,:,::-1]).convert('RGBA')
    ov=Image.new('RGBA',(w,h),(0,0,0,0)); od=ImageDraw.Draw(ov)
    def star(x,y,r,a):
        od.line([(x-r,y),(x+r,y)],fill=(255,255,255,a),width=max(1,ss)); od.line([(x,y-r),(x,y+r)],fill=(255,255,255,a),width=max(1,ss))
        d=int(r*.4); od.line([(x-d,y-d),(x+d,y+d)],fill=(255,255,255,int(a*.6)),width=1)
    def tri(x,y,r,rot,col,a,fill):
        pts=[(x+r*np.cos(rot+k*2.094),y+r*np.sin(rot+k*2.094)) for k in range(3)]
        (od.polygon(pts,fill=col+(a,)) if fill else od.line(pts+[pts[0]],fill=col+(a,),width=max(1,ss)))
    for _ in range(int(W*H/2200)):
        x=random.randint(0,w);y=random.randint(0,h)
        if x>(W*0.47)*ss: continue   # keep text zone mostly clean
        k=random.random()
        if k<.4: star(x,y,random.randint(3,9)*ss,random.randint(120,230))
        elif k<.75: tri(x,y,random.randint(3,8)*ss,random.uniform(0,6.28),random.choice([(255,255,255),(90,210,240),(120,235,255)]),random.randint(130,230),random.random()<.5)
        else:
            r=random.randint(1,3)*ss/1.5; od.ellipse([x-r,y-r,x+r,y+r],fill=(255,255,255,random.randint(120,220)))
    base=Image.alpha_composite(base,ov)
    # products
    arr=np.array(base).astype(np.float32)
    scale=prod_h*ss/ (1260-440)
    for m,(x0,y0,x1,y1) in objs:
        crop=src[y0:y1,x0:x1].astype(np.float32); mm=m[y0:y1,x0:x1]
        cw,ch=int((x1-x0)*scale),int((y1-y0)*scale)
        crop=cv2.resize(crop,(cw,ch),interpolation=cv2.INTER_AREA); mm=cv2.resize(mm,(cw,ch),interpolation=cv2.INTER_AREA)
        px=int(prod_x*ss+(x0-330)*scale); py=int(prod_base*ss-(1260-y0)*scale)
        # shadow
        sh=np.zeros((h,w),np.float32)
        cv2.ellipse(sh,(px+cw//2,py+ch-int(ch*0.02)),(int(cw*0.45),int(ch*0.04)),0,0,360,1,-1)
        sh=cv2.GaussianBlur(sh,(0,0),ss*2.5)*0.5
        arr[:,:,:3]*= (1-sh[...,None])
        ya,yb=max(py,0),min(py+ch,h); xa,xb=max(px,0),min(px+cw,w)
        sub=crop[ya-py:yb-py,xa-px:xb-px]; sm=mm[ya-py:yb-py,xa-px:xb-px][...,None]
        arr[ya:yb,xa:xb,:3]=arr[ya:yb,xa:xb,:3]*(1-sm)+sub[:,:,::-1]*sm
    im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)[:,:,:3]).convert('RGBA')
    # text
    sh=Image.new('RGBA',(w,h),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    for (x,y,s,size,col) in title_blocks+text_blocks:
        sd.text((x*ss,y*ss+2*ss),s,font=F(size*ss),fill=(0,15,35,200),anchor='rm',direction='rtl',language='ar')
    sh=sh.filter(ImageFilter.GaussianBlur(ss*2)); im=Image.alpha_composite(im,sh)
    d=ImageDraw.Draw(im)
    for (x,y,s,size,col) in title_blocks+text_blocks:
        d.text((x*ss,y*ss),s,font=F(size*ss),fill=col+(255,),anchor='rm',direction='rtl',language='ar')
    im.convert('RGB').resize((W,H),Image.LANCZOS).save(out,quality=94)
white=(255,255,255); ice=(200,238,250)
# desktop 1456x180
scene(1456,180,2,150,40,172,
  [(1420,104,"فقط بضغطة زر .. تخلي الساعة ترن",32,ice),(1420,148,"بدون شريحة أو إنترنت أو اشتراكات",25,ice)],
  [(1420,48,"ساعة النداء",64,white)],'bn2_desktop.jpg')
# mobile 780x390
scene(780,390,2,215,38,335,
  [(755,232,"فقط بضغطة زر",30,ice),(755,270,"تخلي الساعة ترن",30,ice),(755,315,"بدون شريحة أو إنترنت أو اشتراكات",23,ice)],
  [(755,135,"ساعة النداء",76,white)],'bn2_mobile.jpg')
a=Image.open('bn2_desktop.jpg');b=Image.open('bn2_mobile.jpg')
P=Image.new('RGB',(1456,180+20+390),(245,245,245));P.paste(a,(0,0));P.paste(b,(0,200));P.save('bn2_prev.jpg',quality=90)
