from shutil import move
import pygame
import time
import math
from lib import *
import button

pygame.init()

def game():
    #track, border, background 
    ASPHALT = pygame.image.load("img/asphalt.jpg")
    TRACK = scale(pygame.image.load("img/map1.png"),1)
    BORDER = scale(pygame.image.load("img/map1border.png"),1)
    BORDERMASK = pygame.mask.from_surface(BORDER)   
    #finishline 
    FINISHLINE = scale(pygame.image.load("img/endline.png"), 0.13)
    FINISHLINE = pygame.transform.rotate(FINISHLINE, 270)
    FINISHLINE_MASK = pygame.mask.from_surface(FINISHLINE)
    FINISLINE_POSITION = (34,240)
    #checkpoint
    CHECKPOINT = scale(pygame.image.load("img/checkpint.png"), 0.13)
    CHECKPOINT = pygame.transform.rotate(CHECKPOINT, 270)
    CHECKPOINTMASK = pygame.mask.from_surface(CHECKPOINT)
    CHECKPOINTPOSITION = (34, 260)
    #cars 
    REDCAR = scale(pygame.image.load("img/redcar.png"), 0.040)
    GREENCAR = scale(pygame.image.load("img/greencar.png"), 0.040)
    PATH =[(129, 146), (226, 114), (294, 204), (236, 353), (285, 454), (391, 410), (477, 218), (551, 159), (629, 216), (632, 404), (730, 456), (827, 391), (836, 216), (948, 184), (1002, 292), (994, 856), (906, 
    943), (824, 858), (828, 678), (740, 607), (188, 617), (89, 525), (85, 271)]

    #window size based on img 
    WIDTH = TRACK.get_width()
    HEIGHT = TRACK.get_height()
    #window 
    WINDOW = pygame.display.set_mode((740,700))
    pygame.display.set_caption("race game")


    class Abstract:
        def __init__(self, max_velocity, rotation_velocity):
            self.img = self.IMG
            self.max_velocity = max_velocity
            self.velocity = 0
            self.rotation_velocity = rotation_velocity
            self.angle = 0
            self.x, self.y = self.START_POS
            self.acceleration = 0.1
            self.check_P = False
        #rotation of car 
        def rotate(self, left=False, right=False):
            if left:
                self.angle += self.rotation_velocity
            elif right:
                self.angle -= self.rotation_velocity   
        def draw(self, win):
            blit_rotated(win, self.img, (self.x, self.y), self.angle)
        #forward and backward movement     
        def forward(self):
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
            self.move()
        def backward(self):
            self.velocity = max(self.velocity - self.acceleration, -self.max_velocity/2)
            self.move()
        #movement based on angle     
        def move(self):
            radians = math.radians(self.angle)
            vertical = math.cos(radians) * self.velocity
            horizontal = math.sin(radians) * self.velocity
            self.y -= vertical
            self.x -= horizontal
        #slow down while no gas
        def slowDown(self):
            self.velocity = max(self.velocity - self.acceleration / 2, 0)
            self.move()
        #collision -> two mask compare return x,y of collision  
        def collision(self, mask, x=0, y=0):
            car_mask = pygame.mask.from_surface(self.img)
            offset = (int(self.x - x ), int(self.y - y))
            coli = mask.overlap(car_mask, offset)
            return coli 
        #bounce - dodelat na nove mape !!!!!  
        def bounce(self):
            self.velocity = -self.velocity / 1.2
        #checkpoint system 
        def checkpoint(self):
            self.check_P = True
        def checkpointResult(self):
            return self.check_P
        
        def reset(self):
                self.x, self.y = self.START_POS
                self.angle = 0
                self.vel = 0
                self.check_P = False 
        
    class PlayerCar(Abstract):
        IMG = REDCAR
        START_POS = (45, 200)

    class ComputerCar(Abstract):
        IMG = GREENCAR
        START_POS = (70, 200)

        def __init__(self, max_velocity, rotation_velocity, path=[]):
            super().__init__(max_velocity, rotation_velocity)
            self.path = path
            self.current_point = 0
            self.velocity = max_velocity

        def draw_points(self, win):
            for point in self.path:
                pygame.draw.circle(win, (255, 0, 0), point, 5)

        def draw(self, win):
            super().draw(win)
            #self.draw_points(win)
            
        def calAngle(self):
            target_x, target_y = self.path[self.current_point]
            x_diff = target_x - self.x
            y_diff = target_y - self.y

            if y_diff == 0:
                desired_radian_angle = math.pi / 2
            else:
                desired_radian_angle = math.atan(x_diff / y_diff)

            if target_y > self.y:
                desired_radian_angle += math.pi

            difference_in_angle = self.angle - math.degrees(desired_radian_angle)
            if difference_in_angle >= 180:
                difference_in_angle -= 360

            if difference_in_angle > 0:
                self.angle -= min(self.rotation_velocity, abs(difference_in_angle))
            else:
                self.angle += min(self.rotation_velocity, abs(difference_in_angle))
            
        def updatePathPoints(self):
            target = self.path[self.current_point]
            rect = pygame.Rect(
                self.x, self.y, self.img.get_width(), self.img.get_height())
            if rect.collidepoint(*target):
                self.current_point += 1
                
        def move(self):
            if self.current_point >= len(self.path):
                return
            
            self.calAngle()
            self.updatePathPoints()
            super().move()
        
            
    #variables  
    FPS = 60 
    run = True 
    gameStart = False
    clock = pygame.time.Clock()
    images = [(ASPHALT, (0,0)), (TRACK, (0,0)),(FINISHLINE, FINISLINE_POSITION),(BORDER, (10,13)), (CHECKPOINT, CHECKPOINTPOSITION)]
    red_car = PlayerCar(3,3)
    green_car = ComputerCar(3,3,PATH)
    
    def map(win,images):
        #map printing loop 
        for img, position in images:
            win.blit(img, position)
        red_car.draw(win)
        green_car.draw(win)
        pygame.display.update()
            
    #first player  
    def movementOne():
        keys = pygame.key.get_pressed()
        moved = False        
        #movement 
        if keys[pygame.K_a]:
            red_car.rotate(left=True)
        if keys[pygame.K_d]:
            red_car.rotate(right=True)
        if keys[pygame.K_w]:
            moved = True
            red_car.forward()
        if keys[pygame.K_s]:
            moved = True
            red_car.backward()        
        if not moved:
            red_car.slowDown()
            
    def collisionCheck():
        #bounce while collision 
        if red_car.collision(BORDERMASK) != None:
            red_car.bounce()
        else: 
            pass
        
    def ending():
        #checkpoint check -> swap to true 
        check_bool =  red_car.collision(CHECKPOINTMASK, *CHECKPOINTPOSITION)
        if check_bool != None: 
            red_car.checkpoint()
        
        #finish line for computer car
        computerCar = green_car.collision(FINISHLINE_MASK, *FINISLINE_POSITION)
        if computerCar != None:
            car = 1
            ResultsOfRace(car)
            time.sleep(5)
            green_car.reset()
            red_car.reset()
            
        #finish line -> race end only if player pick up checkpoint 
        playerCar = red_car.collision(FINISHLINE_MASK, *FINISLINE_POSITION)
        results = red_car.checkpointResult()
        if playerCar != None and results == True:
            car = 0
            ResultsOfRace(car)
            green_car.reset()
            red_car.reset()
        elif playerCar != None and results == False:
            red_car.bounce()
            
    def ResultsOfRace(car):
        if car == 0:
            center_text(WINDOW,font, "vyhral jste")
        else: 
            center_text(WINDOW,font, "prohral jste")
        pygame.display.update()
        
    #game loop 
    while run:
        clock.tick(FPS)
        map(WINDOW, images)  
        font = pygame.font.SysFont('arialblack', 40)
        while not gameStart == True:
                center_text(WINDOW,font, "press any key to start")
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        break
                    if event.type == pygame.KEYDOWN:
                        gameStart = True
        #close window 
        esc = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
                run = False
                menuSett()

        green_car.move()
        movementOne()
        collisionCheck()
        ending()

    pygame.quit()

