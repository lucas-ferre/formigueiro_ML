"""
Testes de Interface e Inicialização Headless com Pygame.
"""
import os
import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from ui.colors import PRIMARY, SUCCESS
from ui.widgets import Button, Slider, SegmentedControl
from ui.chart_panel import RealtimeChart
from ui.visualizer_tsp import VisualizerTSP
from ui.visualizer_grid import VisualizerGrid


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_ui_button_and_slider():
    surface = pygame.Surface((800, 600))

    clicked = False
    def on_click():
        nonlocal clicked
        clicked = True

    btn = Button((10, 10, 100, 30), "Test", callback=on_click)
    btn.draw(surface)

    ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (20, 20), "button": 1})
    btn.handle_event(ev_down)
    ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (20, 20), "button": 1})
    btn.handle_event(ev_up)
    assert clicked is True

    val_changed = 0.0
    def on_slide(v):
        nonlocal val_changed
        val_changed = v

    slider = Slider((10, 50, 200, 30), "Alpha", 0.0, 5.0, 1.0, callback=on_slide)
    slider.draw(surface)
    slider.set_value(3.5)
    assert slider.value == 3.5


def test_realtime_chart():
    surface = pygame.Surface((400, 300))
    chart = RealtimeChart((0, 0, 380, 200), "Teste")
    chart.draw(surface)

    best = [500.0, 420.0, 380.0, 310.0]
    mean = [520.0, 480.0, 430.0, 390.0]
    chart.update_data(best, mean)
    chart.draw(surface)

    assert len(chart.best_data) == 4


def test_visualizer_tsp_lifecycle():
    surface = pygame.Surface((1140, 760))
    vis_tsp = VisualizerTSP((0, 55, 1140, 705))
    
    vis_tsp.draw(surface)

    vis_tsp.step_once()
    assert vis_tsp.aco.iteration == 1
    assert vis_tsp.last_iteration_data is not None

    vis_tsp.update()
    vis_tsp.draw(surface)


def test_visualizer_grid_lifecycle():
    surface = pygame.Surface((1140, 760))
    vis_grid = VisualizerGrid((0, 55, 1140, 705))

    vis_grid.draw(surface)

    vis_grid.update()
    assert len(vis_grid.sim.ants) > 0

    vis_grid.draw(surface)
