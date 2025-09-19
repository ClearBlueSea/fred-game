# FRED: Ocean Cleanup

## 🌊 FRED: Ocean Cleanup - An Educational Simulation Game

**FRED: Ocean Cleanup** is an educational 2D top-down simulation game designed to raise awareness about ocean plastic pollution while teaching players about robotics, environmental science, and physics-based challenges. Players take on the role of piloting FRED (**F**loating **R**obot for **E**liminating **D**ebris), a solar-powered Autonomous Surface Vehicle (ASV), on a crucial mission to collect plastic bottles scattered across the ocean.

The game is built using **Python and the Pygame framework** and is targeted at all ages.

---

## 🚀 Project Overview

The core objective of the game is to navigate FRED from a base station to collect all plastic bottles in the water, aiming for the lowest possible score. The score is a measure of propeller usage, encouraging efficient and thoughtful navigation. FRED's unique control system mimics the differential thrust steering of a real catamaran, providing a challenging and rewarding gameplay experience without traditional "up, down, left, right" steering or reverse.

### Architectural Philosophy

The technical vision for 'FRED: Ocean Cleanup' is founded on three core software engineering principles, ensuring a robust, maintainable, and extensible codebase:

1.  **Modularity**: Each core game system (Physics, Rendering, Audio, UI, State Management) is designed as a distinct, loosely coupled component to allow for independent development and simplified maintenance.
2.  **Data-Driven Design**: Game logic is separated from game data. Critical parameters are externalized into configuration files, allowing designers to tune gameplay without modifying source code.
3.  **Performance by Design**: Architectural decisions prioritize efficiency, utilizing Pygame's optimized `pygame.sprite.Group` for rendering and collision, and `pygame.math.Vector2` for physics calculations.

---

## ✅ Current Status: Phase 1 - Foundation & Core Loop (Completed)

**Phase 1: Foundation & Core Loop** has been successfully completed, establishing the essential technical skeleton of the 'FRED: Ocean Cleanup' game. This phase focused on setting up the project environment, creating the application's entry point, the main game loop, and a rudimentary Finite State Machine (FSM).

### Key Achievements of Phase 1:

*   **Project Setup & Environment**:
    *   A complete, well-organized **project directory structure** has been established.
    *   A **Git repository** has been initialized for version control.
    *   A dedicated **Python virtual environment** (managed by UV) has been created.
    *   The **`pyproject.toml`** file lists `pygame` (v2.x) as a core dependency and configures `Ruff` for linting and formatting, ensuring PEP 8 compliance.
*   **Core Application Loop (`src/game.py`)**:
    *   The central `Game` class has been implemented, responsible for initializing Pygame, creating the main game window (e.g., 800x600), and managing the game clock.
    *   It houses the primary **game loop** which handles events, updates game logic, and renders visuals, calculating `dt` (delta time) for consistent performance.
*   **Global Settings (`src/settings.py`)**:
    *   A centralized `settings.py` module defines essential global constants, including `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS`, and basic color definitions.
*   **Finite State Machine (FSM) (`src/states/`)**:
    *   A robust **FSM architecture** has been implemented, enabling clean transitions between different game screens.
    *   An **abstract `BaseState` class** defines a consistent interface (`startup`, `cleanup`, `handle_event`, `update`, `draw`) for all game states.
    *   **Minimal `MainMenuState`** and **`GameplayState`** classes have been created, inheriting from `BaseState`. These states currently display distinct placeholder content for visual identification.
    *   The game can successfully **transition** from the "Main Menu" to the "Gameplay Screen" and back, controlled by player input (e.g., pressing 'Return' to start, 'Escape' to return).
*   **Graceful Exit**: The application window can be cleanly closed, demonstrating a stable game loop.

### Expected User Experience (After Phase 1)

When running the project, a Pygame window will open, initially displaying a "Main Menu" screen. Pressing a designated key (e.g., `Return`) will transition the display to a "Gameplay Screen" placeholder. Another designated key (e.g., `Escape`) will return to the "Main Menu". The application can be closed at any time via the window's close button.

---

## 🛠️ Technical Stack & Dependencies (Foundation)

