import pygame
import sys
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
PADDLE_SPEED = 7
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Paddle:
    """Represents a player's paddle on screen."""
    def __init__(self, x, y, width=10, height=140):
        self.rect = pygame.Rect(x, y, width, height)

    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED

    def move_down(self):
        if self.rect.bottom < HEIGHT:
            self.rect.y += PADDLE_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)


class Ball:
    """Represents the game ball and handles its unique trajectory math."""
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)
        self.dx = BALL_SPEED_X * random.choice((1, -1))
        self.dy = BALL_SPEED_Y * random.choice((1, -1))

    def update_position(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def bounce_y(self):
        self.dy *= -1

    def bounce_x(self):
        self.dx *= -1

    def reset(self):
        """Resets ball to the center with a completely random 360-degree direction."""
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        
        # Pick random angle in radians (0 to 2*pi)
        angle = random.uniform(0, 2 * math.pi)
        
        # Avoid angles that are too vertical
        while abs(math.cos(angle)) < 0.3:
            angle = random.uniform(0, 2 * math.pi)
        
        # Calculate velocities based on angle speed
        BASE_SPEED = 6
        self.dx = BASE_SPEED * math.cos(angle)
        self.dy = BASE_SPEED * math.sin(angle)

    def draw(self, screen):
        pygame.draw.ellipse(screen, WHITE, self.rect)


class Game:
    """Manages the overall game state, loops, events, and rendering."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        
        # Instantiate objects using our new classes
        self.opponent = Paddle(10, HEIGHT // 2 - 70)       # Player 1 (Left)
        self.player = Paddle(WIDTH - 20, HEIGHT // 2 - 70)  # Player 2 (Right)
        self.ball = Ball()
        
        # Scores & Fonts
        self.player_score = 0
        self.opponent_score = 0
        self.score_font = pygame.font.Font(None, 74)
        self.label_font = pygame.font.Font(None, 36)

    def check_winner(self):
        """Checks if a player has reached 7 points with a lead of at least 2."""
        if self.player_score >= 7 or self.opponent_score >= 7:
            if abs(self.player_score - self.opponent_score) >= 2:
                return True
        return False

    def handle_game_over(self):
        """Freezes the main loop and runs the interactive menu state."""
        waiting_for_input = True
        
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.player_score = 0
                        self.opponent_score = 0
                        self.ball.reset()
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
        """The main game execution loop."""
        while True:
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Key Input Collection
            keys = pygame.key.get_pressed()

            # P1 Controls
            if keys[pygame.K_w]:
                self.opponent.move_up()
            if keys[pygame.K_s]:
                self.opponent.move_down()

            # P2 Controls
            if keys[pygame.K_UP]:
                self.player.move_up()
            if keys[pygame.K_DOWN]:
                self.player.move_down()

            # Physics & Ball Updates
            self.ball.update_position()

            # Wall Collisions
            if self.ball.rect.top <= 0 or self.ball.rect.bottom >= HEIGHT:
                self.ball.bounce_y()

            # Paddle Collision
            if self.ball.rect.colliderect(self.player.rect) and self.ball.dx > 0:
                self.ball.bounce_x()
            if self.ball.rect.colliderect(self.opponent.rect) and self.ball.dx < 0:
                self.ball.bounce_x()

            # Scoring Logic
            game_over = False
            
            if self.ball.rect.left <= 0:
                self.player_score += 1
                if self.check_winner():
                    game_over = True
                else:
                    self.ball.reset()
                    
            if self.ball.rect.right >= WIDTH:
                self.opponent_score += 1
                if self.check_winner():
                    game_over = True
                else:
                    self.ball.reset()

            if game_over:
                self.handle_game_over()

            # Drawing and Rendering
            self.screen.fill(BLACK)
            
            # Static Corner Labels
            p1_label = self.label_font.render("Player 1", True, (150, 150, 150))
            self.screen.blit(p1_label, (20, 20))
            p2_label = self.label_font.render("Player 2", True, (150, 150, 150))
            self.screen.blit(p2_label, (WIDTH - p2_label.get_width() - 20, 20))

            # Dynamic Game Objects
            self.player.draw(self.screen)
            self.opponent.draw(self.screen)
            self.ball.draw(self.screen)
            pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

            # Scores text
            player_text = self.score_font.render(str(self.player_score), True, WHITE)
            self.screen.blit(player_text, (WIDTH // 2 + 30, 20))
            opponent_text = self.score_font.render(str(self.opponent_score), True, WHITE)
            self.screen.blit(opponent_text, (WIDTH // 2 - 70, 20))

            # Frame Refresh
            pygame.display.flip()
            self.clock.tick(60)


# Program Entry Point
if __name__ == "__main__":
    game = Game()
    game.run()
