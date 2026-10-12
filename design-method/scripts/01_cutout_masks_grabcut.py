import cv2, numpy as np
im=cv2.imread('cover_base.png')   # 1600x1600
def gc(rect,fg_rects,bg_extra=None,it=8):
    x0,y0,x1,y1=rect
    mask=np.full(im.shape[:2],cv2.GC_BGD,np.uint8)
    mask[y0:y1,x0:x1]=cv2.GC_PR_BGD
    for (a,b,c,d) in fg_rects: mask[b:d,a:c]=cv2.GC_FGD
    if bg_extra is not None:
        for (a,b,c,d) in bg_extra: mask[b:d,a:c]=cv2.GC_BGD
    bgd=np.zeros((1,65));fgd=np.zeros((1,65))
    cv2.grabCut(im,mask,None,bgd,fgd,it,cv2.GC_INIT_WITH_MASK)
    m=((mask==1)|(mask==3)).astype(np.uint8)*255
    n,l,s,_=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(s[1:,4]);return ((l==k)*255).astype(np.uint8)
rem=gc((340,430,720,1280),[(410,600,640,1150)],bg_extra=[(340,1255,720,1280)])
wat=gc((790,500,1420,1290),[(880,700,1180,1100)])
cv2.imwrite('rem.png',rem);cv2.imwrite('wat.png',wat)
v=im.copy()
for m in (rem,wat):
    v[m==0]=(v[m==0]*0.25+np.array([0,0,255])*0.75).astype(np.uint8)
cv2.imwrite('v2.jpg',cv2.resize(v,(800,800)))