def menuSett():
    MENUWIN = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Race Game Menu")

    font = pygame.font.SysFont('arialblack', 40)

    TEXT_COL = (255,255,255)

    playImg = pygame.image.load('img/playbtn.png').convert_alpha()
    infoImg = pygame.image.load('img/infobtn.png').convert_alpha()
    exitImg = pygame.image.load('img/exitbtn.png').convert_alpha()
    bckgroundImg = scale(pygame.image.load('img/menubckground.jpg'), 0.5)

    playBtn = button.Button(285,125,playImg,1)
    infoBtn = button.Button(285,250,infoImg,1)
    exitBtn = button.Button(285,375,exitImg,1)


    menu_state = 'menu'
    run = True
    while run:
        
        MENUWIN.blit(bckgroundImg, (0,0))
        
        if menu_state == 'menu':
            if playBtn.draw(MENUWIN):
                #next menu or start Game
                game()
            if  infoBtn.draw(MENUWIN):
                menu_state = 'info'
            if exitBtn.draw(MENUWIN):
                run = False
                break
            
        if menu_state == 'info':
            info(font, TEXT_COL,MENUWIN)
            if exitBtn.draw(MENUWIN):
                menu_state = 'menu'
            for event in pygame.event.get():
                if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
                    menu_state = 'menu'
                    break
                
        esc = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
                run = False
                break
            
        pygame.display.update()
        
    pygame.quit()

game()