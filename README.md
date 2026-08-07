# Pygame Pong with Spin and Tilt Physics

* This is a local 2-player Pong game built from scratch using Python and Pygame
* Made using OOP
* Includes many new features

## Features
*   **Ball Spin (Magnus Effect):** If you move your paddle up or down right as you hit the ball, you slice it and add spin. The code calculates a constant force that makes the ball literally curve and bend through the air mid-flight
*   **Paddle Tilting:** You can manually tilt your paddle forward and backward. The ball doesn't just bounce at a boring 90-degree angle anymore; it bounces based on the exact angle of your paddle's surface
*   **Visual Trails & Spin Indicator:** Slicing the ball with high spin creates a fading smoke trail behind it. There is also a little black crosshair indicator drawn inside the ball that spins faster or slower depending on how much spin you put on it
*   **Win-by-Two Rule:** The game goes to 7 points, but you have to win by a clear 2-point lead. If it hits a 7-6 tie, you keep playing until someone gets a 2-point advantage (like 8-6 or 9-7)

## Controls
The game is local multiplayer on a single keyboard.

| Controls | Player 1 (Left Side) | Player 2 (Right Side) |
| :--- | :--- | :--- |
| **Move Up / Down** | `W` / `S` | `Up Arrow` / `Down Arrow` |
| **Tilt Paddle** | `A` / `D` | `Left Arrow` / `Right Arrow` |