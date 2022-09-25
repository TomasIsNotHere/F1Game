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
    PATH = [(140, 66),(168, 274), (267, 262), (333, 105), (419, 254), (551, 268), (588, 117), (670, 268), (663, 579), (552, 577), (524, 415), (122, 408), (63, 243)]   
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
    images = [(ASPHALT, (0,0)), (TRACK, (0,0)),(FINISHLINE, FINISLINE_POSITION),(BORDER, (0,0)), (CHECKPOINT, CHECKPOINTPOSITION)]
    red_car = PlayerCar(3,3)
    green_car = ComputerCar(3.6,3.6,PATH)
    
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
        
    def ending(run):
        #checkpoint check -> swap to true 
        check_bool =  red_car.collision(CHECKPOINTMASK, *CHECKPOINTPOSITION)
        if check_bool != None: 
            red_car.checkpoint()
        
        #finish line for computer car
        computerCar = green_car.collision(FINISHLINE_MASK, *FINISLINE_POSITION)
        if computerCar != None:
            winOrLose = False
            run = False
            winLoseScreen(winOrLose)

            
        #finish line -> race end only if player pick up checkpoint 
        playerCar = red_car.collision(FINISHLINE_MASK, *FINISLINE_POSITION)
        results = red_car.checkpointResult()
        if playerCar != None and results == True:
            winOrLose = True
            run = False
            winLoseScreen(winOrLose)
        elif playerCar != None and results == False:
            red_car.bounce()
                       
        
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
        ending(run)
    
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
    menuRun = True
    while menuRun:
        
        MENUWIN.blit(bckgroundImg, (0,0))
        
        if menu_state == 'menu':
            if playBtn.draw(MENUWIN):
                menuRun = False
                game()
            if  infoBtn.draw(MENUWIN):
                menu_state = 'info'
            if exitBtn.draw(MENUWIN):
                menuRun = False
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
                menuRun = False
                break
            
        pygame.display.update()
        
    pygame.quit()

def winLoseScreen(winOrLose):
    
    WINLOSEWIN = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Race Game")
    
    bckgroundImg = scale(pygame.image.load('img/endingbckground.png'), 0.5)
    playImg = pygame.image.load('img/playbtn.png').convert_alpha()
    exitImg = pygame.image.load('img/exitbtn.png').convert_alpha()
    playBtn = button.Button(285,125,playImg,1)
    exitBtn = button.Button(285,375,exitImg,1)
    
    font = pygame.font.SysFont('arialblack', 40)

    
    choice = True
    while choice: 
        WINLOSEWIN.blit(bckgroundImg, (0,0))
        if winOrLose == True:
            center_text(WINLOSEWIN,font,"Victory")
            if exitBtn.draw(WINLOSEWIN):
                choice = False
                menuSett()
            if playBtn.draw(WINLOSEWIN):
                choice = False
                game()
        else : 
            center_text(WINLOSEWIN,font,"Lose")
            if exitBtn.draw(WINLOSEWIN):
                choice = False
                menuSett()
            if playBtn.draw(WINLOSEWIN):
                choice = False
                game()

        pygame.display.update()
    pygame.quit()
    
menuSett()