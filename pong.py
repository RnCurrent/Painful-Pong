import pygame
import sys
import random
import math

# Window and Physics Configurations
WIDTH, HEIGHT = 800, 600
PADDLE_SPEED = 7
TILT_SPEED = 2  
MAX_TILT = 10   
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

class Paddle:
    """Represents a player's paddle with authentic geometric rotation and vertices."""
    def __init__(self, x, y, width=10, height=140):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.angle = 0  
        self.current_velocity = 0  

    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED
            self.current_velocity = -PADDLE_SPEED

    def move_down(self):
        if self.rect.bottom < HEIGHT:
            self.rect.y += PADDLE_SPEED
            self.current_velocity = PADDLE_SPEED

    def tilt_up(self):
        self.angle = max(-MAX_TILT, self.angle - TILT_SPEED)

    def tilt_down(self):
        self.angle = min(MAX_TILT, self.angle + TILT_SPEED)

    def get_vertices(self):
        """Calculates the 4 actual corner points of the paddle based on its tilt angle."""
        cx, cy = self.rect.center
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        w2, h2 = self.width / 2, self.height / 2
        local_corners = [
            (-w2, -h2),  # Top-Left
            (w2, -h2),   # Top-Right
            (w2, h2),    # Bottom-Right
            (-w2, h2)    # Bottom-Left
        ]

        world_vertices = []
        for lx, ly in local_corners:
            rx = cx + (lx * cos_a + ly * sin_a)
            ry = cy + (-lx * sin_a + ly * cos_a)
            world_vertices.append((rx, ry))
        return world_vertices

    def draw(self, screen):
        vertices = self.get_vertices()
        pygame.draw.polygon(screen, WHITE, vertices)

