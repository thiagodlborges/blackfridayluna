import segno
from PIL import Image, ImageDraw, ImageFont, ImageChops
SRC='logo-original.jpg'
OUT='/home/user/blackfridayluna/'
URL='https://blackfridayluna.vercel.app/'
CREME=(245,239,228); BORDO=(107,30,46); BORDO_D=(74,18,32)

# --- logo: preto sobre bege -> transparente
im=Image.open(SRC).convert('L')
bg=sorted(im.tobytes())[len(im.tobytes())//2]          # luminancia do fundo
lo=25
alpha=im.point(lambda v: 0 if v>=bg-12 else min(255,int((bg-12-v)/(bg-12-lo)*255)))
bbox=alpha.point(lambda v:255 if v>60 else 0).getbbox()
pad=int((bbox[2]-bbox[0])*0.03)
bbox=(bbox[0]-pad,bbox[1]-pad,bbox[2]+pad,bbox[3]+pad)
alpha=alpha.crop(bbox)
def logo(color):
    l=Image.new('RGBA',alpha.size,color+(255,)); l.putalpha(alpha); return l
logo_creme=logo(CREME); logo_escuro=logo((44,24,16))
logo_creme.save(OUT+'public/logo-luna.png'); logo_creme.save(OUT+'material/logo-luna-creme.png'); logo_escuro.save(OUT+'material/logo-luna-escuro.png')
print('logo',alpha.size)

# --- QR
qr=segno.make(URL,error='h')
qr.save(OUT+'material/qr-blackfridayluna.png',scale=40,border=4,dark='#000000',light='#ffffff')
qr.save(OUT+'material/qr-blackfridayluna.svg',scale=10,border=4,dark='#000000',light='#ffffff')

# --- cartaz A5 (300 dpi) 1748x2480
W,H=1748,2480
c=Image.new('RGB',(W,H),BORDO); d=ImageDraw.Draw(c)
for y in range(H):                                           # degrade bordo -> bordo escuro
    t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(BORDO[i]+(BORDO_D[i]-BORDO[i])*t) for i in range(3)))
F=lambda n,s: ImageFont.truetype(f'/usr/share/fonts/truetype/{n}',s)
serifB=lambda s:F('liberation/LiberationSerif-Bold.ttf',s); serifBI=lambda s:F('liberation/LiberationSerif-BoldItalic.ttf',s)
sans=lambda s:F('liberation/LiberationSans-Regular.ttf',s); sansB=lambda s:F('liberation/LiberationSans-Bold.ttf',s)
def center(text,y,font,fill):
    w=d.textlength(text,font=font); d.text(((W-w)/2,y),text,font=font,fill=fill)
lg=logo_creme.copy(); lg.thumbnail((720,340)); c.paste(lg,((W-lg.width)//2,130),lg)
center('BLACK FRIDAY  ·  26/11 A 02/12',560,sansB(44),(196,168,130))
center('Pontos em',650,serifB(170),CREME)
center('dobro',830,serifBI(210),(196,168,130))
center('no freezer da sede',1085,serifB(84),CREME)
q=Image.open(OUT+'material/qr-blackfridayluna.png').convert('RGB'); qs=760
q=q.resize((qs,qs),Image.NEAREST)
card=Image.new('RGB',(qs+80,qs+80),'white'); card.paste(q,(40,40))
mask=Image.new('L',card.size,0); ImageDraw.Draw(mask).rounded_rectangle((0,0,card.width-1,card.height-1),50,fill=255)
c.paste(card,((W-card.width)//2,1250),mask)
center('Aponte a câmera do celular e envie seu comprovante',2160,sans(46),CREME)
center('Cada R$ 1,00 vale 2 pontos no clube da Luna',2230,sansB(46),(196,168,130))
c.save(OUT+'material/cartaz-freezer-A5.png',dpi=(300,300)); c.save(OUT+'material/cartaz-freezer-A5.pdf',resolution=300)
print('ok')
