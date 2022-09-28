
path creator
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()
        green_car.path.append(pos)
        print(green_car.path)
