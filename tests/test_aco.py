"""
Testes Unitários para o Algoritmo ACO e Rastreamento de Métricas.
"""
import pytest
import numpy as np
from core.aco_tsp import AntColonyTSP
from core.metrics import MetricsTracker
from core.grid_foraging import GridForagingSim, AntAgent


def test_metrics_tracker():
    tracker = MetricsTracker()
    assert tracker.all_time_best == float('inf')

    tours = [100.0, 120.0, 150.0, 95.0]
    res1 = tracker.record_iteration(1, tours, 95.0)
    assert tracker.all_time_best == 95.0
    assert tracker.all_time_best_iter == 1
    assert len(tracker.iterations) == 1

    tours2 = [90.0, 92.0, 85.0]
    res2 = tracker.record_iteration(2, tours2, 85.0)
    assert tracker.all_time_best == 85.0
    assert tracker.all_time_best_iter == 2
    assert len(tracker.best_history) == 2


def test_aco_tsp_initialization():
    cities = np.array([
        [0.0, 0.0],
        [0.0, 10.0],
        [10.0, 10.0],
        [10.0, 0.0]
    ])
    aco = AntColonyTSP(cities=cities, n_ants=10, alpha=1.0, beta=2.0, rho=0.1)

    assert aco.n_cities == 4
    assert aco.distances.shape == (4, 4)
    assert aco.pheromones.shape == (4, 4)
    assert np.isclose(aco.distances[0, 1], 10.0)
    assert np.isclose(aco.distances[0, 2], np.sqrt(200.0))
    assert aco.pheromones[0, 0] == 0.0
    assert aco.pheromones[1, 1] == 0.0


def test_aco_tsp_tour_length():
    cities = np.array([
        [0.0, 0.0],
        [0.0, 10.0],
        [10.0, 10.0],
        [10.0, 0.0]
    ])
    aco = AntColonyTSP(cities=cities)
    tour = [0, 1, 2, 3]
    length = aco.compute_tour_length(tour)
    assert np.isclose(length, 40.0)


def test_aco_tsp_step_iteration():
    cities = AntColonyTSP.generate_circular_cities(n=10, radius=50)
    aco = AntColonyTSP(cities=cities, n_ants=15, alpha=1.0, beta=3.0, rho=0.1)

    initial_tau = aco.pheromones.copy()
    step_result = aco.step_iteration()

    assert step_result["iteration"] == 1
    assert len(step_result["all_tours"]) == 15
    assert len(step_result["all_lengths"]) == 15
    assert step_result["global_best_length"] > 0
    assert len(step_result["global_best_tour"]) == 10
    assert not np.array_equal(initial_tau, aco.pheromones)


def test_aco_dynamic_city_addition_and_removal():
    cities = np.array([[0, 0], [10, 0], [10, 10]])
    aco = AntColonyTSP(cities=cities)
    assert aco.n_cities == 3

    aco.add_city(0, 10)
    assert aco.n_cities == 4
    assert aco.distances.shape == (4, 4)

    aco.remove_city(0)
    assert aco.n_cities == 3
    assert aco.distances.shape == (3, 3)


def test_grid_foraging_simulation():
    sim = GridForagingSim(width=400, height=300, grid_scale=4, n_ants=20)
    assert len(sim.ants) == 20
    assert sim.pheromone_home.shape == (75, 100)
    assert sim.pheromone_food.shape == (75, 100)

    for _ in range(10):
        sim.step()

    assert any(ant.steps_since_nest > 0 for ant in sim.ants)
    assert np.sum(sim.pheromone_home) > 0

    sim.add_obstacle_rect(100, 100, 150, 150)
    assert sim.is_obstacle_at(120, 120) is True
    assert sim.is_obstacle_at(10, 10) is False

    sim.clear_obstacles()
    assert sim.is_obstacle_at(120, 120) is False