The project leverages the following key technologies, with `pygame` at its core:

*   **Core Game Framework**: **`pygame` (v2.x)** - Provides fundamental 2D graphics, audio, and input handling via SDL.
    *   **Underlying SDL Libraries**: SDL 2, SDL_mixer, SDL_image, SDL_ttf are inherently relied upon for Pygame's functionality.
*   **State Management**: Custom **Finite State Machine (FSM)** Class - Ensures scalable application flow.
*   **Code Quality**: **`Ruff`** - For linting and consistent code formatting (PEP 8 compliance).
*   **Environment Management**: **`UV`** - For managing the Python virtual environment and project dependencies.

---

## 📂 Project Structure

The project follows a clear and modular directory hierarchy:

```
fred-game/
├── assets/                 # Stores all game assets (graphics, audio, fonts)
│   ├── graphics/
│   │   ├── player/         # Sprites for FRED
│   │   ├── trash/          # Sprites for trash items
│   │   └── ui/             # UI elements and icons
│   ├── audio/
│   │   ├── music/          # Background music tracks
│   │   └── sfx/            # Sound effects
│   └── fonts/              # Font files (e.g., .ttf)
├── src/                    # Contains all Python source code
│   ├── __main__.py         # Main entry point of the application
│   ├── game.py             # Main Game class and game loop orchestration
│   ├── settings.py         # Global constants and configuration
│   ├── states/             # Package for game state implementations
│   │   ├── __init__.py
│   │   ├── base.py         # Abstract BaseState class
│   │   ├── menu.py         # MainMenuState implementation
│   │   └── gameplay.py     # GameplayState implementation
│   ├── entities/           # (Planned) Classes for game entities (FRED, Trash, etc.)
│   │   ├── __init__.py
│   │   ├── player.py       
│   │   └── trash.py        
│   └── systems/            # (Planned) Game-wide systems (e.g., Camera)
│       ├── __init__.py
│       └── camera.py       
├── pyproject.toml          # Project metadata and Python package dependencies
└── README.md               # This project documentation
```

---

## 🎮 Getting Started

To run the 'FRED: Ocean Cleanup' project, follow these steps:

### Prerequisites

*   **Python 3.x** installed on your system.
*   **`uv`** (recommended for virtual environment and dependency management) or `pip` and `venv`.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ClearBlueSea/fred-ocean-cleanup.git
    cd fred-ocean-cleanup
    ```
2.  **Create and activate a virtual environment** using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate  # On Windows
    ```
3.  **Install dependencies** using `uv`:
    ```bash
    uv sync
    ```
    (This will install `pygame` and other necessary packages defined in `pyproject.toml`).

### Running the Game

1.  **Ensure your virtual environment is active.**
2.  **Run the game** from the project root:
    ```bash
    uv run python -m src
    ```
    Alternatively, if using `pip`/`venv`:
    ```bash
    python -m src
    ```

### Running the development version

```bash
uv run python -m main
```

---

## 🗺️ Development Roadmap (Next Phases)

With Phase 1 complete, the project will move through these subsequent phases:

*   **Phase 2: FRED Prototyping**: Implementing and tuning FRED's `Vector2`-based physics model and differential thrust control system. **In Progress**
*   **Phase 3: World & Interaction**: Introducing collectible trash and basic collision detection.
*   **Phase 4: Camera & Environment**: Developing the scrolling camera and environmental physics like water drag and ocean currents.
*   **Phase 5: UI & State Transitions**: Integrating `pygame-gui` to build out the main menu, HUD, and other UI elements.
*   **Phase 6: Polish (Audio & VFX)**: Adding sound effects, background music, dynamic stereo panning for thrusters, and particle systems.
*   **Phase 7: Content & Balancing**: Finalizing art/sound, designing levels, and extensive playtesting.

---

## 📄 License

This project is licensed under the GNU General Public License. See the `LICENSE` file for details.

---

## 🙏 Acknowledgements

*   Inspired by the critical issue of ocean plastic pollution and innovative robotic solutions.
*   Leverages the fantastic Pygame community and documentation.
