import pygame
import math
import pygame.font
import sys
import random


pygame.init()

screen = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)
pygame.display.set_caption("Gravity Simulator")

font = pygame.font.Font(None, 20)
surface = pygame.display.get_surface()
WIDTH, HEIGTH = pygame.display.get_surface().get_size()
BACKGROUND_COLOR = (30,30,30)
STAR_COLOR=(255,255,0)
OBJECT_COLOR=(0,255,0)
MOON_COLOR=(220,220,220)
G = 6.5743015E-29
SPEED_UP=3600
USERS_ZOOM = 1
ZOOM=0.002
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
STARS_IN_BACKGROUND_COLOR = (75,75,54)
PAUSE=False


gravity_constant_speed = G *SPEED_UP*SPEED_UP
camera_x = WIDTH//2
camera_y = HEIGTH//2
dropdown_open = False


def render_info(surface, text, position):
    text_surface = font.render(text, True, (255, 255, 255))
    surface.blit(text_surface, position)

class CelestialObject:
    def __init__(self, object_type, name,  mass, radius, velocity, coordinates, color, moons_list=None, parent=None):
        self.parent = parent
        self.object_type = object_type
        self.name=name
        self.mass=mass
        self.radius=radius
        self.color = color
        self.moons_list=moons_list
        if parent is not None:
            self.initial_coordinates = [parent.initial_coordinates[0]+coordinates[0], parent.initial_coordinates[1]+coordinates[1]]
            self.initial_velocity = [parent.initial_velocity[0]+velocity[0], parent.initial_velocity[1]+velocity[1]]
            self.distance_from_parent = format((math.sqrt((self.initial_coordinates[0]-self.parent.initial_coordinates[0])**2+(self.initial_coordinates[1]-self.parent.initial_coordinates[1])**2))*1000,' ,.2f')
        else:
            self.initial_coordinates = [WIDTH//2, HEIGTH // 2]
            self.initial_velocity = [0,0]
        self.coordinates=self.initial_coordinates.copy()
        self.velocity = list(map(lambda x: x * SPEED_UP, self.initial_velocity.copy()))

    def draw(self):
        temp_radius=self.radius*ZOOM
        if temp_radius<1:
            temp_radius=1
        pygame.draw.circle(screen, self.color, (WIDTH//2+(self.coordinates[0]-camera_x)*ZOOM, HEIGTH//2+(self.coordinates[1]-camera_y)*ZOOM), temp_radius)
        if self.name=="Saturn" and temp_radius>1:
            pygame.draw.circle(screen, (32,30,3),(WIDTH//2+(self.coordinates[0]-camera_x)*ZOOM, HEIGTH//2+(self.coordinates[1]-camera_y)*ZOOM), ((temp_radius*92.00)/60.268), width=int((temp_radius*17.5)/60.268) )
            pygame.draw.circle(screen, (48,30,3),(WIDTH//2+(self.coordinates[0]-camera_x)*ZOOM, HEIGTH//2+(self.coordinates[1]-camera_y)*ZOOM), ((temp_radius*117.58)/60.268), width=int((temp_radius*25.580)/60.268) )
            pygame.draw.circle(screen, (40,40,40),(WIDTH//2+(self.coordinates[0]-camera_x)*ZOOM, HEIGTH//2+(self.coordinates[1]-camera_y)*ZOOM), ((temp_radius*136.78)/60.268), width=int((temp_radius*14.58)/60.268) )
            pygame.draw.circle(screen, (35,35,35),(WIDTH//2+(self.coordinates[0]-camera_x)*ZOOM, HEIGTH//2+(self.coordinates[1]-camera_y)*ZOOM), ((temp_radius*148)/60.268), width=int((temp_radius*10)/60.268) )

    def restart(self):
        self.velocity = list(map(lambda x: x * SPEED_UP, self.initial_velocity.copy()))
        self.coordinates=self.initial_coordinates.copy()

    def apply_gravity(self, other_object):
        dx=other_object.coordinates[0] - self.coordinates[0]
        dy = other_object.coordinates[1] - self.coordinates[1]
        distance_squared = dx**2 + dy**2
        force = (gravity_constant_speed * self.mass*other_object.mass)/distance_squared
        acceleration = force/self.mass

        angle = math.atan2(dy,dx)
        acceleration_x=acceleration*math.cos(angle)
        acceleration_y=acceleration*math.sin(angle)

        self.velocity[0]+=acceleration_x
        self.velocity[1]+=acceleration_y

    def update_position(self):
        self.coordinates[0]+= self.velocity[0]
        self.coordinates[1]+=self.velocity[1]
    
    def display_info(self):
        font_2 = pygame.font.Font(None, 30)

        pygame.draw.rect(screen, (20,20,20), (20, 20, 300, 500))  # Dropdown background
        list_of_strings_to_display = [f"Name: {self.name}","",f"Mass: {self.mass} kg","",f"Radius: {format(self.radius*1000, ' ,.2f')} km",""]
        if hasattr(self,"distance_from_parent"):
            list_of_strings_to_display.append(f"Distance from {self.parent.name}:")
            list_of_strings_to_display.append(f"{self.distance_from_parent} km")
        
        text_surfaces = []
        for line in list_of_strings_to_display:
            text_surface_in_info_option = font_2.render(line, True, WHITE)
            text_surfaces.append(text_surface_in_info_option)
        y_pos = 40
        for text_surface_in_info_option in text_surfaces:
            screen.blit(text_surface_in_info_option, ((320 - text_surface_in_info_option.get_width()) // 2, y_pos))
            y_pos += text_surface_in_info_option.get_height()  # Move down to the next line

class Dropdown:
    def __init__(self, dropbox_x,dropbox_y,dropbox_length,dropbox_width, if_opnened=False):
        self.dropbox_length=dropbox_length
        self.dropbox_x=dropbox_x
        self.dropbox_y=dropbox_y
        self.dropbox_width=dropbox_width
        self.if_opnened=if_opnened

    def draw_dropdown(self, name_of_object_in_center, list_of_objects: list[CelestialObject]):
        pygame.draw.rect(screen, GRAY, (self.dropbox_x, self.dropbox_y, self.dropbox_length, self.dropbox_width))  # Dropdown background
        pygame.draw.rect(screen, BLACK, (self.dropbox_x, self.dropbox_y, self.dropbox_length, self.dropbox_width), 2)  # Dropdown border
        text = font.render(name_of_object_in_center, True, BLACK)
        text_rect = text.get_rect(center=(self.dropbox_x+self.dropbox_length/2, self.dropbox_y+self.dropbox_width/2))
        screen.blit(text, text_rect)

        if self.if_opnened:
            for i, item in enumerate(list_of_objects):

                y = self.dropbox_y+self.dropbox_width + i * self.dropbox_width
                pygame.draw.rect(screen, WHITE, (self.dropbox_x, y, self.dropbox_length, self.dropbox_width))  # Item background
                pygame.draw.rect(screen, BLACK, (self.dropbox_x, y, self.dropbox_length, self.dropbox_width), 2)  # Item border

                text = font.render(item.name, True, BLACK)
                text_rect = text.get_rect(center=(self.dropbox_x+self.dropbox_length/2, y + self.dropbox_width/2))
                screen.blit(text, text_rect)
    
    def check_if_clicked_to_open(self, mouse_position_x, mouse_position_y, iteration):
        y_coordinate = self.dropbox_y+self.dropbox_width + iteration * self.dropbox_width
        if self.dropbox_x <= mouse_position_x <= self.dropbox_x+self.dropbox_length and y_coordinate <= mouse_position_y <= y_coordinate+self.dropbox_width:
            return True
        else:
            return False

class Checkbox:
    def __init__(self, checkbox_x, checkbox_y, checkbox_length, if_clicked=False):
        self.checkbox_x=checkbox_x
        self.checkbox_y=checkbox_y
        self.checkbox_length=checkbox_length
        self.if_clicked=if_clicked

    def draw_checkbox(self):
        pygame.draw.rect(screen, WHITE, (self.checkbox_x, self.checkbox_y, self.checkbox_length, self.checkbox_length))
        pygame.draw.rect(screen, BLACK, (self.checkbox_x, self.checkbox_y, self.checkbox_length, self.checkbox_length), 2)

        info_text = f"Display info of an object"
        info_position = (self.checkbox_x+(2*self.checkbox_length), self.checkbox_y)
        render_info(screen, info_text, info_position)
        if self.if_clicked:
            pygame.draw.rect(screen, BLACK, (self.checkbox_x+1, self.checkbox_y+1, self.checkbox_length-2, self.checkbox_length-2))


    def check_if_clicked_to_open(self, mouse_position_x, mouse_position_y):
            if self.checkbox_x <= mouse_position_x <= self.checkbox_x+self.checkbox_length and  self.checkbox_y <= mouse_position_y <= self.checkbox_y+self.checkbox_length:
                return True
            else: 
                return False

        

# Creating objects
sun = CelestialObject(object_type="star", name="Sun", mass=1.989e30, radius=696.34, velocity=[0,0], coordinates=[WIDTH//2, HEIGTH // 2], color=STAR_COLOR)
earth = CelestialObject(parent=sun, object_type="planet", name="Earth",mass=5.972e24, radius=6.371, velocity=[0, 0.02929], coordinates=[152093.25, 0], color=OBJECT_COLOR, moons_list=["Moon"])
moon = CelestialObject(parent=earth, object_type="moon", name="Moon", mass=7.34767e22, radius=1.737, velocity=[0, 0.00097], coordinates=[405.5, 0], color=MOON_COLOR)
mercury = CelestialObject(parent=sun,object_type="planet", name="Mercury",mass=3.30E+23, radius=2.4405, velocity=[0,0.03886], coordinates=[69818, 0], color=MOON_COLOR)
venus = CelestialObject(parent=sun, object_type="planet", name="Venus",mass=4.87E+24, radius=6.0518, velocity=[0,0.03478], coordinates=[108941, 0], color=(255,192,203))
mars = CelestialObject(parent=sun,object_type="planet", name="Mars", mass=6.42E+23, radius=3.3962, velocity=[0, 0.02197],coordinates=[249261, 0],color=(220,106,58), moons_list=["Phobos", "Deimos"])
phobos = CelestialObject(parent = mars, object_type="moon", name="Phobos", mass=1.06E+16, radius=0.5, velocity=[0,0.001680], coordinates=[12.378, 0], color=GRAY)
deimos = CelestialObject(parent = mars, object_type="moon", name="Deimos", mass=2.40E+15, radius=0.5, velocity=[0,-0.0013513], coordinates=[-23.436, 0], color=WHITE)
jupyter = CelestialObject(parent = sun, object_type="planet", name="Jupyter", mass=1.90E+27, radius=71.482, velocity=[0,0.01244], coordinates=[816363, 0], color=(218,137,17), moons_list=["Ganymede","Callisto","Io","Europa"])
ganymede = CelestialObject(parent = jupyter, object_type="moon", name="Ganymede", mass=1.48E+23, radius=5.2682, velocity=[0,0.0109], coordinates=[1070, 0], color=MOON_COLOR)
callisto = CelestialObject(parent = jupyter, object_type="moon", name="Callisto", mass=1.08E+23, radius=4.8206, velocity=[0,-0.0082], coordinates=[-1882.7, 0], color=MOON_COLOR)
io = CelestialObject(parent = jupyter, object_type="moon", name="Io", mass=8.93E+22, radius=3.6432, velocity=[0,0.0173], coordinates=[421.8, 0], color=MOON_COLOR)
europa = CelestialObject(parent = jupyter, object_type="moon", name="Europa", mass=4.80E+22, radius=3.1216, velocity=[-0.01374336,0], coordinates=[0, 671.1], color=MOON_COLOR)
saturn = CelestialObject(parent=sun, object_type="planet", name="Saturn", mass = 5.68E+26, radius = 60.268, velocity = [0,0.00914], coordinates=[1506527, 0], color=(255,196,107), moons_list=["Titan", "Rhea", "Dione", "Tethys"])
titan = CelestialObject(parent=saturn, object_type="moon", name="Titan", mass=1.35E+23, radius=5.149, velocity=[0, 0.00557],coordinates=[1221.87, 0], color=MOON_COLOR)
rhea = CelestialObject(parent=saturn, object_type="moon", name="Rhea", mass=2.30E+21, radius=2, velocity=[0,-0.00849], coordinates=[-527.108, 0], color=MOON_COLOR)
dione = CelestialObject(parent=saturn, object_type="moon", name="Dione", mass=1.10E+21, radius = 2, velocity = [-0.01003,0], coordinates=[0, 377.396], color=MOON_COLOR)
tethys = CelestialObject(parent=saturn, object_type="moon", name="Tethys", mass=6.20E+20, radius=2, velocity=[0,-0.01135], coordinates=[-294.619, 0], color=MOON_COLOR)
uranus = CelestialObject(parent = sun, object_type="planet", name="Uranus", mass=8.68E+25, radius=25.559, velocity=[0,-0.00649], coordinates=[-3001390, 0], color=(204,255,229), moons_list=["Titania", "Oberon", "Umbriel"])
titania = CelestialObject(parent=uranus, object_type="moon", name="Titania", mass = 3.40E+21, radius = 1.5768, velocity=[0,-0.00364], coordinates=[-435.91, 0], color=MOON_COLOR)
oberon = CelestialObject(parent=uranus, object_type="moon", name="Oberon", mass = 3.08E+21, radius = 1.5228, velocity=[-0.00315,0], coordinates=[0, 583.52], color=MOON_COLOR)
umbriel = CelestialObject(parent=uranus, object_type="moon", name="Umbriel", mass = 1.28E+21, radius = 1.1694, velocity=[0,-0.00467], coordinates=[-266.3, 0], color=MOON_COLOR)

planets_dropdown=Dropdown(WIDTH-200, 50, 100, 20)
moons_dropdown = Dropdown(WIDTH-200-100, 50, 100, 20)
info_checkbox= Checkbox(WIDTH//20, HEIGTH-15, 10)

all_celestial_objects = [sun, mercury, venus, earth, moon, mars, phobos, deimos, jupyter, ganymede, callisto, io, europa, saturn, titan, rhea, dione, tethys, uranus, titania, oberon, umbriel]

object_in_center = sun
planets = [x for x in all_celestial_objects if x.object_type!="moon"]
all_moons = [x for x in all_celestial_objects if x.object_type=="moon"]
moons=[]
stars = [[random.randint(0, WIDTH),random.randint(0, HEIGTH)] for _ in range (500)]
celestial_objects = planets
open_moons_dropdown=False


object_pointed_by_mouse=""
running = True
clock = pygame.time.Clock()
while running:
    mx,my=pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Move the camera based on arrow keys
            if event.key == pygame.K_LEFT:
                camera_x += 20000
            elif event.key == pygame.K_RIGHT:
                camera_x -= 20000
            elif event.key == pygame.K_UP:
                camera_y += 20000
            elif event.key == pygame.K_DOWN:
                camera_y -= 20000
            elif event.key == pygame.K_1 and object_in_center==sun:
                ZOOM=0.002
            elif event.key == pygame.K_2 and object_in_center==sun:
                ZOOM=0.0005
            elif event.key == pygame.K_SPACE:
                PAUSE=bool(PAUSE^1)
            elif event.key== pygame.K_COMMA:
                USERS_ZOOM *=1.2
            elif event.key==pygame.K_PERIOD:
                if USERS_ZOOM>=0.24:
                    USERS_ZOOM = USERS_ZOOM/1.2
            elif event.key==pygame.K_ESCAPE:
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if planets_dropdown.check_if_clicked_to_open(event.pos[0],event.pos[1], -1):
                planets_dropdown.if_opnened = not planets_dropdown.if_opnened
                moons_dropdown.if_opnened=False

            elif moons_dropdown.check_if_clicked_to_open(event.pos[0], event.pos[1], -1) and (object_in_center.moons_list or object_in_center.name!="moons"):
                moons_dropdown.if_opnened=not moons_dropdown.if_opnened
                planets_dropdown.if_opnened=False

            elif planets_dropdown.if_opnened:
                for i, item in enumerate(planets):
                    if planets_dropdown.check_if_clicked_to_open(event.pos[0], event.pos[1], i):
                        object_in_center = item

                planets_dropdown.if_opnened = False
                if object_in_center != sun: #all objects
                    stars = [[random.uniform(-WIDTH*0.44, WIDTH*0.44), random.uniform(-HEIGTH*0.44, HEIGTH*0.44)] for _ in range (500)]
                    SPEED_UP=180
                    gravity_constant_speed=G*SPEED_UP*SPEED_UP
                    moons.clear()
                    if object_in_center.moons_list:
                        for one_moon in all_moons:
                           for one_moon_of_object_in_center in object_in_center.moons_list:
                               if one_moon.name == one_moon_of_object_in_center:
                                   moons.append(one_moon)
                    celestial_objects=moons.copy()
                    celestial_objects.append(object_in_center)
                    for obj in celestial_objects:
                        obj.restart()
                else: #only planets and sun
                    stars = [[random.randint(0, WIDTH),random.randint(0, HEIGTH)] for _ in range (500)]
                    SPEED_UP=3600
                    camera_x = WIDTH//2
                    camera_y = HEIGTH//2
                    ZOOM=0.003
                    celestial_objects=planets
                    gravity_constant_speed=G*SPEED_UP*SPEED_UP
                    moons.clear()
                    for obj in celestial_objects:
                        obj.restart()
            elif moons_dropdown.if_opnened:
                for i, item in enumerate(moons):
                    if moons_dropdown.check_if_clicked_to_open(event.pos[0], event.pos[1], i):
                        object_in_center = item
                moons_dropdown.if_opnened=False
                stars = [[random.uniform(-WIDTH*0.44, WIDTH*0.44), random.uniform(-HEIGTH*0.44, HEIGTH*0.44)] for _ in range (500)]
                SPEED_UP=180
                celestial_objects=all_celestial_objects
                gravity_constant_speed=G*SPEED_UP*SPEED_UP
                for obj in celestial_objects:
                    obj.restart()
            elif info_checkbox.check_if_clicked_to_open(event.pos[0], event.pos[1]):
                info_checkbox.if_clicked=not info_checkbox.if_clicked

                
    screen.fill(BACKGROUND_COLOR)
    

    object_pointed_by_mouse=""
    # drawing objects
    for index, obj in enumerate(celestial_objects):
        if PAUSE==False:
            for other_object in celestial_objects:
                if obj != other_object:
                    obj.apply_gravity(other_object)
            obj.update_position()

        # Draw objects with adjusted coordinates based on camera position
        if object_in_center != sun:
            ZOOM=USERS_ZOOM
            camera_x=object_in_center.coordinates[0]
            camera_y=object_in_center.coordinates[1]
            if index==0:
                for star in stars:
                    temp_s_coor_x=star[0]
                    temp_s_coor_y=star[1]
                    star[0]=(((object_in_center.coordinates[0]-sun.coordinates[0])/200)*ZOOM)+WIDTH//2+(star[0]-camera_x/1000)*5*ZOOM
                    star[1]=HEIGTH//2+(star[1]-camera_y/1000)*5*ZOOM 
                    if star[0]<0:
                        star[0]=WIDTH+star[0]
                    elif star[0]>WIDTH:
                        star[0]=star[0]-WIDTH
                    elif star[1]<0:
                        star[1]=HEIGTH+star[1]
                    elif star[1]>HEIGTH:
                        star[1]=star[1]-HEIGTH
                    else:
                        pass   
                    pygame.draw.circle(screen, STARS_IN_BACKGROUND_COLOR, star, 1)     
                    star[0]=temp_s_coor_x
                    star[1]=temp_s_coor_y
            obj.draw()
            #Set name of displayed name of object
            if obj.radius*ZOOM <=5:
                if math.sqrt(((mx-(WIDTH//2+(obj.coordinates[0]-camera_x)*ZOOM))**2)+
                        (my-(HEIGTH//2+(obj.coordinates[1]-camera_y)*ZOOM))**2)<=5:
                    object_pointed_by_mouse=obj.name
            else:
                if math.sqrt(((mx-(WIDTH//2+(obj.coordinates[0]-camera_x)*ZOOM))**2)+
                        (my-(HEIGTH//2+(obj.coordinates[1]-camera_y)*ZOOM))**2)<=(obj.radius*ZOOM):
                    object_pointed_by_mouse=obj.name
            

        #draw with sun in center
        else:
            if index==0:
                for star in stars:
                    temp_s_coor_x=star[0]
                    temp_s_coor_y=star[1]
                    star[0]+=(camera_x//5000)
                    star[1]+=(camera_y//5000)
                    if star[0]<0:
                        star[0]=WIDTH+star[0]
                    elif star[0]>WIDTH:
                        star[0]=star[0]-WIDTH
                    elif star[1]<0:
                        star[1]=HEIGTH+star[1]
                    elif star[1]>HEIGTH:
                        star[1]=star[1]-HEIGTH
                    else:
                        pass
                    pygame.draw.circle(screen, STARS_IN_BACKGROUND_COLOR, star, 1)     
                    star[0] = temp_s_coor_x
                    star[1] = temp_s_coor_y
            obj.draw()
            #Set name of displayed object
            if obj.radius*ZOOM <=5:
                if math.sqrt(((mx-(WIDTH//2+(obj.coordinates[0]-camera_x)*ZOOM))**2)+
                        (my-(HEIGTH//2+(obj.coordinates[1]-camera_y)*ZOOM))**2)<=5:
                    object_pointed_by_mouse=obj.name
            else:
                if math.sqrt(((mx-(WIDTH//2+(obj.coordinates[0]-camera_x)*ZOOM))**2)+
                        (my-(HEIGTH//2+(obj.coordinates[1]-camera_y)*ZOOM))**2)<=(obj.radius*ZOOM):
                    object_pointed_by_mouse=obj.name
        
    if moons:
        moons_dropdown.draw_dropdown("Moons", moons)
    planets_dropdown.draw_dropdown(object_in_center.name, planets)

    #render strip on the bottom of window
    pygame.draw.rect(screen, (100,100,100), (0,HEIGTH-20,WIDTH,20))
    render_info(screen, f"{object_pointed_by_mouse}", (WIDTH//2, HEIGTH-15))

    info_checkbox.draw_checkbox()
    if info_checkbox.if_clicked:
        object_in_center.display_info()

    # if (WIDTH//2+(uranus.coordinates[0]-camera_x)*ZOOM)<0:
    #     pygame.draw.rect(screen, WHITE, (0,40,40,40))
        
# (WIDTH//2)/uranus.initial_coordinates[0]
# (WIDTH//2+(uranus.coordinates[0]-camera_x)*ZOOM)*0/(WIDTH//2+(uranus.coordinates[0]-camera_x)*ZOOM)
# (HEIGTH//2+(self.coordinates[1]-camera_y)*ZOOM)*
    pygame.display.flip()
    clock.tick(500)


pygame.quit()
sys.exit()

