# Importing turtle graphics and math
import turtle
import math

class DoomTurtle:
    def __init__(self):
        self.graphics = 60 # 120 - high, 60 - medium, 20 - low
        # Screen setup
        self.screen = turtle.Screen()
        self.screen.setup(800, 600)
        self.screen.title("Turtle Doom")
        self.screen.bgcolor("black")
        self.screen.tracer(0, 0)  # Disable auto-update for faster rendering
        
        # Player settings
        self.player_x = 2.0
        self.player_y = 2.0
        self.player_angle = 0.0
        self.move_speed = 0.1
        self.rot_speed = 0.05
        
        # Raycasting settings
        self.fov = math.pi / 3  # 60 degree field of view
        self.num_rays = self.graphics      # Reduced for better performance with Turtle
        self.max_depth = 10
        self.wall_height = 1.0
        
        # Game map (1 = wall, 0 = empty space)
        self.game_map = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        # Setup controls
        self.screen.listen()
        self.screen.onkeypress(self.move_forward, "w")
        self.screen.onkeypress(self.move_backward, "s")
        self.screen.onkeypress(self.rotate_left, "a")
        self.screen.onkeypress(self.rotate_right, "d")
        self.screen.onkeypress(self.quit_game, "Escape")
        
        # Create turtle for drawing
        self.drawer = turtle.Turtle()
        self.drawer.hideturtle()
        self.drawer.penup()
        
        # Start game loop
        self.game_loop()
    
    def cast_ray(self, angle):
        # Normalize angle
        angle %= 2 * math.pi
        
        # Ray direction components
        ray_cos = math.cos(angle)
        ray_sin = math.sin(angle)
        
        # Vertical check
        v_dist = float('inf')
        
        # Looking right
        if ray_cos > 0.001:
            x = math.floor(self.player_x) + 1
            dx = 1
        # Looking left
        elif ray_cos < -0.001:
            x = math.ceil(self.player_x) - 1
            dx = -1
        else:
            x = self.player_x
            dx = 0
        
        if dx != 0:
            for _ in range(self.max_depth):
                depth = (x - self.player_x) / ray_cos
                y = self.player_y + ray_sin * depth
                
                map_x = int(x) if dx == 1 else int(x - 1)
                map_y = int(y)
                
                # Boundary check
                if 0 <= map_x < len(self.game_map) and 0 <= map_y < len(self.game_map[0]):
                    if self.game_map[map_x][map_y] == 1:
                        v_dist = depth
                        break
                
                x += dx
        
        # Horizontal check
        h_dist = float('inf')
        
        # Looking down
        if ray_sin > 0.001:
            y = math.floor(self.player_y) + 1
            dy = 1
        # Looking up
        elif ray_sin < -0.001:
            y = math.ceil(self.player_y) - 1
            dy = -1
        else:
            y = self.player_y
            dy = 0
        
        if dy != 0:
            for _ in range(self.max_depth):
                depth = (y - self.player_y) / ray_sin
                x = self.player_x + ray_cos * depth
                
                map_y = int(y) if dy == 1 else int(y - 1)
                map_x = int(x)
                
                # Boundary check
                if 0 <= map_x < len(self.game_map) and 0 <= map_y < len(self.game_map[0]):
                    if self.game_map[map_x][map_y] == 1:
                        h_dist = depth
                        break
                
                y += dy
        
        # Return the closest wall distance
        return min(v_dist, h_dist)
    
    def draw_3d_view(self):
        self.drawer.clear()
        
        # Draw ceiling
        self.drawer.goto(-400, 300)
        self.drawer.color("#333333")
        self.drawer.begin_fill()
        for _ in range(2):
            self.drawer.forward(800)
            self.drawer.right(90)
            self.drawer.forward(300)
            self.drawer.right(90)
        self.drawer.end_fill()
        
        # Draw floor
        self.drawer.goto(-400, -300)
        self.drawer.color("#222222")
        self.drawer.begin_fill()
        for _ in range(2):
            self.drawer.forward(800)
            self.drawer.right(90)
            self.drawer.forward(300)
            self.drawer.right(90)
        self.drawer.end_fill()
        
        # Cast rays and draw walls
        for ray in range(self.num_rays):
            ray_angle = self.player_angle - self.fov/2 + (ray/self.num_rays)*self.fov
            dist = self.cast_ray(ray_angle)
            
            # Fix fisheye effect
            dist *= math.cos(self.player_angle - ray_angle)
            
            if dist > 0:
                # Calculate wall height
                wall_h = (600 * self.wall_height) / dist
                
                # Calculate wall position
                wall_top = wall_h / 2
                wall_bottom = -wall_top
                
                # Determine wall color based on distance
                shade = max(0, min(255, int(255 - dist * 25)))
                color = "#{:02x}{:02x}{:02x}".format(shade, shade//2, shade//3)
                
                # Draw wall slice
                slice_width = 800 / self.num_rays
                x_pos = -400 + ray * slice_width
                
                self.drawer.goto(x_pos, wall_top)
                self.drawer.color(color)
                self.drawer.begin_fill()
                self.drawer.goto(x_pos + slice_width, wall_top)
                self.drawer.goto(x_pos + slice_width, wall_bottom)
                self.drawer.goto(x_pos, wall_bottom)
                self.drawer.goto(x_pos, wall_top)
                self.drawer.end_fill()
        # Crosshair
        self.drawer.goto(0, 0)
        self.drawer.color("black")
        self.drawer.write('+', font= ("Arial", 20, "normal"))

        self.screen.update()
    
    def move_forward(self):
        new_x = self.player_x + math.cos(self.player_angle) * self.move_speed
        new_y = self.player_y + math.sin(self.player_angle) * self.move_speed
        
        # Check collision
        if self.game_map[int(new_x)][int(new_y)] == 0:
            self.player_x = new_x
            self.player_y = new_y
    
    def move_backward(self):
        new_x = self.player_x - math.cos(self.player_angle) * self.move_speed
        new_y = self.player_y - math.sin(self.player_angle) * self.move_speed
        
        # Check collision
        if self.game_map[int(new_x)][int(new_y)] == 0:
            self.player_x = new_x
            self.player_y = new_y
    
    def rotate_left(self):
        self.player_angle -= self.rot_speed
    
    def rotate_right(self):
        self.player_angle += self.rot_speed
    
    def quit_game(self):
        self.screen.bye()
    
    def game_loop(self):
        self.draw_3d_view()
        self.screen.ontimer(self.game_loop, 50)  # ~20 FPS

# Start the game
if __name__ == "__main__":
    game = DoomTurtle()
    turtle.mainloop()
