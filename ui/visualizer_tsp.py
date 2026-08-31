"""
Visualizador Interativo para o Caixeiro Viajante com Otimização por Colônia de Formigas (ACO-TSP).
Interface completa com animação de formigas, trilhas de feromônio, controles e gráficos em tempo real.
"""
from typing import List, Tuple, Optional, Dict, Any
import pygame
import numpy as np

from core.aco_tsp import AntColonyTSP
from ui.colors import (
    BG_DARK, SURFACE, SURFACE_LIGHT, SURFACE_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    PRIMARY, PRIMARY_HOVER, SUCCESS, WARNING, DANGER,
    GOLD, CYAN, PURPLE, ANT_COLOR, CITY_NODE, CITY_NODE_BORDER
)
from ui.widgets import Button, Slider
from ui.chart_panel import RealtimeChart


class VisualizerTSP:
    def __init__(self, rect: Tuple[int, int, int, int]):
        self.rect = pygame.Rect(rect)
        self.canvas_width = 760
        self.canvas_height = self.rect.height - 20
        self.canvas_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.canvas_width, self.canvas_height)

        self.sidebar_x = self.canvas_rect.right + 15
        self.sidebar_width = self.rect.width - self.canvas_width - 35

        self.aco = AntColonyTSP(n_ants=30, alpha=1.0, beta=3.0, rho=0.1, q=100.0)
        self.generate_initial_cities(n=18)

        self.is_running = False
        self.step_mode = False
        self.speed = 1
        self.anim_progress = 0.0
        self.animate_ants = True
        self.show_pheromones = True
        self.show_all_tours = False

        self.last_iteration_data: Optional[Dict[str, Any]] = None
        self.selected_city_drag: Optional[int] = None

        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 16, bold=True)
        self.font_info = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)
        self.font_bold = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)
        self.font_node = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 11, bold=True)

        self._init_ui()

    def generate_initial_cities(self, n: int = 18):
        """Gera cidades iniciais bem distribuídas no canvas."""
        cities = AntColonyTSP.generate_random_cities(
            n=n,
            width=self.canvas_width,
            height=self.canvas_height,
            margin=50,
            seed=42
        )
        self.aco.set_cities(cities)

    def _init_ui(self):
        """Cria botões, sliders e gráfico na barra lateral."""
        sx = self.sidebar_x
        sw = self.sidebar_width
        y = self.rect.y + 15

        btn_w = (sw - 10) // 2
        self.btn_play = Button(
            (sx, y, btn_w, 36),
            "▶ Executar",
            callback=self.toggle_play,
            bg_color=SUCCESS,
            hover_color=(86, 211, 100)
        )
        self.btn_step = Button(
            (sx + btn_w + 10, y, btn_w, 36),
            "⏭ Passo (+1)",
            callback=self.step_once,
            bg_color=SURFACE_LIGHT
        )
        y += 44

        btn_w3 = (sw - 16) // 3
        self.btn_rand = Button(
            (sx, y, btn_w3, 30),
            "Aleatório",
            callback=lambda: self.reset_cities_random(20),
            font_size=12
        )
        self.btn_circle = Button(
            (sx + btn_w3 + 8, y, btn_w3, 30),
            "Círculo",
            callback=self.reset_cities_circle,
            font_size=12
        )
        self.btn_reset = Button(
            (sx + 2 * (btn_w3 + 8), y, btn_w3, 30),
            "Limpar",
            callback=self.reset_simulation,
            bg_color=(60, 30, 35),
            hover_color=(120, 45, 55),
            font_size=12
        )
        y += 40

        self.slider_alpha = Slider(
            (sx, y, sw, 34),
            "α (Peso Feromônio):",
            0.0, 5.0, self.aco.alpha, step=0.1,
            callback=lambda v: setattr(self.aco, 'alpha', v),
            format_str="{:.1f}"
        )
        y += 40

        self.slider_beta = Slider(
            (sx, y, sw, 34),
            "β (Peso Distância/Heurística):",
            0.5, 8.0, self.aco.beta, step=0.1,
            callback=lambda v: setattr(self.aco, 'beta', v),
            format_str="{:.1f}"
        )
        y += 40

        self.slider_rho = Slider(
            (sx, y, sw, 34),
            "ρ (Taxa de Evaporação):",
            0.01, 0.80, self.aco.rho, step=0.01,
            callback=lambda v: setattr(self.aco, 'rho', v),
            format_str="{:.2f}"
        )
        y += 40

        self.slider_ants = Slider(
            (sx, y, sw, 34),
            "Nº de Formigas:",
            5, 100, float(self.aco.n_ants), step=5,
            callback=lambda v: setattr(self.aco, 'n_ants', int(v)),
            format_str="{:.0f}"
        )
        y += 40

        self.slider_speed = Slider(
            (sx, y, sw, 34),
            "Velocidade (Iterações/Frame):",
            1, 10, float(self.speed), step=1,
            callback=lambda v: setattr(self, 'speed', int(v)),
            format_str="{:.0f}x"
        )
        y += 44

        chart_h = 160
        self.chart = RealtimeChart((sx, y, sw, chart_h))
        y += chart_h + 10

        self.stats_y = y

    def toggle_play(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_play.text = "⏸ Pausar"
            self.btn_play.bg_color = WARNING
        else:
            self.btn_play.text = "▶ Executar"
            self.btn_play.bg_color = SUCCESS

    def step_once(self):
        self.last_iteration_data = self.aco.step_iteration()
        self.chart.update_data(self.aco.metrics.best_history, self.aco.metrics.mean_history)

    def reset_simulation(self):
        self.aco.reset_pheromones()
        self.chart.clear()
        self.last_iteration_data = None
        if self.is_running:
            self.toggle_play()

    def reset_cities_random(self, n: int = 20):
        self.generate_initial_cities(n)
        self.reset_simulation()

    def reset_cities_circle(self, n: int = 20):
        cx = self.canvas_width / 2
        cy = self.canvas_height / 2
        radius = min(cx, cy) - 60
        cities = AntColonyTSP.generate_circular_cities(n, cx, cy, radius)
        self.aco.set_cities(cities)
        self.reset_simulation()

    def handle_event(self, event: pygame.event.Event):
        self.btn_play.handle_event(event)
        self.btn_step.handle_event(event)
        self.btn_rand.handle_event(event)
        self.btn_circle.handle_event(event)
        self.btn_reset.handle_event(event)

        self.slider_alpha.handle_event(event)
        self.slider_beta.handle_event(event)
        self.slider_rho.handle_event(event)
        self.slider_ants.handle_event(event)
        self.slider_speed.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.canvas_rect.collidepoint(mx, my):
                rel_x = mx - self.canvas_rect.x
                rel_y = my - self.canvas_rect.y

                clicked_city = None
                for i, (cx, cy) in enumerate(self.aco.cities):
                    if (rel_x - cx) ** 2 + (rel_y - cy) ** 2 <= 14 ** 2:
                        clicked_city = i
                        break

                if event.button == 1:
                    if clicked_city is not None:
                        self.selected_city_drag = clicked_city
                    else:
                        self.aco.add_city(rel_x, rel_y)
                        self.chart.clear()
                        self.last_iteration_data = None
                elif event.button == 3:
                    if clicked_city is not None:
                        self.aco.remove_city(clicked_city)
                        self.chart.clear()
                        self.last_iteration_data = None

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.selected_city_drag = None

        elif event.type == pygame.MOUSEMOTION and self.selected_city_drag is not None:
            mx, my = event.pos
            rel_x = max(20, min(self.canvas_width - 20, mx - self.canvas_rect.x))
            rel_y = max(20, min(self.canvas_height - 20, my - self.canvas_rect.y))
            self.aco.cities[self.selected_city_drag] = [rel_x, rel_y]
            self.aco.set_cities(self.aco.cities)
            self.chart.clear()

    def update(self):
        """Executa passos do algoritmo quando em execução."""
        if self.is_running and self.aco.n_cities >= 3:
            for _ in range(self.speed):
                self.last_iteration_data = self.aco.step_iteration()
            self.chart.update_data(self.aco.metrics.best_history, self.aco.metrics.mean_history)

        self.anim_progress = (self.anim_progress + 0.03 * self.speed) % 1.0

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (14, 16, 22), self.canvas_rect, border_radius=10)
        pygame.draw.rect(surface, SURFACE_BORDER, self.canvas_rect, width=1, border_radius=10)

        for gx in range(self.canvas_rect.x + 30, self.canvas_rect.right, 40):
            for gy in range(self.canvas_rect.y + 30, self.canvas_rect.bottom, 40):
                pygame.draw.circle(surface, (28, 32, 44), (gx, gy), 1)

        if self.show_pheromones and self.aco.n_cities >= 2:
            self._draw_pheromones(surface)

        if self.aco.global_best_tour and len(self.aco.global_best_tour) >= 2:
            self._draw_best_tour(surface)

        if self.animate_ants and self.last_iteration_data:
            self._draw_animated_ants(surface)

        self._draw_cities(surface)

        tip_text = "Clique com botão esquerdo para adicionar cidade | Botão direito para remover | Arraste para mover"
        tip_surf = self.font_node.render(tip_text, True, TEXT_MUTED)
        surface.blit(tip_surf, (self.canvas_rect.x + 12, self.canvas_rect.bottom - 22))

        self._draw_sidebar(surface)

    def _draw_pheromones(self, surface: pygame.Surface):
        """Renderiza as trilhas de feromônio com brilho e intensidade dinâmica."""
        max_tau = np.max(self.aco.pheromones)
        min_tau = np.min(self.aco.pheromones)
        range_tau = max(1e-6, max_tau - min_tau)

        trail_surf = pygame.Surface((self.canvas_rect.width, self.canvas_rect.height), pygame.SRCALPHA)

        for i in range(self.aco.n_cities):
            for j in range(i + 1, self.aco.n_cities):
                tau = self.aco.pheromones[i, j]
                norm_tau = (tau - min_tau) / range_tau

                if norm_tau > 0.05:
                    alpha = int(norm_tau * 180)
                    thickness = max(1, int(norm_tau * 4))
                    c1 = self.aco.cities[i]
                    c2 = self.aco.cities[j]
                    pygame.draw.line(
                        trail_surf,
                        (88, 166, 255, alpha),
                        (c1[0], c1[1]),
                        (c2[0], c2[1]),
                        thickness
                    )

        surface.blit(trail_surf, self.canvas_rect.topleft)

    def _draw_best_tour(self, surface: pygame.Surface):
        """Desenha a melhor rota global com efeito de brilho e setas direcionais."""
        tour = self.aco.global_best_tour
        pts = [
            (int(self.canvas_rect.x + self.aco.cities[idx][0]),
             int(self.canvas_rect.y + self.aco.cities[idx][1]))
            for idx in tour
        ]

        glow_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surf, (245, 197, 24, 40), pts, 8)
        surface.blit(glow_surf, (0, 0))

        pygame.draw.polygon(surface, GOLD, pts, 3)

    def _draw_animated_ants(self, surface: pygame.Surface):
        """Desenha formigas percorrendo seus caminhos calculados na última iteração."""
        all_tours = self.last_iteration_data.get("all_tours", [])
        if not all_tours:
            return

        sample_tours = all_tours[:15]
        total_legs = self.aco.n_cities

        for tour in sample_tours:
            leg_idx = int(self.anim_progress * total_legs) % total_legs
            sub_progress = (self.anim_progress * total_legs) % 1.0

            u = tour[leg_idx]
            v = tour[(leg_idx + 1) % total_legs]

            pos_u = self.aco.cities[u]
            pos_v = self.aco.cities[v]

            cur_x = self.canvas_rect.x + pos_u[0] + sub_progress * (pos_v[0] - pos_u[0])
            cur_y = self.canvas_rect.y + pos_u[1] + sub_progress * (pos_v[1] - pos_u[1])

            pygame.draw.circle(surface, ANT_COLOR, (int(cur_x), int(cur_y)), 4)
            pygame.draw.circle(surface, (255, 255, 255), (int(cur_x), int(cur_y)), 2)

    def _draw_cities(self, surface: pygame.Surface):
        """Renderiza cada cidade com borda luminosa e identificador."""
        for i, (cx, cy) in enumerate(self.aco.cities):
            screen_x = int(self.canvas_rect.x + cx)
            screen_y = int(self.canvas_rect.y + cy)

            pygame.draw.circle(surface, SURFACE, (screen_x, screen_y), 11)
            pygame.draw.circle(surface, PRIMARY, (screen_x, screen_y), 11, 2)
            pygame.draw.circle(surface, CITY_NODE, (screen_x, screen_y), 5)

            lbl = self.font_node.render(str(i + 1), True, TEXT_PRIMARY)
            surface.blit(lbl, (screen_x + 12, screen_y - 8))

    def _draw_sidebar(self, surface: pygame.Surface):
        """Desenha a barra lateral com controles, estatísticas e gráfico."""
        self.btn_play.draw(surface)
        self.btn_step.draw(surface)
        self.btn_rand.draw(surface)
        self.btn_circle.draw(surface)
        self.btn_reset.draw(surface)

        self.slider_alpha.draw(surface)
        self.slider_beta.draw(surface)
        self.slider_rho.draw(surface)
        self.slider_ants.draw(surface)
        self.slider_speed.draw(surface)

        self.chart.draw(surface)

        card_rect = pygame.Rect(self.sidebar_x, self.stats_y, self.sidebar_width, 100)
        pygame.draw.rect(surface, SURFACE, card_rect, border_radius=8)
        pygame.draw.rect(surface, SURFACE_BORDER, card_rect, width=1, border_radius=8)

        sy = card_rect.y + 10
        sx = card_rect.x + 12

        title_s = self.font_bold.render("Métricas em Tempo Real", True, PRIMARY)
        surface.blit(title_s, (sx, sy))
        sy += 22

        l1_txt = f"Iteração: {self.aco.iteration}  |  Cidades: {self.aco.n_cities}"
        l1_surf = self.font_info.render(l1_txt, True, TEXT_SECONDARY)
        surface.blit(l1_surf, (sx, sy))
        sy += 20

        best_str = f"{self.aco.global_best_length:.2f} px" if self.aco.global_best_tour else "---"
        l2_txt = f"Melhor Distância: {best_str}"
        l2_surf = self.font_bold.render(l2_txt, True, GOLD)
        surface.blit(l2_surf, (sx, sy))
        sy += 20

        if self.last_iteration_data:
            mean_val = np.mean(self.last_iteration_data["all_lengths"])
            l3_txt = f"Média da Rodada: {mean_val:.2f} px"
        else:
            l3_txt = "Média da Rodada: ---"
        l3_surf = self.font_info.render(l3_txt, True, PURPLE)
        surface.blit(l3_surf, (sx, sy))
