"""
Implementação do Algoritmo de Otimização por Colônia de Formigas (ACO)
para o Problema do Caixeiro Viajante (TSP - Traveling Salesperson Problem).
"""
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from core.metrics import MetricsTracker


class AntColonyTSP:
    def __init__(
        self,
        cities: Optional[np.ndarray] = None,
        n_ants: int = 30,
        alpha: float = 1.0,
        beta: float = 3.0,
        rho: float = 0.1,
        q: float = 100.0,
        elitist_weight: float = 2.0,
        tau_min: float = 0.01,
        tau_max: float = 10.0
    ):
        self.n_ants = n_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.elitist_weight = elitist_weight
        self.tau_min = tau_min
        self.tau_max = tau_max

        self.cities: np.ndarray = np.empty((0, 2), dtype=float)
        self.n_cities: int = 0
        self.distances: np.ndarray = np.empty((0, 0), dtype=float)
        self.heuristics: np.ndarray = np.empty((0, 0), dtype=float)
        self.pheromones: np.ndarray = np.empty((0, 0), dtype=float)

        self.global_best_tour: Optional[List[int]] = None
        self.global_best_length: float = float('inf')
        self.iteration: int = 0

        self.metrics = MetricsTracker()

        if cities is not None and len(cities) > 0:
            self.set_cities(cities)

    def set_cities(self, cities: np.ndarray):
        """Define as coordenadas das cidades e reinicializa matrizes."""
        self.cities = np.array(cities, dtype=float)
        self.n_cities = len(self.cities)
        self.global_best_tour = None
        self.global_best_length = float('inf')
        self.iteration = 0
        self.metrics.reset()

        if self.n_cities < 2:
            self.distances = np.empty((self.n_cities, self.n_cities), dtype=float)
            self.heuristics = np.empty((self.n_cities, self.n_cities), dtype=float)
            self.pheromones = np.empty((self.n_cities, self.n_cities), dtype=float)
            return

        diff = self.cities[:, np.newaxis, :] - self.cities[np.newaxis, :, :]
        self.distances = np.sqrt(np.sum(diff ** 2, axis=-1))

        epsilon = 1e-10
        with np.errstate(divide='ignore'):
            self.heuristics = 1.0 / (self.distances + epsilon)
        np.fill_diagonal(self.heuristics, 0.0)

        approx_length = self._estimate_nn_tour_length()
        initial_tau = (self.n_ants / (approx_length + epsilon)) if approx_length > 0 else 1.0
        initial_tau = max(self.tau_min, min(self.tau_max, initial_tau))
        
        self.pheromones = np.full((self.n_cities, self.n_cities), initial_tau, dtype=float)
        np.fill_diagonal(self.pheromones, 0.0)

    def _estimate_nn_tour_length(self) -> float:
        """Estima o comprimento de rota com algoritmo guloso (Nearest Neighbor)."""
        if self.n_cities < 2:
            return 1.0
        visited = [0]
        current = 0
        total_dist = 0.0
        unvisited = set(range(1, self.n_cities))

        while unvisited:
            next_city = min(unvisited, key=lambda c: self.distances[current][c])
            total_dist += self.distances[current][next_city]
            visited.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        total_dist += self.distances[current][visited[0]]
        return total_dist

    def reset_pheromones(self):
        """Reinicia apenas a matriz de feromônios e o histórico de busca."""
        if self.n_cities >= 2:
            initial_tau = 1.0
            self.pheromones = np.full((self.n_cities, self.n_cities), initial_tau, dtype=float)
            np.fill_diagonal(self.pheromones, 0.0)
            self.global_best_tour = None
            self.global_best_length = float('inf')
            self.iteration = 0
            self.metrics.reset()

    def add_city(self, x: float, y: float):
        """Adiciona uma nova cidade mantendo o estado de execução de forma consistente."""
        new_city = np.array([[x, y]], dtype=float)
        if self.n_cities == 0:
            self.set_cities(new_city)
        else:
            updated_cities = np.vstack([self.cities, new_city])
            self.set_cities(updated_cities)

    def remove_city(self, index: int):
        """Remove a cidade pelo índice especificado."""
        if 0 <= index < self.n_cities and self.n_cities > 1:
            updated_cities = np.delete(self.cities, index, axis=0)
            self.set_cities(updated_cities)

    def compute_tour_length(self, tour: List[int]) -> float:
        """Calcula a distância total de um tour fechado."""
        if len(tour) < 2:
            return 0.0
        length = 0.0
        for i in range(len(tour)):
            u = tour[i]
            v = tour[(i + 1) % len(tour)]
            length += self.distances[u][v]
        return length

    def _build_ant_tour(self, start_city: int) -> Tuple[List[int], float]:
        """
        Constrói o tour de uma única formiga utilizando a regra de transição probabilística.
        """
        tour = [start_city]
        visited = set(tour)
        current = start_city

        for _ in range(self.n_cities - 1):
            unvisited_list = [c for c in range(self.n_cities) if c not in visited]
            
            tau_vals = self.pheromones[current, unvisited_list] ** self.alpha
            eta_vals = self.heuristics[current, unvisited_list] ** self.beta
            probs = tau_vals * eta_vals
            prob_sum = np.sum(probs)

            if prob_sum > 0 and not np.isnan(prob_sum):
                probs = probs / prob_sum
                next_city = np.random.choice(unvisited_list, p=probs)
            else:
                next_city = np.random.choice(unvisited_list)

            tour.append(next_city)
            visited.add(next_city)
            current = next_city

        tour_length = self.compute_tour_length(tour)
        return tour, tour_length

    def step_iteration(self) -> Dict[str, Any]:
        """
        Executa uma iteração completa do ACO:
        1. Todas as formigas constroem seus caminhos.
        2. Avaliação dos caminhos e atualização do melhor global.
        3. Evaporação de feromônio em todas as arestas.
        4. Depósito de novos feromônios (com bônus elitista).
        5. Atualização de telemetria e métricas.
        """
        if self.n_cities < 3:
            return {
                "iteration": self.iteration,
                "all_tours": [],
                "all_lengths": [],
                "iter_best_tour": [],
                "iter_best_length": 0.0,
                "global_best_tour": [],
                "global_best_length": 0.0,
                "pheromones": self.pheromones
            }

        self.iteration += 1
        all_tours: List[List[int]] = []
        all_lengths: List[float] = []

        start_cities = np.random.randint(0, self.n_cities, size=self.n_ants)

        iter_best_tour: Optional[List[int]] = None
        iter_best_length: float = float('inf')

        for start_node in start_cities:
            tour, length = self._build_ant_tour(int(start_node))
            all_tours.append(tour)
            all_lengths.append(length)

            if length < iter_best_length:
                iter_best_length = length
                iter_best_tour = tour

            if length < self.global_best_length:
                self.global_best_length = length
                self.global_best_tour = tour.copy()

        self.pheromones *= (1.0 - self.rho)

        deposit_matrix = np.zeros_like(self.pheromones)
        for tour, length in zip(all_tours, all_lengths):
            if length > 0:
                delta = self.q / length
                for i in range(len(tour)):
                    u = tour[i]
                    v = tour[(i + 1) % len(tour)]
                    deposit_matrix[u, v] += delta
                    deposit_matrix[v, u] += delta

        if self.global_best_tour is not None and self.global_best_length > 0:
            elitist_delta = self.elitist_weight * (self.q / self.global_best_length)
            for i in range(len(self.global_best_tour)):
                u = self.global_best_tour[i]
                v = self.global_best_tour[(i + 1) % len(self.global_best_tour)]
                deposit_matrix[u, v] += elitist_delta
                deposit_matrix[v, u] += elitist_delta

        self.pheromones += deposit_matrix
        self.pheromones = np.clip(self.pheromones, self.tau_min, self.tau_max)
        np.fill_diagonal(self.pheromones, 0.0)

        metric_info = self.metrics.record_iteration(
            iteration=self.iteration,
            tour_lengths=all_lengths,
            global_best=self.global_best_length,
            pheromone_matrix=self.pheromones
        )

        return {
            "iteration": self.iteration,
            "all_tours": all_tours,
            "all_lengths": all_lengths,
            "iter_best_tour": iter_best_tour,
            "iter_best_length": iter_best_length,
            "global_best_tour": self.global_best_tour,
            "global_best_length": self.global_best_length,
            "pheromones": self.pheromones,
            "metrics": metric_info
        }

    @staticmethod
    def generate_random_cities(
        n: int,
        width: float = 600,
        height: float = 500,
        margin: float = 40,
        seed: Optional[int] = None
    ) -> np.ndarray:
        """Gera coordenadas 2D aleatórias dentro de uma área delimitada."""
        if seed is not None:
            np.random.seed(seed)
        xs = np.random.uniform(margin, width - margin, size=n)
        ys = np.random.uniform(margin, height - margin, size=n)
        return np.column_stack((xs, ys))

    @staticmethod
    def generate_circular_cities(
        n: int,
        center_x: float = 300,
        center_y: float = 250,
        radius: float = 180
    ) -> np.ndarray:
        """Gera cidades dispostas em um círculo (ótimo conhecido trivial para teste visual)."""
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        xs = center_x + radius * np.cos(angles)
        ys = center_y + radius * np.sin(angles)
        return np.column_stack((xs, ys))
