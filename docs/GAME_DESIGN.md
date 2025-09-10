# Game Design Document: FRED: Ocean Cleanup
1. Game Overview
* Title: FRED: Ocean Cleanup
* Concept: An educational 2D top-down simulation game where players pilot FRED (Floating Robot for Eliminating Debris), a solar-powered Autonomous Surface Vehicle (ASV) designed for ocean cleanup.
* Target Audience: All ages, with a focus on players interested in robotics, environmental science, and physics-based challenges.
* Platform: Pygame (Python)
* Game Perspective: Bird's-eye view (top-down).
* Core Objective: Navigate FRED from a base station to collect all plastic bottles scattered in the water, achieving the lowest possible score. The score is based on the total time the propellers are active.
2. Gameplay Mechanics
FRED - The Player Character
* Representation: FRED is a catamaran, a boat with two parallel hulls. This dual-hull structure is central to the game's physics and control scheme.
* Movement: FRED moves forward based on thrust from two independently controlled propellers, one on each hull.
   * The game will simulate basic physics: momentum, drag, and turning forces. FRED will not stop instantly when thrust is cut but will drift to a stop due to water resistance.
* Collision: FRED will collide with the boundaries of the game area. Collisions will stop FRED's movement. There are no other obstacles besides the bottles to be collected.
Control System
The control system is the core challenge of the game. It mimics the differential thrust steering of a real catamaran. There is no traditional "up, down, left, right" steering or reverse function.
* Left Propeller: A dedicated key (e.g., the 'A' key or Left Arrow) activates the left propeller.
* Right Propeller: A dedicated key (e.g., the 'D' key or Right Arrow) activates the right propeller.
* Forward Movement: Pressing both keys simultaneously applies equal thrust, moving FRED straight forward.
* Turning:
   * Turn Right: Applying thrust only to the left propeller will cause FRED to pivot and turn to the right.
   * Turn Left: Applying thrust only to the right propeller will cause FRED to pivot and turn to the left.
* No Reverse: FRED cannot move backward. Players must plan their movements carefully to avoid getting stuck.
The Environment
* The Sea: A visually clear, blue, and open rectangular area. The boundaries will be clearly marked, perhaps with a coastline or docks.
* Base Station: A starting dock located in one corner of the screen where FRED begins each level.
* Plastic Bottles: These are the collectible items. They are stationary.
   * Quantity: 5-10 bottles will be randomly placed throughout the level at the start of each game.
   * Collection: When FRED's hitbox makes contact with a bottle's hitbox, the bottle is "collected" and disappears from the screen.
3. Scoring System
The goal is to complete the mission with the lowest score possible, encouraging efficiency.
* Score Calculation: The score starts at 0 and increases based on propeller usage.
   * Single Propeller: For every second that either the left or right propeller is active, the score increases by 1.
   * Both Propellers: For every second that both propellers are active, the score increases by 2.
* End Game: The game ends when the last bottle is collected. The final score is displayed, and the player can choose to play again.
4. User Interface (UI) & Heads-Up Display (HUD)
The UI will be clean and minimalistic to keep the focus on the gameplay.
* Score Display: A running counter, clearly visible in a corner of the screen (e.g., top-left).
* Bottles Remaining: An icon of a bottle with a number next to it, showing how many bottles are left to collect (e.g., top-right).
* Thrust Indicators: Simple visual cues on the screen to show when each propeller is active. This could be two simple bars or circles that light up when the corresponding key is pressed.
* Start Screen: A simple screen with the game title, a brief instruction on the controls and objective, and a "Start Game" button.
* End Screen: A screen that appears after collecting all bottles, displaying "Mission Complete!", the final score, and a "Play Again" button.
5. Art & Visual Style
* Style: Clean, simple, and vibrant 2D graphics. The style should be accessible and clear.
* FRED: A simple, top-down sprite of a catamaran. It could be stylized to look slightly futuristic and robotic. The propellers could have a simple spinning animation when active.
* Environment: The water could have a subtle, slow-moving wave or ripple texture to give it life.
* Bottles: A clear and easily recognizable sprite of a plastic water bottle.
6. Sound Design
* Propeller Sound: A low, humming sound that plays when a propeller is active. The sound could be stereo-panned, so activating the left propeller produces sound from the left speaker, and the right from the right speaker. When both are on, the sound is centered. The sound should stop immediately when the key is released.
* Collection Sound: A satisfying, positive "bloop" or "chime" sound when a bottle is collected.
* Music: A calm, ambient, and slightly inspirational background track to create a focused and relaxing atmosphere.
* UI Sounds: Simple clicks for button presses on the start/end screens.
7. Educational Component
The primary educational aspect is the hands-on understanding of differential steering and basic physics (momentum and drag). The game subtly teaches:
* Robotics & Engineering: How twin-propeller systems are used for steering in real-world robotics and marine vehicles.
* Physics: An intuitive feel for concepts like thrust, pivot turning, and inertia.
* Environmental Awareness: The game's theme highlights the problem of plastic pollution in our oceans and the innovative solutions being developed to combat it. An optional "Did You Know?" fact could appear on the end screen.
8. Pygame Implementation Plan
1. Setup: Initialize Pygame, create the game window, and set up the main game loop.
2. Assets: Create or source simple sprites for FRED, the bottle, and the background. Source sound effects.
3. FRED Class: Create a Player or FRED class to handle its position, rotation, movement logic, and rendering. Implement methods for apply_thrust_left(), apply_thrust_right(), and update() which will handle the physics calculations.
4. Bottle Class: Create a Bottle class to handle its position and rendering.
5. Game Logic:
   * Implement the control scheme to link key presses to the FRED's thrust methods.
   * Implement the scoring logic based on a timer that tracks how long each key is held down.
   * Manage a list of bottle objects and check for collisions between FRED and the bottles.
.
   6. UI: Render the score and bottles remaining text on the screen. Create functions for the start and end game screens.