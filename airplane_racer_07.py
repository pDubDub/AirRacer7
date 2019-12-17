"""
    Program 5 - PyGame 2D Arcade Shooter

    CIS151 - MCC - Fall 2019

    Patrick Wheeler PAT2100606
    December 2019

    based on paper plane / mail pilot example
    turned into airplane racer slalom game
"""
    
import sys
import pygame
import random
from timeit import default_timer as timer
pygame.init()

# made this 3:4 (600 x 800), more like iPad and classic arcade games
# background image is 800 x 1600
screen = pygame.display.set_mode((600, 800))


# this is the player's plane
# there is still some leftover old code from template here that is unused
class Plane(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.PA_FOLD = 0
        self.PA_ROLL_LEFT = 1
        self.PA_ROLL_RIGHT = 2
        self.PA_FLY_STRAIGHT = 3

        # self.imgList = []
        # self.loadPics()
        self.dir = self.PA_FLY_STRAIGHT
        # self.frame = 0

        self.image_LEVEL = pygame.image.load("images/GeeBee100.png")
        self.image_LEFT10 = pygame.image.load("images/GeeBee100_L1.png")
        self.image_LEFT20 = pygame.image.load("images/GeeBee100_L2.png")
        self.image_LEFT30 = pygame.image.load("images/GeeBee100_L3.png")
        self.image_RIGHT10 = pygame.image.load("images/GeeBee100_R1.png")
        self.image_RIGHT20 = pygame.image.load("images/GeeBee100_R2.png")
        self.image_RIGHT30 = pygame.image.load("images/GeeBee100_R3.png")
        self.image = self.image_LEVEL
        # self.image = self.image.convert()
        # tranColor = self.image.get_at((1, 1))
        # self.image.set_colorkey(tranColor)
        self.rect = self.image.get_rect()
        self.x = 300                        # sets the start point in screen center
        self.y = 700
        self.rect.center = (self.x, self.y)
        # self.delay = 3                      # unknown
        # self.pause = self.delay             # unknown
        self.speed = 1                      # initially effects cloud speed while paused
        self.throttle = 0
        self.drag = 0
        self.dx = 0
        self.dy = 0
        self.distance = 0
        self.pylons_to_go = 10              # defines length of game
        self.pylons_missed = 0
        self.mask = pygame.mask.from_surface(self.image)

        # TODO - add result of altitude
        self.altitude = 50                  # greater throttle = greater altitude, thus forcing you to throttle up/speed up to clear trees
        # future feature: more throttle -> more heat
        #   +speed -> greater cooling... to a point
        self.engine_temp = 0

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # changed to move TOWARDS cursor, not automatically track it.
        #   and this is my complicated method to give the plane some inertia
        #   when starting to move or switching directions
        stick = (mouse_x - self.x) / 10                 # about +/- 30
        if stick < self.dx:                             # stick to the left
            self.dx -= abs(stick - self.dx) / 7        # larger number should make it more sluggish, was originally 5
        else:                                           # stick to the right
            self.dx += abs(stick - self.dx) / 7
        self.x += self.dx
        # still feel it moves left/right a little linearly. Would still like it to corner more progressively.

        # mouse_y between 300 and 700 -> throttle (thrust)
        #   was between 400 and 800 before
        # self.throttle = (400 - max(0, (mouse_y - 400))) / 20
        self.throttle = (400 - (max(min(mouse_y, 700), 300) - 300)) / 15
        # last value of 20 yields throttle of 0 to 20. reducing it, increases max speed.
        # I changed it to 15, making game harder if you run full power the whole time.

        # greater speed -> exponentially greater drag
        self.drag = ((self.speed / 20) ** 2) * 20
        # turning also increases drag
        self.drag += abs(self.dx) / 1.8             # tuning value
        # new speed = old speed + (thrust - drag)
        self.speed += (self.throttle - self.drag) / 50
        self.speed = max(5, self.speed)             # minimum speed of 5  (max is about 20)
        # in addition to moving faster, greater speed also move player sprite higher up screen
        self.y = 800 - (self.speed * 20)
        self.rect.center = (self.x, self.y)
        # self.distance += int(self.speed)

        # changing plane graphic with cornering
        print(self.dx)
        if self.dx < -25:                           # going left
            self.image = self.image_LEFT30
        elif self.dx < -10:
            self.image = self.image_LEFT20
        elif self.dx < -4:
            self.image = self.image_LEFT10
        elif self.dx > 4:                          # going right
            self.image = self.image_RIGHT10
        elif self.dx > 10:
            self.image = self.image_RIGHT20
        elif self.dx > 25:
            self.image = self.image_RIGHT30
        else:                                       # going more or less straight
            self.image = self.image_LEVEL


# the ground (background)
class Ground(pygame.sprite.Sprite):
    # initializer
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/field800x1600.png")
        self.rect = self.image.get_rect()
        self.reset()

    # update
    def update(self, speed):
        self.rect.bottom += speed
        if self.rect.bottom >= 1600:
            self.reset()

    # move image back to top
    def reset(self):
        self.rect.top = -800


class Pylon(pygame.sprite.Sprite):
    def __init__(self, side):
        pygame.sprite.Sprite.__init__(self)
        # preloading alternate images
        self.image_pylon_LEFT = pygame.image.load("images/pylon_L.png")
        self.image_pylon_RIGHT = pygame.image.load("images/pylon_R.png")
        self.image_pylon_OK = pygame.image.load("images/pylon_OK.png")
        self.image_pylon_MISS = pygame.image.load("images/pylon_MISS.png")
        self.image_pylon_END = pygame.image.load("images/pylon_END.png")
        self.side = side
        if self.side == 0:
            self.image = self.image_pylon_LEFT
            self.x = random.randrange(100, 300, 1)
            self.y = 0
        else:
            self.image = self.image_pylon_RIGHT
            self.x = random.randrange(300, 500, 1)
            self.y = -500
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.isPassed = False
        self.wasGood = False
        self.wasMissed = False
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, speed, plane_x, plane_y, pylons_to_go, pylons_missed, left_x, right_x):
        self.rect.bottom += speed
        # reset to top
        if self.rect.top >= 800 and pylons_to_go > 1:
            self.rect.top = -80
            if self.side == 0:
                self.x = random.randrange(100, right_x, 1)
                self.image = self.image_pylon_LEFT
            else:
                self.x = random.randrange(left_x, 500, 1)
                self.image = self.image_pylon_RIGHT
            if pylons_to_go <= 2:
                self.image = self.image_pylon_END
            self.rect.centerx = self.x
            self.isPassed = False
        # pass detection
        if plane_y < self.rect.bottom and not self.isPassed:
            self.isPassed = True
            if (self.side == 0 and plane_x < self.x) or (self.side == 1 and plane_x > self.x):
                self.image = self.image_pylon_OK
                # pylons_to_go -= 1
                self.wasGood = True
                self.wasMissed = False
            else:
                self.image = self.image_pylon_MISS
                # pylons_missed += 1
                self.wasMissed = True
                self.wasGood = False


