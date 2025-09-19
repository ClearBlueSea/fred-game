.PHONY: test test-verbose test-watch

test:
		SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest --cov --cov-report=term-missing

test-verbose:
		SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest -v --cov --cov-report=term-missing

test-watch:
		SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest-watch -- --cov
