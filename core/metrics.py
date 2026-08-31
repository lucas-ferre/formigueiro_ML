"""
Módulo de Métricas e Telemetria para Algoritmos ACO.
Registra e fornece dados estatísticos de convergência e diversidade.
"""
from typing import List, Dict, Any, Optional
import numpy as np


class MetricsTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reinicia todas as métricas gravadas."""
        self.iterations: List[int] = []
        self.best_history: List[float] = []
        self.mean_history: List[float] = []
        self.worst_history: List[float] = []
        self.std_history: List[float] = []
        self.pheromone_max: List[float] = []
        self.pheromone_mean: List[float] = []
        self.all_time_best: float = float('inf')
        self.all_time_best_iter: int = 0
        self.start_time: Optional[float] = None

    def record_iteration(
        self,
        iteration: int,
        tour_lengths: List[float],
        global_best: float,
        pheromone_matrix: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Registra as métricas de uma iteração completa de formigas.
        """
        lengths = np.array(tour_lengths, dtype=float)
        iter_best = float(np.min(lengths))
        iter_mean = float(np.mean(lengths))
        iter_worst = float(np.max(lengths))
        iter_std = float(np.std(lengths))

        if global_best < self.all_time_best:
            self.all_time_best = global_best
            self.all_time_best_iter = iteration

        self.iterations.append(iteration)
        self.best_history.append(global_best)
        self.mean_history.append(iter_mean)
        self.worst_history.append(iter_worst)
        self.std_history.append(iter_std)

        if pheromone_matrix is not None and pheromone_matrix.size > 0:
            self.pheromone_max.append(float(np.max(pheromone_matrix)))
            self.pheromone_mean.append(float(np.mean(pheromone_matrix)))
        else:
            self.pheromone_max.append(0.0)
            self.pheromone_mean.append(0.0)

        return {
            "iteration": iteration,
            "iter_best": iter_best,
            "iter_mean": iter_mean,
            "global_best": global_best,
            "diversity_std": iter_std
        }

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos melhores resultados obtidos."""
        total_iters = len(self.iterations)
        if total_iters == 0:
            return {
                "total_iterations": 0,
                "best_distance": None,
                "best_iteration": None,
                "current_mean": None
            }
        return {
            "total_iterations": total_iters,
            "best_distance": self.all_time_best,
            "best_iteration": self.all_time_best_iter,
            "current_mean": self.mean_history[-1] if self.mean_history else None,
            "diversity_std": self.std_history[-1] if self.std_history else None
        }
