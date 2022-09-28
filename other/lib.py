import pygame 


def scale(img, scale_size):
    size_width = round(img.get_width() * scale_size)
    size_heigth =  round(img.get_height() * scale_size)
    return pygame.transform.scale(img, (size_width,size_heigth))

def blit_rotated(win, img, top_left, angle):
    rotated_img = pygame.transform.rotate(img, angle)
    new_rect = rotated_img.get_rect(center=img.get_rect(topleft = top_left).center)
    win.blit(rotated_img, new_rect.topleft)


    