import pygame
import random
import Box2D
from orbs import *
from Box2D.b2 import (world, polygonShape, circleShape,
    staticBody, dynamicBody, pi, globals)

#TO DO:
#fix pushing bug - done!
#make babies push other orbs on collision/absorption
    # might need to play w/density/size/scale
#figure out zoom in/out
    #draw everything based off screen size, ppm, player location
    # special case for zoom all the way out- don't trace/center on player
#create art over orbs

FPS = 60
VIEW = 600,600
TIME_STEP = 1.0/FPS
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)

game = False
m_failed = False
m_main = True
m_passed = False
m_pause = False
level = 1

pygame.init()

screen = pygame.display.set_mode((VIEW[0],VIEW[1]),0,32)
pygame.display.set_caption("osmos clone")
clock = pygame.time.Clock()

world = world(gravity=(0,0), doSleep=True)

ground_body = world.CreateStaticBody(position=(0,-4))
ground_body.CreatePolygonFixture(box=(50,5),density = 10,
    restitution = 1, friction = 0)
ceiling_body = world.CreateStaticBody(position=(0,VIEW[1]/PPM+4))
ceiling_body.CreatePolygonFixture(box=(50,5),density = 10,
    restitution = 1, friction = 0)
right_wall_body = world.CreateStaticBody(position=(VIEW[0]/PPM+4,1)
    ,angle=(pi/2))
right_wall_body.CreatePolygonFixture(box=(50,5),density = 10,
    restitution = 1, friction = 0)
left_wall_body = world.CreateStaticBody(position=(-4,1),angle=(pi/2))
left_wall_body.CreatePolygonFixture(box=(50,5),density = 10,
    restitution = 1, friction = 0)
walls = [ground_body,ceiling_body,right_wall_body,left_wall_body]


def clear_world(world):
    for body in world.bodies:
        if not body in walls:
            world.DestroyBody(body)

def make_orbs(world,level):
    clear_world(world)
    orbs = []
    player = Player(world,(5,5),20)
    orbs.append(player)
    created = 0
    num = 50
    range_small = 1,60-5*(level-1)
    if range_small[1]-1 <5:
        range_small = 1,5
    range_med = range_small[1]+1,100
    while created < num:
        size = random.randint(1,100)
        if range_small[0]<=size<=range_small[1]:
            mass = random.randint(5,15)
        elif range_med[0]<=size<=range_med[1]:
            mass = random.randint(16,40)
        x = random.randint(5,VIEW[0]/PPM-5)
        y = random.randint(5,VIEW[1]/PPM-5)
        ok = True
        for orb in orbs:
            radius = 5*mass/100
            for x_val in range(int(x-radius),int(x+radius+1)):
                y_vala = y+(radius+(x_val-x))*(radius-(x_val-x))
                y_valb = y-(radius+(x_val-x))*(radius-(x_val-x))
                if orb.circle.TestPoint((x_val,y_vala)):
                    ok = False
                elif orb.circle.TestPoint((x_val,y_valb)):
                    ok = False
            if ok:
                radius = 5*mass/100
                distance = (abs(((orb.orb_body.position[0]-x)**2
                    +(orb.orb_body.position[1]-y)**2)**(1/2)))
                min_distance = radius+orb.radius
                if distance<=.1+min_distance:
                    ok = False

        if ok:
            orb = Orb(world,(x,y),mass)
            if orb.mass<player.mass:
                orb.color = BLUE
            orbs.append(orb)
            point = random.randint(1,29),random.randint(1,29)
            while orb.circle.TestPoint(point):
                point = random.randint(1,29),random.randint(1,29)
            distance = (((point[0]-orb.orb_body.position[0])**2
                +(point[1]-orb.orb_body.position[1])**2)**(1/2))
            reduct = .25/distance
            vector = ((point[0]-orb.orb_body.position[0])*reduct,
                (point[1]-orb.orb_body.position[1])*reduct)
            #orb.orb_body.linearVelocity.Set(vector[0],vector[1])
            created+=1

    return orbs, player


def draw_poly(polygon,body,fixture):
    vertices = [(body.transform * v) * PPM for v in polygon.vertices]
    vertices = [(v[0], VIEW[1]-v[1]) for v in vertices]
    pygame.draw.polygon(screen,WHITE,vertices)
polygonShape.draw = draw_poly

def draw_circle(circle,body,fixture):
    position = body.transform * circle.pos * PPM #get corresponding coords
    position = position[0],600-position[1]
    pygame.draw.circle(screen,WHITE,
        (int(position[0]),int(position[1])),int(circle.radius*PPM))
circleShape.draw = draw_circle #assigns this to draw function

def show_text(screen,text,x,y,color,size):
    text_list = text.split('*')
    lines = 0
    for line in text_list:
        lines+=1
    size = int(size*((.9)**(lines-1)))
    if lines == 2:
        y = y-size//2
    elif lines == 3:
        y = y-size*1.1
    font = pygame.font.Font("fancy_pixels.ttf",size)
    for line in text_list:
        TextSurf, TextRect = ((font.render(line, True, color)),
            (font.render(line, True, color)).get_rect())
        TextRect.center = (x,y)
        screen.blit(TextSurf, TextRect)
        y+=size

