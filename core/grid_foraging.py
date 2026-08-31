"""
Simulação Contínua de Forrageamento de Formigas em Grade 2D (Grid Foraging Simulation).
Implementa comunicação indireta estigmergica (estigmergia) com feromônios de ida e volta,
desvio de obstáculos e coleta de recursos.
"""
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


class AntAgent:
    SEARCHING = 0
    RETURNING = 1

    def __init__(self, x: float, y: float, angle: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.state = AntAgent.SEARCHING
        self.has_food = False
        self.steps_since_nest = 0
        self.steps_since_food = 0
        self.speed = 3.2
        self.sensor_angle = np.radians(35.0)
        self.sensor_dist = 18.0
        self.max_steps = 1500


class GridForagingSim:
    def __init__(
        self,
        width: int = 700,
        height: int = 600,
        grid_scale: int = 4,
        n_ants: int = 200,
        evaporation_rate: float = 0.008,
        diffusion_rate: float = 0.05
    ):
        self.width = width
        self.height = height
        self.grid_scale = grid_scale
        self.cols = width // grid_scale
        self.rows = height // grid_scale
        self.n_ants = n_ants
        self.evaporation_rate = evaporation_rate
        self.diffusion_rate = diffusion_rate

        self.pheromone_home = np.zeros((self.rows, self.cols), dtype=np.float32)
        self.pheromone_food = np.zeros((self.rows, self.cols), dtype=np.float32)

        self.obstacles = np.zeros((self.rows, self.cols), dtype=bool)

        self.nest_pos = (width * 0.2, height * 0.5)
        self.nest_radius = 22.0

        self.food_sources: List[Dict[str, Any]] = [
            {"x": width * 0.8, "y": height * 0.3, "radius": 24.0, "amount": 1000},
            {"x": width * 0.75, "y": height * 0.75, "radius": 20.0, "amount": 800}
        ]

        self.total_food_collected = 0
        self.ants: List[AntAgent] = []
        self.init_ants()

    def init_ants(self):
        """Inicializa a população de formigas saindo do ninho."""
        self.ants = []
        for _ in range(self.n_ants):
            angle = np.random.uniform(0, 2 * np.pi)
            ant = AntAgent(self.nest_pos[0], self.nest_pos[1], angle)
            self.ants.append(ant)

    def set_ant_count(self, count: int):
        """Ajusta dinamicamente a contagem de formigas."""
        self.n_ants = count
        if len(self.ants) < count:
            for _ in range(count - len(self.ants)):
                angle = np.random.uniform(0, 2 * np.pi)
                self.ants.append(AntAgent(self.nest_pos[0], self.nest_pos[1], angle))
        elif len(self.ants) > count:
            self.ants = self.ants[:count]

    def add_obstacle_rect(self, x0: int, y0: int, x1: int, y1: int):
        """Adiciona obstáculo retangular."""
        c0 = max(0, min(self.cols - 1, x0 // self.grid_scale))
        c1 = max(0, min(self.cols - 1, x1 // self.grid_scale))
        r0 = max(0, min(self.rows - 1, y0 // self.grid_scale))
        r1 = max(0, min(self.rows - 1, y1 // self.grid_scale))
        
        min_c, max_c = min(c0, c1), max(c0, c1)
        min_r, max_r = min(r0, r1), max(r0, r1)
        self.obstacles[min_r:max_r + 1, min_c:max_c + 1] = True

    def clear_obstacles(self):
        """Remove todos os obstáculos da grade."""
        self.obstacles.fill(False)

    def add_food_source(self, x: float, y: float, radius: float = 22.0, amount: int = 1000):
        """Adiciona uma nova fonte de comida."""
        self.food_sources.append({
            "x": float(x),
            "y": float(y),
            "radius": float(radius),
            "amount": amount
        })

    def set_nest_pos(self, x: float, y: float):
        """Altera a posição do ninho."""
        self.nest_pos = (float(x), float(y))

    def _sample_pheromone(self, grid: np.ndarray, x: float, y: float) -> float:
        """Lê a intensidade do feromônio nas coordenadas contínuas (x, y)."""
        c = int(x // self.grid_scale)
        r = int(y // self.grid_scale)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            if self.obstacles[r, c]:
                return -1.0
            return float(grid[r, c])
        return -1.0

    def _deposit_pheromone(self, grid: np.ndarray, x: float, y: float, amount: float):
        """Deposita feromônio no grid contínuo."""
        c = int(x // self.grid_scale)
        r = int(y // self.grid_scale)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            if not self.obstacles[r, c]:
                grid[r, c] = min(150.0, grid[r, c] + amount)

    def is_obstacle_at(self, x: float, y: float) -> bool:
        """Verifica se há obstáculo nas coordenadas (x, y)."""
        c = int(x // self.grid_scale)
        r = int(y // self.grid_scale)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return bool(self.obstacles[r, c])
        return True

    def step(self):
        """
        Executa um passo de tempo da simulação:
        1. Atualiza movimento e sensores de todas as formigas.
        2. Aplica depósito de feromônios.
        3. Realiza evaporação e difusão dos campos de feromônio.
        """
        nest_x, nest_y = self.nest_pos

        for ant in self.ants:
            target_grid = self.pheromone_food if ant.state == AntAgent.SEARCHING else self.pheromone_home

            left_angle = ant.angle - ant.sensor_angle
            right_angle = ant.angle + ant.sensor_angle

            lx = ant.x + np.cos(left_angle) * ant.sensor_dist
            ly = ant.y + np.sin(left_angle) * ant.sensor_dist

            cx = ant.x + np.cos(ant.angle) * ant.sensor_dist
            cy = ant.y + np.sin(ant.angle) * ant.sensor_dist

            rx = ant.x + np.cos(right_angle) * ant.sensor_dist
            ry = ant.y + np.sin(right_angle) * ant.sensor_dist

            s_left = self._sample_pheromone(target_grid, lx, ly)
            s_center = self._sample_pheromone(target_grid, cx, cy)
            s_right = self._sample_pheromone(target_grid, rx, ry)

            steer = np.random.uniform(-0.15, 0.15)

            if s_center > s_left and s_center > s_right and s_center > 0.05:
                pass
            elif s_left > s_right and s_left > 0.05:
                steer -= 0.35
            elif s_right > s_left and s_right > 0.05:
                steer += 0.35

            if ant.state == AntAgent.SEARCHING:
                for food in self.food_sources:
                    if food["amount"] > 0:
                        df_sq = (ant.x - food["x"]) ** 2 + (ant.y - food["y"]) ** 2
                        if df_sq < (food["radius"] + 35.0) ** 2:
                            target_angle = np.arctan2(food["y"] - ant.y, food["x"] - ant.x)
                            steer = 0.5 * (target_angle - ant.angle)
                            break
            else:
                dn_sq = (ant.x - nest_x) ** 2 + (ant.y - nest_y) ** 2
                if dn_sq < (self.nest_radius + 60.0) ** 2:
                    target_angle = np.arctan2(nest_y - ant.y, nest_x - ant.x)
                    steer = 0.5 * (target_angle - ant.angle)

            ant.angle += steer

            next_x = ant.x + np.cos(ant.angle) * ant.speed
            next_y = ant.y + np.sin(ant.angle) * ant.speed

            if (next_x < 10 or next_x > self.width - 10 or
                next_y < 10 or next_y > self.height - 10 or
                self.is_obstacle_at(next_x, next_y)):
                ant.angle += np.random.uniform(np.pi * 0.6, np.pi * 1.4)
            else:
                ant.x = next_x
                ant.y = next_y

            if ant.state == AntAgent.SEARCHING:
                ant.steps_since_nest += 1
                deposit_intensity = max(0.2, 5.0 * (1.0 - ant.steps_since_nest / ant.max_steps))
                self._deposit_pheromone(self.pheromone_home, ant.x, ant.y, deposit_intensity)

                for food in self.food_sources:
                    if food["amount"] > 0:
                        dist_sq = (ant.x - food["x"]) ** 2 + (ant.y - food["y"]) ** 2
                        if dist_sq <= food["radius"] ** 2:
                            food["amount"] -= 1
                            ant.has_food = True
                            ant.state = AntAgent.RETURNING
                            ant.steps_since_food = 0
                            ant.angle += np.pi
                            break

                if ant.steps_since_nest > ant.max_steps:
                    ant.x, ant.y = nest_x, nest_y
                    ant.steps_since_nest = 0
                    ant.angle = np.random.uniform(0, 2 * np.pi)

            else:
                ant.steps_since_food += 1
                deposit_intensity = max(0.4, 8.0 * (1.0 - ant.steps_since_food / ant.max_steps))
                self._deposit_pheromone(self.pheromone_food, ant.x, ant.y, deposit_intensity)

                dist_nest_sq = (ant.x - nest_x) ** 2 + (ant.y - nest_y) ** 2
                if dist_nest_sq <= self.nest_radius ** 2:
                    ant.has_food = False
                    ant.state = AntAgent.SEARCHING
                    ant.steps_since_nest = 0
                    self.total_food_collected += 1
                    ant.angle += np.pi

        self._diffuse_and_evaporate(self.pheromone_home)
        self._diffuse_and_evaporate(self.pheromone_food)

    def _diffuse_and_evaporate(self, grid: np.ndarray):
        """Aplica evaporação e leve difusão espacial para suavizar trilhas."""
        grid *= (1.0 - self.evaporation_rate)

        if self.diffusion_rate > 0:
            diff = (
                np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
                np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1)
            ) * 0.25
            grid[...] = (1.0 - self.diffusion_rate) * grid + self.diffusion_rate * diff

        grid[self.obstacles] = 0.0
        grid[grid < 0.02] = 0.0
