import pygame 
    
def scale(img, scale_size):
    size_width = round(img.get_width() * scale_size)
    size_heigth =  round(img.get_height() * scale_size)
    return pygame.transform.scale(img, (size_width,size_heigth))

def blit_rotated(win, img, top_left, angle):
    rotated_img = pygame.transform.rotate(img, angle)
    new_rect = rotated_img.get_rect(center=img.get_rect(topleft = top_left).center)
    win.blit(rotated_img, new_rect.topleft)

def text(text, font, text_col, x, y,constWindow):
        img = font.render(text, True, text_col)
        constWindow.blit(img, (x,y))
            
def info(font,TEXT_COL, MENUWIN):
    text('Ovladání: W,S,A,D - have fun', font, TEXT_COL, 95,225,constWindow=MENUWIN)
    
def center_text(window, font, text):
    render = font.render(text,1, (255,255,255))
    window.blit(render,(window.get_width()/2 - render.get_width()/2,window.get_height()/2 - render.get_height()/2))