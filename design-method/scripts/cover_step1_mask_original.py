import cv2, numpy as np
im=cv2.imread('/mnt/user-data/uploads/1791417636077_image.png')
mask=np.zeros(im.shape[:2],np.uint8)
x0,y0,x1,y1=420,312,672,625
mask[:]=cv2.GC_BGD
mask[y0:y1,x0:x1]=cv2.GC_PR_BGD
# sure fg: dark pixels inside
g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
dark=(g<60)
sub=np.zeros_like(dark);sub[y0:y1,x0:x1]=True
mask[dark&sub]=cv2.GC_PR_FGD
core=np.zeros_like(dark);core[380:560,450:600]=True
mask[core]=cv2.GC_FGD
b=np.zeros((1,65));f=np.zeros((1,65))
cv2.grabCut(im,mask,None,b,f,6,cv2.GC_INIT_WITH_MASK)
m=((mask==1)|(mask==3)).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,l,s,_=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(s[1:,4]);m=((l==k)*255).astype(np.uint8)
cv2.imwrite('m.png',m)
v=im.copy();v[m==0]=(v[m==0]*0.3+np.array([0,0,255])*0.7).astype(np.uint8)
cv2.imwrite('v.png',v)
