from shutil import move
import pygame
import time
import math
from other.lib import *
import other.button as button

pygame.init()

def menu():
    
    WINDOW = pygame.display.set_mode((800,600))
    pygame.display.set_caption("race game")
    
    
    bckgroundImg = scale(pygame.image.load('img/menubckground.jpg'), 0.5)
    infoImg = pygame.image.load('img/info.png')
    playBtnImg = pygame.image.load('img/playbtn.png')
    exitBtnImg = pygame.image.load('img/exitbtn.png')
    infoBtnImg = pygame.image.load('img/infobtn.png')
    
    playBtn = button.Button(285,125,playBtnImg,1)
    exitBtn = button.Button(285,375,exitBtnImg,1)
    infoBtn = button.Button(285,250,infoBtnImg,1)
   
    i = 2000
    menu_state = "menu"
    while True:
        
        WINDOW.blit(bckgroundImg, (0,0))
        
        if menu_state == "menu":
            if playBtn.draw(WINDOW):
                i = 0
                break
            if exitBtn.draw(WINDOW):
                i = 1
                break
            if infoBtn.draw(WINDOW):
                menu_state = "info"
        if menu_state == "info":
            WINDOW.blit(infoImg, (30,175))
            if exitBtn.draw(WINDOW):
                menu_state = 'menu'
                
        esc = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                i = 1
                return i
                    
        pygame.display.update()
        
    pygame.quit()
    return i
            
def game():
    
    #track, border, background, press key img 
    ASPHALT = pygame.image.load("img/asphalt.jpg")
    TRACK = scale(pygame.image.load("img/map1.png"),1)
    BORDER = scale(pygame.image.load("img/map1border.png"),1)
    BORDERMASK = pygame.mask.from_surface(BORDER)   
    WAIT = pygame.image.load("img/wait.png")
    
    #finishline 
    FINISHLINE = scale(pygame.image.load("img/endline.png"), 0.12)
    FINISHLINE = pygame.transform.rotate(FINISHLINE, 270)
    FINISHLINE_MASK = pygame.mask.from_surface(FINISHLINE)
    FINISLINE_POSITION = (38,240)
    
    #checkpoint
    CHECKPOINT = scale(pygame.image.load("img/checkpint.png"), 0.12)
    CHECKPOINT = pygame.transform.rotate(CHECKPOINT, 270)
    CHECKPOINTMASK = pygame.mask.from_surface(CHECKPOINT)
    CHECKPOINTPOSITION = (38, 260)
    
    #cars 
    REDCAR = scale(pygame.image.load("img/redcar.png"), 0.040)
    GREENCAR = scale(pygame.image.load("img/greencar.png"), 0.040)
    PATH = [(140, 66),(168, 274), (267, 262), (333, 105), (419, 254), (551, 268), (588, 117), (670, 268), (663, 579), (552, 577), (524, 415), (122, 408), (63, 243)]   
    
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
    gameStart = False
    clock = pygame.time.Clock()
    images = [(ASPHALT, (0,0)), (TRACK, (0,0)),(FINISHLINE, FINISLINE_POSITION),(BORDER, (0,0)), (CHECKPOINT, CHECKPOINTPOSITION)]
    red_car = PlayerCar(3,3)
    green_car = ComputerCar(3.6,3.6,PATH)
    i = 2000
    
    def map(win,images):
        #map printing loop 
        for img, position in images:
            win.blit(img, position)
        red_car.draw(win)
        green_car.draw(win)
        pygame.display.update()
            
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
        
    def ending(i):
        #checkpoint check -> swap to true 
        check_bool =  red_car.collision(CHECKPOINTMASK, *CHECKPOINTPOSITION)
        if check_bool != None: 
            red_car.checkpoint()
        
        #finish line for computer car
        computerCar = green_car.collision(FINISHLINE_MASK, *FINISLINE_POSITION)
        if computerCar != None:
            i = 1

            
        #finish line -> race end only if player pick up checkpoint 
        playerCar = red_car.collision(FINISHLINE_MASK, *FINISLINE_POSITION)
        results = red_car.checkpointResult()
        if playerCar != None and results == True:
            i = 0
        elif playerCar != None and results == False:
            red_car.bounce()
            
        return i 
                       
        
    #game loop 
    while True:
        clock.tick(FPS)
        map(WINDOW, images)  
        
        #start after player press any key or esc
        while not gameStart == True:
                WINDOW.blit(WAIT,(0,250))
                pygame.display.update()
                for event in pygame.event.get():
                    esc = pygame.key.get_pressed()
                    if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
                        pygame.quit()
                        results = 2
                        return results
                    elif event.type == pygame.KEYDOWN:
                        gameStart = True    
        #close window 
        esc = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
                pygame.quit()
                results = 2
                return results
                
        green_car.move()
        movementOne()
        collisionCheck()
        results = ending(i)
        if results == 0 or results == 1:
            break
    
    pygame.quit()
    return results

def winLoseScreen(winOrLose):
    
    WINDOW = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Race Game")
    
    bckgroundImg = scale(pygame.image.load('img/endingbckground.png'), 0.5)
    playImg = pygame.image.load('img/playbtn.png').convert_alpha()
    exitImg = pygame.image.load('img/exitbtn.png').convert_alpha()
    winImg = pygame.image.load('img/winimg.png')
    loseImg = pygame.image.load('img/loseimg.png')
    playBtn = button.Button(285,125,playImg,1)
    exitBtn = button.Button(285,375,exitImg,1)
    

    i = 2000
    while True: 
        
        WINDOW.blit(bckgroundImg, (0,0))
        
        if winOrLose == 0:
            WINDOW.blit(winImg, (145,205))
            if exitBtn.draw(WINDOW):
                i = 0
                break
            if playBtn.draw(WINDOW):
                i = 1
                break

        elif winOrLose == 1: 
            WINDOW.blit(loseImg, (145,205))
            if exitBtn.draw(WINDOW):
                i = 0
                break
            if playBtn.draw(WINDOW):
                i = 1
                break
            
        esc = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
                i = 0
                break

        pygame.display.update()
        
    pygame.quit()
    return i 
    
state = "menu"
while True:
    if state == "menu":
        results = menu()
        if results == 0:
            state = "game"
        elif results == 1:
            state = "exit"
    if state == "game":
        results = game()
        if results == 0:
            choice = winLoseScreen(results)
            if choice == 1:
                state = "game"
            elif choice == 0:
                state = "menu"
        elif results == 1:
            choice = winLoseScreen(results)
            if choice == 1:
                state = "game"
            elif choice == 0:
                state = "menu"
        elif results == 2:
            state = "menu"
    if state == "exit":
        break
    
pygame.quit()