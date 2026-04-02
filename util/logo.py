#MERLogo
import turtle as tt
def tri(size,stAgl,isLeft):
    for i in range(3):
        if i==0:
            tt.seth(stAgl)
        else:
            if isLeft:
                tt.left(120)
            else:
                tt.right(120)
        tt.fd(size)
def init():
    tt.setup(800,400)
    tt.speed(0)
    tt.pensize(2)
    tt.pd()
    tt.ht()
def f():
    init()
    O=tt.pos()
    L=50
    G=[0,5,5]
    LL=[L,L*pow(2,0.5),L]
    A1=[210,30,90]
    A2=[180,60,60]
    D=[1,0,1]
    for i in range(3):
        tt.pu()
        tt.seth(A1[i])
        tt.fd(G[i])
        tt.pd()
        tri(LL[i],A2[i],D[i])
        tt.pu()
        tt.goto(O)
f()
input()