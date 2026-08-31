"""
Visualizador Interativo para Simulação de Forrageamento em Grade 2D (Grid Foraging Sim).
Renderiza trilhas de feromônios, obstáculos desenháveis pelo usuário, formigas animadas e fontes de alimento.
"""
from typing import Tuple, Optional, Dict, Any
import pygame
import numpy as np

from core.grid_foraging import GridForagingSim, AntAgent
from ui.colors import (
    SURFACE, SURFACE_LIGHT, SURFACE_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    PRIMARY, SUCCESS, WARNING, DANGER, GOLD,
    NEST_COLOR, FOOD_COLOR, OBSTACLE_COLOR, OBSTACLE_BORDER,
    ANT_COLOR, ANT_FOOD_COLOR
)
from ui.widgets import Button, Slider


class VisualizerGrid:
    TOOL_DRAW_WALL = 0
    TOOL_ERASE_WALL = 1
    TOOL_PLACE_FOOD = 2
    TOOL_MOVE_NEST = 3

    def __init__(self, rect: Tuple[int, int, int, int]):
        self.rect = pygame.Rect(rect)
        self.canvas_width = 760
        self.canvas_height = self.rect.height - 20
        self.canvas_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.canvas_width, self.canvas_height)

        self.sidebar_x = self.canvas_rect.right + 15
        self.sidebar_width = self.rect.width - self.canvas_width - 35

        self.sim = GridForagingSim(
            width=self.canvas_width,
            height=self.canvas_height,
            grid_scale=4,
            n_ants=220,
            evaporation_rate=0.008,
            diffusion_rate=0.04
        )

        self.is_running = True
        self.active_tool = VisualizerGrid.TOOL_DRAW_WALL
        self.brush_size = 2
        self.is_mouse_drawing = False

        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 16, bold=True)
        self.font_info = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)
        self.font_bold = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)
        self.font_node = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 11, bold=True)

        self._init_default_map()
        self._init_ui()

    def _init_default_map(self):
        """Adiciona uma barreira central clássica para demonstrar otimização de caminho."""
        cx = self.canvas_width // 2
        cy = self.canvas_height // 2
        self.sim.add_obstacle_rect(cx - 15, cy - 140, cx + 15, cy + 140)

    def _init_ui(self):
        """Inicializa controles da barra lateral."""
        sx = self.sidebar_x
        sw = self.sidebar_width
        y = self.rect.y + 15

        btn_w = (sw - 10) // 2
        self.btn_play = Button(
            (sx, y, btn_w, 36),
            "⏸ Pausar",
            callback=self.toggle_play,
            bg_color=WARNING,
            hover_color=(235, 175, 45)
        )
        self.btn_reset = Button(
            (sx + btn_w + 10, y, btn_w, 36),
            "Resetar",
            callback=self.reset_sim,
            bg_color=SURFACE_LIGHT
        )
        y += 44

        btn_w4 = (sw - 18) // 4
        self.btn_tool_wall = Button(
            (sx, y, btn_w4, 30),
            "Parede",
            callback=lambda: self.set_tool(VisualizerGrid.TOOL_DRAW_WALL),
            font_size=11,
            is_toggle=True,
            toggled=True
        )
        self.btn_tool_erase = Button(
            (sx + btn_w4 + 6, y, btn_w4, 30),
            "Borracha",
            callback=lambda: self.set_tool(VisualizerGrid.TOOL_ERASE_WALL),
            font_size=11,
            is_toggle=True
        )
        self.btn_tool_food = Button(
            (sx + 2 * (btn_w4 + 6), y, btn_w4, 30),
            "+ Comida",
            callback=lambda: self.set_tool(VisualizerGrid.TOOL_PLACE_FOOD),
            font_size=11,
            is_toggle=True
        )
        self.btn_tool_nest = Button(
            (sx + 3 * (btn_w4 + 6), y, btn_w4, 30),
            "Ninho",
            callback=lambda: self.set_tool(VisualizerGrid.TOOL_MOVE_NEST),
            font_size=11,
            is_toggle=True
        )
        y += 38

        btn_w3 = (sw - 16) // 3
        self.btn_preset_barrier = Button(
            (sx, y, btn_w3, 28),
            "Barreira",
            callback=self.preset_barrier,
            font_size=11
        )
        self.btn_preset_maze = Button(
            (sx + btn_w3 + 8, y, btn_w3, 28),
            "Labirinto",
            callback=self.preset_maze,
            font_size=11
        )
        self.btn_clear_walls = Button(
            (sx + 2 * (btn_w3 + 8), y, btn_w3, 28),
            "Sem Muros",
            callback=self.clear_walls,
            font_size=11
        )
        y += 38

        self.slider_ants = Slider(
            (sx, y, sw, 34),
            "População de Formigas:",
            30, 450, float(self.sim.n_ants), step=10,
            callback=lambda v: self.sim.set_ant_count(int(v)),
            format_str="{:.0f}"
        )
        y += 40

        self.slider_evap = Slider(
            (sx, y, sw, 34),
            "Taxa de Evaporação:",
            0.002, 0.030, self.sim.evaporation_rate, step=0.002,
            callback=lambda v: setattr(self.sim, 'evaporation_rate', v),
            format_str="{:.3f}"
        )
        y += 40

        self.slider_diff = Slider(
            (sx, y, sw, 34),
            "Difusão do Feromônio:",
            0.00, 0.12, self.sim.diffusion_rate, step=0.01,
            callback=lambda v: setattr(self.sim, 'diffusion_rate', v),
            format_str="{:.2f}"
        )
        y += 44

        self.stats_y = y

    def set_tool(self, tool_id: int):
        self.active_tool = tool_id
        self.btn_tool_wall.toggled = (tool_id == VisualizerGrid.TOOL_DRAW_WALL)
        self.btn_tool_erase.toggled = (tool_id == VisualizerGrid.TOOL_ERASE_WALL)
        self.btn_tool_food.toggled = (tool_id == VisualizerGrid.TOOL_PLACE_FOOD)
        self.btn_tool_nest.toggled = (tool_id == VisualizerGrid.TOOL_MOVE_NEST)

    def toggle_play(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_play.text = "⏸ Pausar"
            self.btn_play.bg_color = WARNING
        else:
            self.btn_play.text = "▶ Executar"
            self.btn_play.bg_color = SUCCESS

    def reset_sim(self):
        self.sim.pheromone_home.fill(0.0)
        self.sim.pheromone_food.fill(0.0)
        self.sim.total_food_collected = 0
        self.sim.init_ants()
        for f in self.sim.food_sources:
            f["amount"] = 1000

    def clear_walls(self):
        self.sim.clear_obstacles()
        self.sim.pheromone_home.fill(0.0)
        self.sim.pheromone_food.fill(0.0)

    def preset_barrier(self):
        self.clear_walls()
        self._init_default_map()

    def preset_maze(self):
        self.clear_walls()
        w, h = self.canvas_width, self.canvas_height
        self.sim.add_obstacle_rect(int(w * 0.35), 0, int(w * 0.38), int(h * 0.65))
        self.sim.add_obstacle_rect(int(w * 0.60), int(h * 0.35), int(w * 0.63), h)

    def _apply_brush(self, mx: int, my: int, erase: bool = False):
        rel_x = mx - self.canvas_rect.x
        rel_y = my - self.canvas_rect.y
        scale = self.sim.grid_scale
        c = int(rel_x // scale)
        r = int(rel_y // scale)
        bs = self.brush_size

        r_min = max(0, r - bs)
        r_max = min(self.sim.rows - 1, r + bs)
        c_min = max(0, c - bs)
        c_max = min(self.sim.cols - 1, c + bs)

        self.sim.obstacles[r_min:r_max + 1, c_min:c_max + 1] = not erase

    def handle_event(self, event: pygame.event.Event):
        self.btn_play.handle_event(event)
        self.btn_reset.handle_event(event)
        self.btn_tool_wall.handle_event(event)
        self.btn_tool_erase.handle_event(event)
        self.btn_tool_food.handle_event(event)
        self.btn_tool_nest.handle_event(event)
        self.btn_preset_barrier.handle_event(event)
        self.btn_preset_maze.handle_event(event)
        self.btn_clear_walls.handle_event(event)

        self.slider_ants.handle_event(event)
        self.slider_evap.handle_event(event)
        self.slider_diff.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.canvas_rect.collidepoint(mx, my):
                rel_x = mx - self.canvas_rect.x
                rel_y = my - self.canvas_rect.y

                if event.button == 3:
                    self._apply_brush(mx, my, erase=True)
                    self.is_mouse_drawing = True
                elif event.button == 1:
                    if self.active_tool == VisualizerGrid.TOOL_DRAW_WALL:
                        self._apply_brush(mx, my, erase=False)
                        self.is_mouse_drawing = True
                    elif self.active_tool == VisualizerGrid.TOOL_ERASE_WALL:
                        self._apply_brush(mx, my, erase=True)
                        self.is_mouse_drawing = True
                    elif self.active_tool == VisualizerGrid.TOOL_PLACE_FOOD:
                        self.sim.add_food_source(rel_x, rel_y, radius=22.0, amount=1000)
                    elif self.active_tool == VisualizerGrid.TOOL_MOVE_NEST:
                        self.sim.set_nest_pos(rel_x, rel_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_mouse_drawing = False

        elif event.type == pygame.MOUSEMOTION and self.is_mouse_drawing:
            mx, my = event.pos
            if self.canvas_rect.collidepoint(mx, my):
                erase = (self.active_tool == VisualizerGrid.TOOL_ERASE_WALL) or (pygame.mouse.get_pressed()[2])
                self._apply_brush(mx, my, erase=erase)

    def update(self):
        if self.is_running:
            self.sim.step()

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (12, 14, 20), self.canvas_rect, border_radius=10)
        pygame.draw.rect(surface, SURFACE_BORDER, self.canvas_rect, width=1, border_radius=10)

        self._draw_pheromone_heatmaps(surface)
        self._draw_obstacles(surface)
        self._draw_nest(surface)
        self._draw_food(surface)
        self._draw_ants(surface)

        tip = "Clique/Arraste no canvas para desenhar paredes, adicionar comida ou mover o ninho"
        tip_s = self.font_node.render(tip, True, TEXT_MUTED)
        surface.blit(tip_s, (self.canvas_rect.x + 12, self.canvas_rect.bottom - 22))

        self._draw_sidebar(surface)

    def _draw_pheromone_heatmaps(self, surface: pygame.Surface):
        """Renderiza camadas combinadas de feromônio de Comida (Verde/Ciano) e de Ninho (Azul)."""
        food_grid = self.sim.pheromone_food
        home_grid = self.sim.pheromone_home

        grid_surf = pygame.Surface((self.sim.cols, self.sim.rows))
        
        r_channel = np.clip(home_grid * 1.5, 0, 80).astype(np.uint8)
        g_channel = np.clip(food_grid * 3.5, 0, 240).astype(np.uint8)
        b_channel = np.clip(home_grid * 2.8 + food_grid * 0.8, 0, 220).astype(np.uint8)

        rgb_array = np.dstack((r_channel, g_channel, b_channel))
        pygame.surfarray.blit_array(grid_surf, np.transpose(rgb_array, (1, 0, 2)))

        scaled_surf = pygame.transform.scale(grid_surf, (self.canvas_width, self.canvas_height))
        surface.blit(scaled_surf, self.canvas_rect.topleft, special_flags=pygame.BLEND_ADD)

    def _draw_obstacles(self, surface: pygame.Surface):
        """Renderiza as paredes/obstáculos na grade."""
        scale = self.sim.grid_scale
        rows, cols = np.where(self.sim.obstacles)
        for r, c in zip(rows, cols):
            rect = pygame.Rect(
                self.canvas_rect.x + c * scale,
                self.canvas_rect.y + r * scale,
                scale, scale
            )
            pygame.draw.rect(surface, OBSTACLE_COLOR, rect)

    def _draw_nest(self, surface: pygame.Surface):
        """Renderiza o ninho com círculos concêntricos luminosos."""
        nx = int(self.canvas_rect.x + self.sim.nest_pos[0])
        ny = int(self.canvas_rect.y + self.sim.nest_pos[1])
        rad = int(self.sim.nest_radius)

        pygame.draw.circle(surface, (80, 60, 20), (nx, ny), rad + 6)
        pygame.draw.circle(surface, NEST_COLOR, (nx, ny), rad)
        pygame.draw.circle(surface, (255, 220, 120), (nx, ny), rad - 6)

        lbl = self.font_bold.render("NINHO", True, (40, 25, 0))
        surface.blit(lbl, lbl.get_rect(center=(nx, ny)))

    def _draw_food(self, surface: pygame.Surface):
        """Renderiza as fontes de comida com contador de recursos."""
        for food in self.sim.food_sources:
            if food["amount"] > 0:
                fx = int(self.canvas_rect.x + food["x"])
                fy = int(self.canvas_rect.y + food["y"])
                rad = int(food["radius"])

                pygame.draw.circle(surface, (20, 70, 30), (fx, fy), rad + 4)
                pygame.draw.circle(surface, FOOD_COLOR, (fx, fy), rad)
                pygame.draw.circle(surface, (160, 245, 175), (fx, fy), max(4, rad - 6))

                lbl = self.font_node.render(str(food["amount"]), True, (10, 40, 15))
                surface.blit(lbl, lbl.get_rect(center=(fx, fy)))

    def _draw_ants(self, surface: pygame.Surface):
        """Renderiza cada formiga orientada pelo seu vetor de direção."""
        for ant in self.sim.ants:
            ax = self.canvas_rect.x + ant.x
            ay = self.canvas_rect.y + ant.y

            color = ANT_FOOD_COLOR if ant.has_food else ANT_COLOR
            pygame.draw.circle(surface, color, (int(ax), int(ay)), 3)

            hx = ax + np.cos(ant.angle) * 4.0
            hy = ay + np.sin(ant.angle) * 4.0
            pygame.draw.line(surface, (255, 255, 255), (int(ax), int(ay)), (int(hx), int(hy)), 1)

    def _draw_sidebar(self, surface: pygame.Surface):
        """Desenha widgets e estatísticas na barra lateral."""
        self.btn_play.draw(surface)
        self.btn_reset.draw(surface)

        self.btn_tool_wall.draw(surface)
        self.btn_tool_erase.draw(surface)
        self.btn_tool_food.draw(surface)
        self.btn_tool_nest.draw(surface)

        self.btn_preset_barrier.draw(surface)
        self.btn_preset_maze.draw(surface)
        self.btn_clear_walls.draw(surface)

        self.slider_ants.draw(surface)
        self.slider_evap.draw(surface)
        self.slider_diff.draw(surface)

        card_rect = pygame.Rect(self.sidebar_x, self.stats_y, self.sidebar_width, 140)
        pygame.draw.rect(surface, SURFACE, card_rect, border_radius=8)
        pygame.draw.rect(surface, SURFACE_BORDER, card_rect, width=1, border_radius=8)

        sy = card_rect.y + 12
        sx = card_rect.x + 12

        title_s = self.font_bold.render("Estatísticas de Forrageamento", True, PRIMARY)
        surface.blit(title_s, (sx, sy))
        sy += 24

        c_food = self.sim.total_food_collected
        l1 = self.font_bold.render(f"Comida Coletada: {c_food} unid.", True, SUCCESS)
        surface.blit(l1, (sx, sy))
        sy += 22

        searching_count = sum(1 for a in self.sim.ants if a.state == AntAgent.SEARCHING)
        returning_count = len(self.sim.ants) - searching_count
        l2 = self.font_info.render(f"Buscando: {searching_count}  |  Retornando: {returning_count}", True, TEXT_SECONDARY)
        surface.blit(l2, (sx, sy))
        sy += 20

        l3 = self.font_node.render("Trilha Verde: Feromônio de Comida", True, (100, 220, 120))
        surface.blit(l3, (sx, sy))
        sy += 18

        l4 = self.font_node.render("Trilha Azul: Feromônio de Ninho", True, (110, 180, 255))
        surface.blit(l4, (sx, sy))