def move_all(orbs,world):
    for orb in orbs:
        distances = {}
        for other in orbs:
            if other!=orb:
                distance = (((other.orb_body.position[0]
                    -orb.orb_body.position[0])**2+(other.orb_body.position[1]
                    -orb.orb_body.position[1])**2)**(1/2))
                distance = abs(distance)
                distances[other]=distance
        for other in orbs:
            if other != orb:
                if (orb.mass>other.mass and
                    (distances[other]-other.radius-orb.radius)<.01):
                    if other.mass>5:
                        other.addMass(-1)
                        reduct = .05 # change in mass/100*SIZE
                        vector = ((orb.orb_body.position[0]
                            -other.orb_body.position[0])*reduct,
                            (orb.orb_body.position[1]
                            -other.orb_body.position[1])*reduct)
                        move = (other.orb_body.position[0]+vector[0],
                            other.orb_body.position[1]+vector[1])
                        other.orb_body.transform = (move,other.orb_body.angle)
                    else:
                        world.DestroyBody(other.orb_body)
                        orbs.remove(other)
                    orb.addMass(.1)


#game loop below here

running = True
while running:
    if game and player.orb_body not in world.bodies:
        game = False
        m_failed = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game:
            if not m_pause:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.thrust(world,orbs)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if PPM<=95:
                            zoom(5)
                            PPM+=5
                    elif event.key == pygame.K_DOWN:
                        if PPM>=25:
                            zoom(-5)
                            PPM-=5
                    elif event.key == pygame.K_SPACE:
                        time_pause = pygame.time.get_ticks()
                        m_pause = True
            elif m_pause: #handle pause menu stuff
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_SPACE
                        and pygame.time.get_ticks()-time_pause>500):
                        m_pause = False
        #elif menus- events for menus
        elif not game:
            if m_main:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        orb_num = 20+10*(level-1)
                        orbs, player = make_orbs(world,level)
                        m_main = False
                        game = True
            elif m_failed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        orb_num = 20+10*(level-1)
                        orbs, player = make_orbs(world,level)
                        m_failed = False
                        game = True
                    elif event.key == pygame.K_ESCAPE:
                        game = False
                        m_failed = False
                        m_main = True
            elif m_passed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        orb_num = 20+10*(level-1)
                        orbs, player = make_orbs(world,level)
                        m_passed = False
                        level+=1
                        game = True
                    elif event.key == pygame.K_ESCAPE:
                        game = False
                        m_passed = False
                        m_main = True


    screen.fill(BLACK)
    if game:
        for body in walls:
            for fixture in body.fixtures:
                fixture.shape.draw(body,fixture)
        for orb in orbs:
            if orb != player:
                if orb.mass<player.mass:
                    if orb.color != BLUE:
                        if orb.color[2]<245 and orb.color[0]>10:
                            orb.color = (orb.color[0]-10,orb.color[1],orb.color[2]+10)
                        else:
                            orb.color = BLUE


                else:
                    if orb.color != RED:
                        if orb.color[0]<245 and orb.color[2]>10:
                            orb.color = (orb.color[0]+10,orb.color[1],orb.color[2]-10)
                        else:
                            orb.color = RED
            orb.draw(screen)
    if game and not m_pause:
        move_all(orbs,world)
        world.Step(TIME_STEP, 10, 10)
        show_text(screen,("level "+str(level)),520,550,WHITE,20)
        orbs.sort(key=(lambda x: x.mass),reverse=True)
        if orbs[0] == player:
            game = False
            m_passed = True


    elif m_pause:
        pygame.draw.rect(screen,WHITE,(100,200,400,200))
        pygame.draw.rect(screen,BLACK,(105,205,390,190),2)
        show_text(screen,"game paused",300,270,BLACK,40)
        show_text(screen,"press space to unpause",300,320,BLACK,20)
    elif m_failed:
        pygame.draw.rect(screen,WHITE,(100,200,400,200))
        pygame.draw.rect(screen,BLACK,(105,205,390,190),2)
        show_text(screen,"level "+str(level)+" failed",300,270,BLACK,40)
        show_text(screen,"press space to retry",300,320,BLACK,20)
        show_text(screen,"press esc for main menu",300,340,BLACK,20)

    elif m_passed:
        pygame.draw.rect(screen,WHITE,(100,200,400,200))
        pygame.draw.rect(screen,BLACK,(105,205,390,190),2)
        show_text(screen,"level "+str(level)+" passed!",300,270,BLACK,40)
        show_text(screen,"press space to continue",300,320,BLACK,20)
        show_text(screen,"press esc for main menu",300,340,BLACK,20)
    elif m_main:
        show_text(screen,"ORBS",300,200,WHITE,100)
        show_text(screen,"an osmos clone",300,260,WHITE,30)
        show_text(screen,"press space to start",300,350,WHITE,30)
        pygame.draw.circle(screen,WHITE,(40,560),60)
        pygame.draw.circle(screen,WHITE,(140,600),40)
        pygame.draw.circle(screen,WHITE,(0,450),50)
        pygame.draw.circle(screen,WHITE,(70,480),20)
        pygame.draw.circle(screen,WHITE,(115,550),10)
        pygame.draw.circle(screen,WHITE,(130,500),35)
        pygame.draw.circle(screen,WHITE,(200,600),10)

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