# cloud objects and shadows
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/cloud_v2.png")
        self.dx = random.randrange(0, 3, 2) - 1
        # TODO - would be good if a cloud moving left did not spawn on far left side of screen
        self.x = random.randrange(-50, 650, 10)
        self.y = random.randrange(0, 400, 10)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self, speed):
        self.rect.bottom += speed
        self.rect.centerx += self.dx
        # reset to top
        if self.rect.top >= 800 or self.rect.right < -100 or self.rect.left > 600:
            self.rect.bottom = random.randrange(-600, -10, 10)
            self.rect.centerx = random.randrange(-50, 650, 10)
            self.dx = random.randrange(0, 3, 2) - 1
        # setting x and y for shadow
        self.x, self.y = self.rect.center


class CloudShadow(pygame.sprite.Sprite):
    def __init__(self, cloud_x, cloud_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/cloud_v2_shadow.png")
        self.rect = self.image.get_rect()
        self.rect.center = (cloud_x + 100, cloud_y + 100)

    def update(self, cloud_x, cloud_y):
        self.rect.center = (cloud_x + 100, cloud_y + 100)


# plane shadow
"""
        - make throttle add to or subtract from altitude (not directly linked)
            - or else speed
        - altitude determins shadow location vs. plane.x/y
"""


# TODO - might alter plane shadow to read plane.altitude, and make d_altitude based on throttle?
class PlaneShadow(pygame.sprite.Sprite):
    def __init__(self, plane_x, plane_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/GeeBee100_shadow.png")
        self.rect = self.image.get_rect()
        self.difference = 10
        self.rect.center = (plane_x + self.difference * 2, plane_y + self.difference * 2)

    def update(self, plane_x, plane_y, plane_speed):
        self.difference = plane_speed + 5
        self.rect.center = (plane_x + self.difference * 2, plane_y + self.difference * 2)


# TODO - future - create tree objects
# TODO - future - create building objects?
# TODO - future - might change Opp class to create opponent racers
# class Opp(pygame.sprite.Sprite):
#     def __init__(self):
#         pygame.sprite.Sprite.__init__(self)
#
#         # self.dir = self.PA_FLY_STRAIGHT
#
#         self.image = pygame.image.load("images/pa_fold0009.jpg")
#         self.image = self.image.convert()
#         tran_color = self.image.get_at((1, 1))
#         self.image.set_colorkey(tran_color)
#         self.rect = self.image.get_rect()
#         self.rect.center = (320, 50)
#         self.delay = 3
#         self.pause = self.delay
#         self.speed = 10
#         self.dx = 10
#         self.dy = 0
#         self.image = pygame.transform.flip(self.image, 0, 1)
#
#     def update(self):
#         self.rect.centerx += self.dx
#         self.checkbounds()
#
#     def checkbounds(self):
#         if self.rect.centerx <= 0:
#             self.dx *= -1
#         elif self.rect.centerx >= 640:
#             self.dx *= -1


def game():
    pygame.display.set_caption("Program 5 - PyGame 2D Arcade Shooter - Wheeler")

    is_initially_paused = True
    pygame.key.set_repeat()

    # create my sprites
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    the_ground = Ground()
    plane = Plane()
    plane_shadow = PlaneShadow(plane.x, plane.y)
    pylon_left = Pylon(0)
    pylon_right = Pylon(1)
    cloud = Cloud()
    cloud_shadow = CloudShadow(cloud.x, cloud.y)

    # putting sprites in Groups
    ground_sprites = pygame.sprite.Group(the_ground)
    plane_sprites = pygame.sprite.Group(plane)
    pshadow_sprites = pygame.sprite.Group(plane_shadow)
    pylon_sprites = pygame.sprite.Group(pylon_left, pylon_right)
    cloud_sprites = pygame.sprite.Group(cloud)
    cshadow_sprites = pygame.sprite.Group(cloud_shadow)

    # for onscreen text
    font_big = pygame.font.SysFont('georgia', 50, True, False)
    font_small = pygame.font.SysFont('georgia', 30, False, True)

    start_time = 0
    clock_is_running = False
    elapsed_time = start_time
    best_time = 0

    clock = pygame.time.Clock()
    keep_going = True
    while keep_going:
        clock.tick(30)
        pygame.mouse.set_visible(True)      # changed from False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if (event.mod & pygame.KMOD_META and event.key == pygame.K_q) or event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
                elif is_initially_paused and event.key == pygame.K_SPACE:
                    is_initially_paused = False
                    start_time = timer()
                    clock_is_running = True
                # if not clock_is_running and key == pygame.K_r then reset the game
                elif not clock_is_running and event.key == pygame.K_r:
                    # TODO - extract common operations into reset methods where possible.
                    # print("Reset")
                    plane.pylons_to_go = 10
                    # TODO - extract this value to a single variable instead of being hardcoded twice
                    plane.pylons_missed = 0
                    plane.x = 300
                    plane.y = 700
                    plane.rect.center = (300, 700)
                    plane.speed = 1
                    # move shadow
                    pshadow_sprites.update(plane.x, plane.y, plane.speed)
                    # reset pylons
                    pylon_left.x = random.randrange(100, 300, 1)
                    pylon_left.y = -20
                    pylon_left.rect.center = (pylon_left.x, pylon_left.y)
                    pylon_left.image = pylon_left.image_pylon_LEFT
                    pylon_left.isPassed = False
                    pylon_right.x = random.randrange(100, 300, 1)
                    pylon_right.y = -520
                    pylon_right.rect.center = (pylon_right.x, pylon_right.y)
                    pylon_right.image = pylon_right.image_pylon_RIGHT
                    pylon_right.isPassed = False
                    # reset timer
                    elapsed_time = 0
                    is_initially_paused = True

        # I let cloud animated even when game is initially paused
        cloud_sprites.update(plane.speed)
        cshadow_sprites.update(cloud.x, cloud.y)

        # embedded updates in an IF so game doesn't start until hitting 'space' to start
        if not is_initially_paused:
            plane_sprites.update()
            pshadow_sprites.update(plane.x, plane.y, plane.speed)
            ground_sprites.update(plane.speed)
            pylon_sprites.update(plane.speed, plane.x, plane.y, plane.pylons_to_go, plane.pylons_missed, pylon_left.x, pylon_right.x)

            # collision detection between plane and pylons
            if pygame.sprite.spritecollide(plane, pylon_sprites, False, pygame.sprite.collide_mask):
                plane.speed -= 0.4                  # slows the plane down while colliding

            # adds a little wind effect when passing through clouds
            if pygame.sprite.spritecollide(plane, cloud_sprites, False, pygame.sprite.collide_mask):
                plane.dx += cloud.dx / 2

            # adjusting the score if pylons are passed or missed
            if pylon_left.wasGood or pylon_right.wasGood:
                plane.pylons_to_go -= 1
                pylon_left.wasGood = False
                pylon_right.wasGood = False
            elif pylon_left.wasMissed or pylon_right.wasMissed:
                plane.pylons_to_go -= 1
                plane.pylons_missed += 1
                pylon_left.wasMissed = False
                pylon_right.wasMissed = False

            # TODO - seen a BUG where you can miss the last pylon, it doesn't count as passed, and the timer never stops,
            #           but could not reproduce.

            # Timing and Race Completion
            now_time = timer()
            # swapped order of these IF statements. As was, it didn't penalize for missing the last pylon.
            if clock_is_running:
                elapsed_time = (now_time - start_time) + (plane.pylons_missed * 5)
                # adds 10 second penalty for missing a pylon
                # reduced penalty to perhaps 5.
            # stops timer when reached the last pylon
            if plane.pylons_to_go <= 0:
                clock_is_running = False
                if elapsed_time < best_time or best_time == 0:
                    best_time = elapsed_time
                # should also land the airplane now
                # TODO - land the airplane
                """
                    stop listening to mouse
                    return to center_x
                    drop throttle to 0    
                """

        # order here defines layering
        ground_sprites.draw(screen)
        pshadow_sprites.draw(screen)
        cshadow_sprites.draw(screen)
        plane_sprites.draw(screen)
        pylon_sprites.draw(screen)
        cloud_sprites.draw(screen)

        # zero = 0
        onscreen_1 = "Time: {0:.2f}".format(elapsed_time)
        onscreen_2 = "Pylons Left: {0}".format(plane.pylons_to_go)
        onscreen_3 = "Pylons Missed: {0}".format(plane.pylons_missed)
        if is_initially_paused and not clock_is_running:
            onscreen_4 = "Press 'SPACE' to start"
        elif not clock_is_running:
            onscreen_4 = "Press 'R' to reset"
        else:
            onscreen_4 = ""
        onscreen_5 = "Best Time: {0:.2f}".format(best_time)

        text1_time = font_big.render(onscreen_1, True, (255, 255, 255))
        text2_pylons = font_small.render(onscreen_2, True, (255, 255, 255))
        text3_misses = font_small.render(onscreen_3, True, (255, 255, 255))
        text3_width = text3_misses.get_width()
        text4_begin = font_small.render(onscreen_4, True, (255, 255, 255))
        text4_width = text4_begin.get_width()
        text5_best = font_small.render(onscreen_5, True, (255, 255, 255))
        text5_width = text5_best.get_width()

        screen.blit(text1_time, (10, 10))
        screen.blit(text2_pylons, (10, 760))
        screen.blit(text3_misses, (590 - text3_width, 760))
        screen.blit(text4_begin, (300 - (text4_width / 2), 400))
        screen.blit(text5_best, (590 - text5_width, 10))

        pygame.display.flip()
    
    # plane.sndEngine.stop()
    # return mouse cursor
    # pygame.mouse.set_visible(True)
    # return scoreboard.score
    

# main
def main():
    done_playing = False
    # score = 0
    while not done_playing:
        # done_playing = instructions(score)
        if not done_playing:
            # score = game()
            game()


if __name__ == "__main__":
    main()
