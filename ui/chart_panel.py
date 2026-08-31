"""
Painel de Gráficos em Tempo Real (Chart Panel) para Pygame.
Renderiza curvas de convergência de fitness/distância sem lag.
"""
from typing import List, Tuple, Optional
import pygame
from ui.colors import (
    SURFACE, SURFACE_LIGHT, SURFACE_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    GOLD, PURPLE, CYAN
)


class RealtimeChart:
    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        title: str = "Convergência do Fitness (Distância)"
    ):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.best_data: List[float] = []
        self.mean_data: List[float] = []

        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)
        self.font_axis = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 11)
        self.font_legend = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 11, bold=True)

    def update_data(self, best_history: List[float], mean_history: Optional[List[float]] = None):
        """Atualiza a série temporal do gráfico."""
        self.best_data = best_history
        self.mean_data = mean_history if mean_history is not None else []

    def clear(self):
        """Limpa os dados do gráfico."""
        self.best_data = []
        self.mean_data = []

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, SURFACE, self.rect, border_radius=8)
        pygame.draw.rect(surface, SURFACE_BORDER, self.rect, width=1, border_radius=8)

        title_surf = self.font_title.render(self.title, True, TEXT_PRIMARY)
        surface.blit(title_surf, (self.rect.x + 12, self.rect.y + 10))

        pygame.draw.circle(surface, GOLD, (self.rect.right - 130, self.rect.y + 17), 4)
        leg1 = self.font_legend.render("Melhor", True, TEXT_SECONDARY)
        surface.blit(leg1, (self.rect.right - 120, self.rect.y + 10))

        pygame.draw.circle(surface, PURPLE, (self.rect.right - 65, self.rect.y + 17), 4)
        leg2 = self.font_legend.render("Média", True, TEXT_SECONDARY)
        surface.blit(leg2, (self.rect.right - 55, self.rect.y + 10))

        plot_rect = pygame.Rect(
            self.rect.x + 40,
            self.rect.y + 35,
            self.rect.width - 55,
            self.rect.height - 55
        )
        pygame.draw.rect(surface, (22, 24, 32), plot_rect, border_radius=4)
        pygame.draw.rect(surface, SURFACE_BORDER, plot_rect, width=1, border_radius=4)

        if not self.best_data:
            no_data_surf = self.font_axis.render("Aguardando iterações...", True, TEXT_MUTED)
            surface.blit(no_data_surf, no_data_surf.get_rect(center=plot_rect.center))
            return

        all_vals = list(self.best_data)
        if self.mean_data:
            all_vals.extend(self.mean_data)

        min_val = min(all_vals)
        max_val = max(all_vals)

        if max_val == min_val:
            min_val -= 10.0
            max_val += 10.0
        else:
            padding = (max_val - min_val) * 0.08
            min_val -= padding
            max_val += padding

        for i in range(3):
            ratio = i / 2.0
            gy = int(plot_rect.bottom - ratio * plot_rect.height)
            pygame.draw.line(surface, SURFACE_BORDER, (plot_rect.x, gy), (plot_rect.right, gy), 1)

            val_at_grid = min_val + ratio * (max_val - min_val)
            val_lbl = self.font_axis.render(f"{val_at_grid:.0f}", True, TEXT_MUTED)
            surface.blit(val_lbl, (self.rect.x + 6, gy - 6))

        total_pts = len(self.best_data)
        iter_0 = self.font_axis.render("1", True, TEXT_MUTED)
        iter_end = self.font_axis.render(str(total_pts), True, TEXT_MUTED)
        surface.blit(iter_0, (plot_rect.x, plot_rect.bottom + 4))
        surface.blit(iter_end, (plot_rect.right - iter_end.get_width(), plot_rect.bottom + 4))

        def get_points(data_list: List[float]) -> List[Tuple[int, int]]:
            pts = []
            n = len(data_list)
            for idx, val in enumerate(data_list):
                if n == 1:
                    px = plot_rect.centerx
                else:
                    px = int(plot_rect.x + (idx / (n - 1)) * plot_rect.width)
                
                norm_y = (val - min_val) / (max_val - min_val)
                py = int(plot_rect.bottom - norm_y * plot_rect.height)
                py = max(plot_rect.top, min(plot_rect.bottom, py))
                pts.append((px, py))
            return pts

        if len(self.mean_data) >= 2:
            mean_pts = get_points(self.mean_data)
            pygame.draw.lines(surface, PURPLE, False, mean_pts, 2)

        if len(self.best_data) >= 2:
            best_pts = get_points(self.best_data)
            pygame.draw.lines(surface, GOLD, False, best_pts, 2)
            pygame.draw.circle(surface, GOLD, best_pts[-1], 4)
        elif len(self.best_data) == 1:
            best_pts = get_points(self.best_data)
            pygame.draw.circle(surface, GOLD, best_pts[0], 4)
