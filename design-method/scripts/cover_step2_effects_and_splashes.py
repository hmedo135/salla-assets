import cv2, numpy as np, random
random.seed(7);np.random.seed(7)
S=2
im=cv2.imread('/mnt/user-data/uploads/1791417636077_image.png')
m=cv2.imread('m.png',0)
big=cv2.resize(im,None,fx=S,fy=S,interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
H,W=big.shape[:2]
# --- extra paint splashes (behind products): drawn on a layer then composited only on background (not on remote/watch/podium)
prot=np.zeros((H,W),np.float32)
# protect podium+remote+watch region by building mask of remote rect & podium
cv2.rectangle(prot,(180*S,225*S),(345*S,625*S),1,-1)
cv2.ellipse(prot,(400*S,640*S),(335*S,85*S),0,0,360,1,-1)
cv2.rectangle(prot,(0,560*S),(W,H),1,-1)
wm=cv2.resize(m,None,fx=S,fy=S,interpolation=cv2.INTER_LINEAR)
prot=np.maximum(prot,(wm>0).astype(np.float32))
prot=cv2.GaussianBlur(prot,(0,0),3)
def splash(cx,cy,length,thick,ang,color,alpha):
    L=np.zeros((H,W),np.float32)
    pts=[]
    for i in range(14):
        t=i/13
        x=cx+np.cos(ang)*length*(t-.5)
        y=cy+np.sin(ang)*length*(t-.5)+random.uniform(-thick*.25,thick*.25)
        r=thick*(0.5+0.5*np.sin(np.pi*t))*random.uniform(.6,1.1)
        cv2.ellipse(L,(int(x),int(y)),(int(r*2.2),int(r*.7)),np.degrees(ang),0,360,1,-1)
    # bristle streaks
    for i in range(70):
        t=random.uniform(.05,.95)
        x=cx+np.cos(ang)*length*(t-.5);y=cy+np.sin(ang)*length*(t-.5)+random.uniform(-thick,thick)
        l2=random.uniform(.05,.25)*length
        cv2.line(L,(int(x),int(y)),(int(x+np.cos(ang)*l2),int(y+np.sin(ang)*l2)),1,random.randint(1,4))
    n=cv2.GaussianBlur(np.random.rand(H,W).astype(np.float32),(0,0),6)
    L=cv2.GaussianBlur(L,(0,0),5)
    L=np.clip(L*1.6-0.2+ (n-0.5)*0.9,0,1)
    L=np.clip((L-0.3)*1.6,0,1)
    L=cv2.GaussianBlur(L,(0,0),14)
    a=(L*alpha*(1-prot))[...,None]
    return a,np.array(color,np.float32)
out=big.copy()
cols=[(215,190,40),(190,150,20),(235,215,90)] # BGR teal/cyan
for (cx,cy,l,t,a,c,al) in [
 (200,170,420,40,-0.15,cols[0],.30),
 (620,150,480,45,0.12,cols[1],.28),
 (110,430,260,36,-1.2,cols[2],.26),
 (700,330,300,34,1.1,cols[0],.28),
 (400,90,520,28,0.03,cols[2],.2),
 (60,640,200,30,-.9,cols[1],.22),
 (740,600,220,30,1.0,cols[1],.4)]:
    A,c_=splash(cx*S,cy*S,l*S,t*S,a,c,al)
    out=out*(1-A)+c_*A
# --- stars & triangles
def star(img,x,y,r,al=1):
    L=np.zeros((H,W),np.float32)
    cv2.line(L,(int(x-r),int(y)),(int(x+r),int(y)),1,2);cv2.line(L,(int(x),int(y-r)),(int(x),int(y+r)),1,2)
    d=int(r*.45);cv2.line(L,(x-d,y-d),(x+d,y+d),1,1);cv2.line(L,(x-d,y+d),(x+d,y-d),1,1)
    g=cv2.GaussianBlur(L,(0,0),r*.25)
    L=np.clip(L+g*1.5,0,1)*al*(1-prot)
    return np.clip(img+L[...,None]*255,0,255)
def tri(img,x,y,r,rot,col,filled,al=1):
    L=np.zeros((H,W),np.float32)
    p=np.array([[x+r*np.cos(rot+k*2.094),y+r*np.sin(rot+k*2.094)] for k in range(3)],np.int32)
    if filled: cv2.fillPoly(L,[p],1)
    else: cv2.polylines(L,[p],True,1,3,cv2.LINE_AA)
    L=cv2.GaussianBlur(L,(0,0),1)*al*(1-prot)
    return img*(1-L[...,None])+np.array(col,np.float32)*L[...,None]
for _ in range(26):
    x=random.randint(30*S,770*S);y=random.randint(30*S,540*S)
    if prot[y,x]>.05: continue
    star(out,x,y,random.randint(8,22),random.uniform(.5,1)) if False else None
    out=star(out,x,y,random.randint(8,24),random.uniform(.5,1))
tcols=[(255,255,255),(240,210,80),(255,230,150)]
for _ in range(30):
    x=random.randint(30*S,770*S);y=random.randint(30*S,540*S)
    if prot[y,x]>.05: continue
    out=tri(out,x,y,random.randint(10,26),random.uniform(0,6.28),random.choice(tcols),random.random()<.45,random.uniform(.6,1))
# dots
for _ in range(60):
    x=random.randint(10*S,790*S);y=random.randint(10*S,550*S)
    if prot[y,x]>.05: continue
    r=random.randint(2,6);L=np.zeros((H,W),np.float32);cv2.circle(L,(x,y),r,1,-1,cv2.LINE_AA)
    out=out*(1-L[...,None]*.8)+255*L[...,None]*.8
# --- bigger watch, anchored bottom-center
sc=1.22
ys,xs=np.where(wm>0)
x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
crop=big[y0:y1+1,x0:x1+1]; cm=wm[y0:y1+1,x0:x1+1]
nw,nh=int(crop.shape[1]*sc),int(crop.shape[0]*sc)
crop2=cv2.resize(crop,(nw,nh),interpolation=cv2.INTER_LANCZOS4)
cm2=cv2.resize(cm,(nw,nh),interpolation=cv2.INTER_LINEAR).astype(np.float32)/255
cm2=cv2.GaussianBlur(cm2,(0,0),1.2)
cx=(x0+x1)//2+8*S; by=y1+6*S
px=cx-nw//2; py=by-nh
# restore original watch area first (cover old watch pixels with blurred background fill)
old=(cv2.dilate(wm,np.ones((9,9),np.uint8))>0)
bgfill=cv2.inpaint(np.clip(out,0,255).astype(np.uint8),old.astype(np.uint8)*255,7,cv2.INPAINT_TELEA).astype(np.float32)
out=np.where(old[...,None],bgfill,out)
# shadow
sh=np.zeros((H,W),np.float32)
cv2.ellipse(sh,(cx,by-6*S),(nw//2-10*S,16*S),0,0,360,1,-1)
sh=cv2.GaussianBlur(sh,(0,0),14)*.45
out=out*(1-sh[...,None])
# paste
x_a,y_a=max(px,0),max(py,0)
roi=out[py:py+nh,px:px+nw]
out[py:py+nh,px:px+nw]=roi*(1-cm2[...,None])+crop2*cm2[...,None]
# red LED glow boost on watch
res=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite('cover_base.png',res)
cv2.imwrite('prev.jpg',cv2.resize(res,(800,800),interpolation=cv2.INTER_AREA))
print(px,py,nw,nh)