class Ball:
    """Represents the game ball, handling spin physics, visual arrows, and trail particles."""
    def __init__(self):
        self.radius = 15
        self.rect = pygame.Rect(WIDTH // 2 - self.radius, HEIGHT // 2 - self.radius, self.radius * 2, self.radius * 2)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.base_speed = 7
        self.current_speed = self.base_speed
        self.spin = 0.0  
        self.visual_angle = 0.0  
        self.particles = []  # List holding active particle dictionaries
        self.reset(random.choice(['left', 'right']))

    def update_position(self):
        magnus_force = 0.08 * self.spin * (1.0 if self.dx > 0 else -1.0)
        self.dy += magnus_force
        
        speed = math.hypot(self.dx, self.dy)
        if speed > 0:
            self.dx = (self.dx / speed) * self.current_speed
            self.dy = (self.dy / speed) * self.current_speed

        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.visual_angle += self.spin * 3.0

        # Generate trail particles behind the center of the ball
        cx, cy = self.rect.center
        if abs(self.spin) > 0.1:
            # High spin creates more rapid, erratic cloud formations
            num_particles = random.randint(2, 4)
        else:
            num_particles = 1
            
        for _ in range(num_particles):
            # Give particles a small layout offset and velocity opposite to ball travel
            p_vx = -self.dx * 0.2 + random.uniform(-0.5, 0.5)
            # Spin applies a small vertical vortex drift to the cloud
            p_vy = -self.dy * 0.2 + (self.spin * random.uniform(0.1, 0.4)) + random.uniform(-0.5, 0.5)
            
            self.particles.append({
                'x': float(cx) + random.uniform(-5, 5),
                'y': float(cy) + random.uniform(-5, 5),
                'vx': p_vx,
                'vy': p_vy,
                'radius': random.uniform(3.0, 7.0),
                'alpha': 200.0  # Transparency ceiling
            })

        # Process and filter out dead particles
        alive_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['radius'] += 0.2    # Cloud expand over time
            p['alpha'] -= 8.0     # Cloud fade rate per frame
            
            if p['alpha'] > 0:
                alive_particles.append(p)
        self.particles = alive_particles

        self.spin *= 0.985

    def bounce_y(self):
        self.dy *= -1
        self.spin *= -0.6
        self.dx += self.spin * 0.2

    def check_poly_collision(self, paddle):
        vertices = paddle.get_vertices()
        cx, cy = self.rect.center
        
        for i in range(4):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % 4]
            
            x1, y1 = p1
            x2, y2 = p2
            dx, dy = x2 - x1, y2 - y1
            
            if dx == 0 and dy == 0:
                continue
                
            t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
            t = max(0.0, min(1.0, t))
            
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy
            
            distance = math.hypot(cx - closest_x, cy - closest_y)
            if distance <= self.radius:
                return True
        return False

    def handle_paddle_collision(self, paddle, is_left_paddle):
        relative_intersect_y = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height / 2)
        relative_intersect_y = max(-1.0, min(1.0, relative_intersect_y))
        
        max_bounce_angle = 5 * math.pi / 12
        base_bounce_angle = relative_intersect_y * max_bounce_angle
        paddle_tilt_radians = math.radians(paddle.angle)
        
        if is_left_paddle:
            bounce_angle = base_bounce_angle + paddle_tilt_radians
        else:
            bounce_angle = base_bounce_angle - paddle_tilt_radians
            
        self.current_speed = min(self.current_speed + 0.4, 18)
        
        direction = 1 if is_left_paddle else -1
        self.dx = direction * self.current_speed * math.cos(bounce_angle)
        self.dy = -self.current_speed * math.sin(bounce_angle)

        if paddle.current_velocity != 0:
            side_modifier = 1.0 if is_left_paddle else -1.0
            self.spin += (paddle.current_velocity * 0.5) * side_modifier
            self.spin = max(-4.0, min(4.0, self.spin))
            
        if is_left_paddle:
            self.x = paddle.rect.right + 2
        else:
            self.x = paddle.rect.left - self.rect.width - 2

    def reset(self, loser):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.x = float(self.rect.centerx - self.radius)
        self.y = float(self.rect.centery - self.radius)
        self.current_speed = self.base_speed
        self.spin = 0.0 
        self.visual_angle = 0.0
        self.particles = []  # Clear previous point particle leftovers
        
        angle = random.uniform(-math.pi / 6, math.pi / 6)
        if loser == 'left':
            self.dx = -self.current_speed * math.cos(angle)
        else:
            self.dx = self.current_speed * math.cos(angle)
            
        self.dy = self.current_speed * math.sin(angle)

    def draw_particles(self, screen):
        """Renders transparent clouds with alpha configurations."""
        for p in self.particles:
            # Create a localized temporary surface to safely draw individual transparent elements
            size = int(p['radius'] * 2) + 2
            p_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Base color gray with dynamic opacity fade
            color = (160, 160, 160, int(p['alpha']))
            pygame.draw.circle(p_surf, color, (size // 2, size // 2), int(p['radius']))
            
            screen.blit(p_surf, (int(p['x']) - size // 2, int(p['y']) - size // 2))

    def draw(self, screen):
        # Draw the baseline ball sphere
        pygame.draw.ellipse(screen, WHITE, self.rect)
        
        if abs(self.spin) > 0.1:
            cx, cy = self.rect.center
            rad = math.radians(self.visual_angle)
            
            line_len = self.radius - 2
            x_end = cx + line_len * math.cos(rad)
            y_end = cy + line_len * math.sin(rad)
            x_start = cx - line_len * math.cos(rad)
            y_start = cy - line_len * math.sin(rad)
            
            pygame.draw.line(screen, BLACK, (x_start, y_start), (x_end, y_end), 2)
            
            arrow_angle = rad + (math.pi / 6 if self.spin > 0 else -math.pi / 6)
            arrow_len = 5
            
            tip_x1 = x_end - arrow_len * math.cos(arrow_angle)
            tip_y1 = y_end - arrow_len * math.sin(arrow_angle)
            
            arrow_angle2 = rad - (math.pi / 6 if self.spin > 0 else -math.pi / 6)
            tip_x2 = x_end - arrow_len * math.cos(arrow_angle2)
            tip_y2 = y_end - arrow_len * math.sin(arrow_angle2)
            
            pygame.draw.line(screen, BLACK, (x_end, y_end), (tip_x1, tip_y1), 2)
            pygame.draw.line(screen, BLACK, (x_end, y_end), (tip_x2, tip_y2), 2)

class Game:
    """Manages the overall game state, loops, events, and rendering."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Painful Pong")
        self.clock = pygame.time.Clock()
        
        self.opponent = Paddle(15, HEIGHT // 2 - 70)       
        self.player = Paddle(WIDTH - 25, HEIGHT // 2 - 70)  
        self.ball = Ball()
        
        self.player_score = 0
        self.opponent_score = 0
        self.score_font = pygame.font.Font(None, 74)
        self.label_font = pygame.font.Font(None, 36)

    def check_winner(self):
        if self.player_score >= 7 or self.opponent_score >= 7:
            if abs(self.player_score - self.opponent_score) >= 2:
                return True
        return False

    def handle_game_over(self):
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.player_score = 0
                        self.opponent_score = 0
                        self.ball.reset(random.choice(['left', 'right']))
                        waiting_for_input = False
            
            self.screen.fill(BLACK)
            winner_text = "Player 2 Wins!" if self.player_score > self.opponent_score else "Player 1 Wins!"
            end_font = pygame.font.Font(None, 60)
            sub_font = pygame.font.Font(None, 36)
            
            text_surface = end_font.render(winner_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            self.screen.blit(text_surface, text_rect)
            
            replay_surface = sub_font.render("Press Enter to play again", True, (200, 200, 200))
            replay_rect = replay_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            self.screen.blit(replay_surface, replay_rect)
            
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()

            self.opponent.current_velocity = 0
            self.player.current_velocity = 0

            # Player 1 Controls
            if keys[pygame.K_w]:
                self.opponent.move_up()
            if keys[pygame.K_s]:
                self.opponent.move_down()
            if keys[pygame.K_a]:
                self.opponent.tilt_up()
            if keys[pygame.K_d]:
                self.opponent.tilt_down()

            # Player 2 Controls
            if keys[pygame.K_UP]:
                self.player.move_up()
            if keys[pygame.K_DOWN]:
                self.player.move_down()
            if keys[pygame.K_LEFT]:
                self.player.tilt_up()
            if keys[pygame.K_RIGHT]:
                self.player.tilt_down()

            # Physics & Ball Updates
            self.ball.update_position()

            # Wall Collisions
            if self.ball.rect.top <= 0 and self.ball.dy < 0:
                self.ball.bounce_y()
            elif self.ball.rect.bottom >= HEIGHT and self.ball.dy > 0:
                self.ball.bounce_y()

            # Geometric Polygon Collision Checks
            if self.ball.dx > 0 and self.ball.check_poly_collision(self.player):
                self.ball.handle_paddle_collision(self.player, is_left_paddle=False)
            elif self.ball.dx < 0 and self.ball.check_poly_collision(self.opponent):
                self.ball.handle_paddle_collision(self.opponent, is_left_paddle=True)

            # Scoring Logic
            game_over = False
            if self.ball.rect.left <= 0:
                self.player_score += 1
                if self.check_winner():
                    game_over = True
                else:
                    self.ball.reset(loser='left')
                    
            if self.ball.rect.right >= WIDTH:
                self.opponent_score += 1
                if self.check_winner():
                    game_over = True
                else:
                    self.ball.reset(loser='right')

            if game_over:
                self.handle_game_over()

            # Drawing and Rendering
            self.screen.fill(BLACK)
            
            # Particle clouds rendered underneath actual targets to preserve clear geometry
            self.ball.draw_particles(self.screen)
            
            p1_label = self.label_font.render("Player 1", True, (150, 150, 150))
            self.screen.blit(p1_label, (20, 20))
            
            p2_label = self.label_font.render("Player 2", True, (150, 150, 150))
            self.screen.blit(p2_label, (WIDTH - p2_label.get_width() - 20, 20))

            self.player.draw(self.screen)
            self.opponent.draw(self.screen)
            self.ball.draw(self.screen)

            pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

            player_text = self.score_font.render(str(self.player_score), True, WHITE)
            self.screen.blit(player_text, (WIDTH // 2 + 30, 20))
            opponent_text = self.score_font.render(str(self.opponent_score), True, WHITE)
            self.screen.blit(opponent_text, (WIDTH // 2 - 70, 20))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
