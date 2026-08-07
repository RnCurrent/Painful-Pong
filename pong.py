import pygame
import sys
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
PADDLE_SPEED = 7
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Game Objects
ball = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)
player = pygame.Rect(WIDTH - 20, HEIGHT // 2 - 70, 10, 140)
opponent = pygame.Rect(10, HEIGHT // 2 - 70, 10, 140)

# Movement Vars
ball_dx = BALL_SPEED_X * random.choice((1, -1))
ball_dy = BALL_SPEED_Y * random.choice((1, -1))

# Scores
player_score = 0
opponent_score = 0
font = pygame.font.Font(None, 74)

def reset_ball():
    """Resets the ball to the center with a completely random 360-degree direction."""
    global ball_dx, ball_dy
    ball.center = (WIDTH // 2, HEIGHT // 2)
    
    # Pick random angle in radians (0 to 2*pi)
    angle = random.uniform(0, 2 * math.pi)
    
    # Avoid angles that are too vertical
    # If angle too close to straight up or down, pick new angle
    while abs(math.cos(angle)) < 0.3:
        angle = random.uniform(0, 2 * math.pi)
    
    # Calculate velocities based on angle speed
    BASE_SPEED = 6
    ball_dx = BASE_SPEED * math.cos(angle)
    ball_dy = BASE_SPEED * math.sin(angle)

def check_winner():
    """Checks if a player has reached 7 points with a lead of at least 2."""
    global player_score, opponent_score
    
    # Check if either player has at least 7 points
    if player_score >= 7 or opponent_score >= 7:
        # Check if the score difference is 2 or more
        if abs(player_score - opponent_score) >= 2:
            return True
            
    return False

# Main Loop
while True:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Player 1 Controls
    if keys[pygame.K_w] and opponent.top > 0:
        opponent.y -= PADDLE_SPEED
    if keys[pygame.K_s] and opponent.bottom < HEIGHT:
        opponent.y += PADDLE_SPEED

    # Player 2 Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
        player.y += PADDLE_SPEED

    # Ball Movement
    ball.x += ball_dx
    ball.y += ball_dy

    # Wall Collisions
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy *= -1

    # 6. Scoring and Win Condition Check
    game_over = False
    
    if ball.left <= 0:
        player_score += 1
        if check_winner():
            game_over = True
        else:
            reset_ball()
            
    if ball.right >= WIDTH:
        opponent_score += 1
        if check_winner():
            game_over = True
        else:
            reset_ball()

    # If someone wins freeze game and wait for user input
    if game_over:
        waiting_for_input = True
        
        while waiting_for_input:
            # Handle events inside end screen loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    # If Enter pressed, reset scores and break out to play again
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        player_score = 0
                        opponent_score = 0
                        reset_ball()
                        waiting_for_input = False
            
            # Draw end screen bg
            screen.fill(BLACK)
            
            # Winner text
            winner_text = "Player 2 Wins!" if player_score > opponent_score else "Player 1 Wins!"
            
            # Fonts
            end_font = pygame.font.Font(None, 60)
            sub_font = pygame.font.Font(None, 36)
            
            # Render winner text
            text_surface = end_font.render(winner_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(text_surface, text_rect)
            
            # Render replay text
            replay_surface = sub_font.render("Press Enter to play again", True, (200, 200, 200))
            replay_rect = replay_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            screen.blit(replay_surface, replay_rect)
            
            pygame.display.flip()
            clock.tick(60)

    # Paddle Collision
    if ball.colliderect(player) and ball_dx > 0:
        ball_dx *= -1
    if ball.colliderect(opponent) and ball_dx < 0:
        ball_dx *= -1

    # Drawing
    screen.fill(BLACK)
    label_font = pygame.font.Font(None, 36)
    
    # Render "Player 1"
    p1_label = label_font.render("Player 1", True, (150, 150, 150)) # Subtle gray
    screen.blit(p1_label, (20, 20))
    
    # Render "Player 2"
    p2_label = label_font.render("Player 2", True, (150, 150, 150))
    screen.blit(p2_label, (WIDTH - p2_label.get_width() - 20, 20))

    # Draw game objects
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, WHITE, opponent)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Draw texts
    player_text = font.render(str(player_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 2 + 30, 20))
    opponent_text = font.render(str(opponent_score), True, WHITE)
    screen.blit(opponent_text, (WIDTH // 2 - 70, 20))

    # Frame Rate and Display Refresh
    pygame.display.flip()
    clock.tick(60) # 60 FPS limit
