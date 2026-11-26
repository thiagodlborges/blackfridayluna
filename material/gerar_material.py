import segno
from PIL import Image, ImageDraw, ImageFont, ImageChops
SRC='/home/user/blackfridayluna/material/logo-original.jpg'
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
W,H=1748,2480; OURO=(196,168,130)
c=Image.new('RGB',(W,H),BORDO); d=ImageDraw.Draw(c)
for y in range(H):
    t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(BORDO[i]+(BORDO_D[i]-BORDO[i])*t) for i in range(3)))
F=lambda n,s: ImageFont.truetype(f'/usr/share/fonts/truetype/{n}',s)
serifB=lambda s:F('liberation/LiberationSerif-Bold.ttf',s); serifBI=lambda s:F('liberation/LiberationSerif-BoldItalic.ttf',s)
sans=lambda s:F('liberation/LiberationSans-Regular.ttf',s); sansB=lambda s:F('liberation/LiberationSans-Bold.ttf',s)
def center(text,y,font,fill):
    w=d.textlength(text,font=font); d.text(((W-w)/2,y),text,font=font,fill=fill)
lg=logo_creme.copy(); lg.thumbnail((620,300)); c.paste(lg,((W-lg.width)//2,110),lg)
center('BLACK FRIDAY  ·  26/11 A 02/12',450,sansB(40),OURO)
f1,f2=serifB(150),serifBI(175); a,b='Pontos em ','dobro'
wa,wb=d.textlength(a,font=f1),d.textlength(b,font=f2); x=(W-wa-wb)/2
d.text((x,520),a,font=f1,fill=CREME); d.text((x+wa,508),b,font=f2,fill=OURO)
center('no freezer da sede',735,serifB(72),CREME)

# passo a passo
px0,px1,py0,py1=120,W-120,880,1430
ov=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rounded_rectangle((px0,py0,px1,py1),40,fill=(245,239,228,28),outline=(196,168,130,160),width=3)
c.paste(Image.alpha_composite(c.convert('RGBA'),ov).convert('RGB')); d=ImageDraw.Draw(c)
def passo(n,y,partes):
    d.ellipse((px0+50,y,px0+50+86,y+86),fill=CREME); fn=serifB(54); wn=d.textlength(str(n),font=fn); d.text((px0+93-wn/2,y+10),str(n),font=fn,fill=BORDO)
    x=px0+170
    for txt,fnt,col in partes:
        d.text((x,y+18),txt,font=fnt,fill=col); x+=d.textlength(txt,font=fnt)
passo(1,925,[('Cadastre-se no clube da Luna em ',sansB(44),CREME)])
d.text((px0+170,925+18+54),'lunagelato.com.br',font=sansB(58),fill=OURO)
passo(2,1110,[('Compre no freezer e guarde o comprovante',sans(44),CREME)])
d.text((px0+170,1110+18+52),'da maquininha',font=sans(44),fill=CREME)
passo(3,1275,[('Aponte a câmera para o QR code e',sans(44),CREME)])
d.text((px0+170,1275+18+52),'envie o comprovante',font=sans(44),fill=CREME)

q=Image.open(OUT+'material/qr-blackfridayluna.png').convert('RGB'); qs=600
q=q.resize((qs,qs),Image.NEAREST)
card=Image.new('RGB',(qs+80,qs+80),'white'); card.paste(q,(40,40))
mask=Image.new('L',card.size,0); ImageDraw.Draw(mask).rounded_rectangle((0,0,card.width-1,card.height-1),50,fill=255)
c.paste(card,((W-card.width)//2,1490),mask)
center('Cada R$ 1,00 vale 2 pontos no clube da Luna',2240,sansB(48),OURO)
center('Vale para compras no freezer da sede e para quem já tem cadastro no clube.',2315,sans(34),CREME)
c.save(OUT+'material/cartaz-freezer-A5.png',dpi=(300,300)); c.save(OUT+'material/cartaz-freezer-A5.pdf',resolution=300)
print('ok')
