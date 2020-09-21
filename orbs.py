import pygame
import Box2D
import math
from Box2D.b2 import (world, polygonShape, circleShape,
    staticBody, dynamicBody, pi)

PPM = 60.0
PPM_OUT = 20.0
VIEW = 600,600
SIZE = 5
RED = (255,0,0)
BLUE = (0,0,255)
TRANS = 0,0

def zoom(num):
    global PPM
    PPM += num



class Orb():
    def __init__(self,world,pos,mass):
        self.orb_body = world.CreateDynamicBody(position=(pos),
            fixedRotation=True)
        self.mass = mass
        self.color = RED
        self.radius = SIZE*(self.mass/100)
        self.circle = self.orb_body.CreateCircleFixture(radius=self.radius,
            density=10,friction=0,restitution=1)
    def addMass(self,mass_num): #this works!!
        if 0<=self.mass+mass_num<=100:
            self.mass+=mass_num
        elif self.mass+mass_num>100:
            self.mass = 100 #caps it off
        elif self.mass+mass_num<0:
            self.mass = 0
        self.orb_body.DestroyFixture(self.orb_body.fixtures[0])
        self.radius = SIZE*(self.mass/100)
        self.circle = self.orb_body.CreateCircleFixture(radius=self.radius,
            density=10,friction=0)
    def setMass(self,mass_num):
        self.mass = mass_num
        self.orb_body.DestroyFixture(self.orb_body.fixtures[0])
        self.radius = SIZE*(self.mass/100)
        self.circle = self.orb_body.CreateCircleFixture(radius=self.radius,
            density=10,friction=0)
    def draw(self,screen,translation):
        global TRANS
        point = (self.orb_body.position-translation)* PPM
        #else:
            #point = (self.orb_body.position)* PPM
        point = point[0], VIEW[1]-point[1]
        pygame.draw.circle(screen,self.color,
            (int(point[0]),int(point[1])),int(self.radius*PPM))

class Player(Orb):
    def __init__(self,world,pos,mass):
        super().__init__(world,pos,mass)
        self.color = (255,255,255)

    def thrust(self,world,orbs,translation):
        self.orb_body.awake = True
        self.addMass(-self.mass/60)
        posa = self.orb_body.position
        posb = pygame.mouse.get_pos()
        posb = ((posb[0]/PPM),((VIEW[1]-posb[1])/PPM))
        posb = posb[0] + translation[0], posb[1] + translation[1]
        #print(posb) why does adding the tuples just make one longer tuple??
        length = ((posb[0]-posa[0])**2+(posb[1]-posa[1])**2)**(1/2)
        reduct = (self.radius/length)
        vector = (posb[0]-posa[0])*reduct*-1,(posb[1]-posa[1])*reduct*-1
        baby_radius = SIZE*self.mass/6000
        posc = posa[0]-vector[0],posa[1]-vector[1]
        reduct_baby = (self.radius+baby_radius+.5)/length
        vector_baby = ((posb[0]-posa[0])*reduct_baby*-1,
            (posb[1]-posa[1])*reduct_baby*-1)
        posd = posa[0]-vector_baby[0],posa[1]-vector_baby[1]
        self.orb_body.ApplyLinearImpulse((vector[0]*100,vector[1]*100),posc,True)
        baby = Orb(world,posd,self.mass/6)
        baby.orb_body.ApplyLinearImpulse((-vector[0]*10,-vector[1]*10),posd,True)
        baby.color = (0,0,255)
        orbs.append(baby)
