"""
Ponto de Entrada Principal da Aplicação:
🐜 Ant Colony Optimization (ACO) & Inteligência de Enxame Visualizer.
"""
import sys
import pygame

from ui.colors import (
    BG_DARK, SURFACE, SURFACE_LIGHT, SURFACE_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    PRIMARY, PRIMARY_HOVER, SUCCESS, WARNING, GOLD, CYAN
)
from ui.widgets import SegmentedControl, Button
from ui.visualizer_tsp import VisualizerTSP
from ui.visualizer_grid import VisualizerGrid


class ACOApplication:
    MODE_TSP = 0
    MODE_GRID = 1

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🐜 Ant Colony Optimization (ACO) - Simulador Visual")

        self.width = 1140
        self.height = 760
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True

        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 18, bold=True)
        self.font_subtitle = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 12)
        self.font_modal_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 18, bold=True)
        self.font_modal_body = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)
        self.font_modal_code = pygame.font.SysFont("Consolas, Courier New, monospace", 12)

        header_height = 55
        self.header_rect = pygame.Rect(0, 0, self.width, header_height)

        self.mode_control = SegmentedControl(
            rect=(self.width - 480, 10, 360, 36),
            options=["🌐 Otimização de Rotas (TSP)", "🌿 Forrageamento (Labirinto)"],
            selected_index=0,
            callback=self.on_mode_change
        )

        self.btn_help = Button(
            rect=(self.width - 105, 10, 95, 36),
            text="ℹ Teoria/Ajuda",
            callback=self.toggle_help_modal,
            bg_color=SURFACE_LIGHT,
            font_size=12
        )

        content_rect = (0, header_height, self.width, self.height - header_height)
        self.vis_tsp = VisualizerTSP(content_rect)
        self.vis_grid = VisualizerGrid(content_rect)

        self.active_mode = ACOApplication.MODE_TSP
        self.show_help = False

    def on_mode_change(self, new_mode: int):
        self.active_mode = new_mode

    def toggle_help_modal(self):
        self.show_help = not self.show_help

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_help:
                        self.show_help = False
                    else:
                        self.running = False
                elif event.key == pygame.K_h:
                    self.toggle_help_modal()
                elif event.key == pygame.K_SPACE:
                    if self.active_mode == ACOApplication.MODE_TSP:
                        self.vis_tsp.toggle_play()
                    else:
                        self.vis_grid.toggle_play()
                elif event.key == pygame.K_1:
                    self.mode_control.selected_index = 0
                    self.active_mode = ACOApplication.MODE_TSP
                elif event.key == pygame.K_2:
                    self.mode_control.selected_index = 1
                    self.active_mode = ACOApplication.MODE_GRID

            if self.show_help:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.show_help = False
                continue

            self.mode_control.handle_event(event)
            self.btn_help.handle_event(event)

            if self.active_mode == ACOApplication.MODE_TSP:
                self.vis_tsp.handle_event(event)
            else:
                self.vis_grid.handle_event(event)

    def update(self):
        if not self.show_help:
            if self.active_mode == ACOApplication.MODE_TSP:
                self.vis_tsp.update()
            else:
                self.vis_grid.update()

    def draw_header(self):
        pygame.draw.rect(self.screen, SURFACE, self.header_rect)
        pygame.draw.line(self.screen, SURFACE_BORDER, (0, self.header_rect.bottom), (self.width, self.header_rect.bottom), 1)

        title_surf = self.font_title.render("🐜 Formigueiro ML & Otimização Heurística", True, TEXT_PRIMARY)
        self.screen.blit(title_surf, (20, 10))

        sub_surf = self.font_subtitle.render("Algoritmo de Colônia de Formigas (Ant Colony Optimization - ACO)", True, TEXT_SECONDARY)
        self.screen.blit(sub_surf, (20, 32))

        self.mode_control.draw(self.screen)
        self.btn_help.draw(self.screen)

    def draw_help_modal(self):
        """Desenha a janela modal com teoria matemática do ACO e atalhos."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        modal_w, modal_h = 740, 520
        modal_rect = pygame.Rect((self.width - modal_w) // 2, (self.height - modal_h) // 2, modal_w, modal_h)

        pygame.draw.rect(self.screen, SURFACE, modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, PRIMARY, modal_rect, width=2, border_radius=12)

        mx = modal_rect.x + 25
        my = modal_rect.y + 20

        t_surf = self.font_modal_title.render("🧠 Como funciona o Algoritmo de Colônia de Formigas (ACO)", True, GOLD)
        self.screen.blit(t_surf, (mx, my))
        my += 35

        lines = [
            ("O ACO é uma metaheurística inspirada no comportamento coletivo de formigas reais,", TEXT_PRIMARY),
            ("que encontram os caminhos mais curtos através de comunicação indireta (estigmergia).", TEXT_PRIMARY),
            ("", TEXT_PRIMARY),
            ("1. Regra de Transição Probabilística:", GOLD),
            ("   P(i -> j) = [tau_ij]^alpha * [eta_ij]^beta / SOMATORIO([tau_ik]^alpha * [eta_ik]^beta)", CYAN),
            ("   • tau_ij: Intensidade do Feromônio na aresta (memória coletiva da colônia).", TEXT_SECONDARY),
            ("   • eta_ij: Visibilidade heurística = 1 / Distância (escolha gulosa local).", TEXT_SECONDARY),
            ("   • alpha: Peso do feromônio  |  beta: Peso da heurística de proximidade.", TEXT_SECONDARY),
            ("", TEXT_PRIMARY),
            ("2. Evaporação e Depósito de Feromônio:", GOLD),
            ("   tau_ij <- (1 - rho) * tau_ij + Delta_tau_ij", CYAN),
            ("   • rho (Taxa de Evaporação): Evita convergência prematura em mínimos locais.", TEXT_SECONDARY),
            ("   • Delta_tau = Q / Comprimento: Formigas com rotas mais curtas depositam mais!", TEXT_SECONDARY),
            ("", TEXT_PRIMARY),
            ("⌨ Atalhos do Teclado:", PRIMARY),
            ("   [Espaço] Executar / Pausar  |  [1] Modo TSP  |  [2] Modo Forrageamento", TEXT_PRIMARY),
            ("   [Esc] ou [Clique] para fechar esta tela de ajuda.", TEXT_MUTED)
        ]

        for text, color in lines:
            if text.startswith("   P(") or text.startswith("   tau_ij"):
                font_to_use = self.font_modal_code
            else:
                font_to_use = self.font_modal_body

            s = font_to_use.render(text, True, color)
            self.screen.blit(s, (mx, my))
            my += 22

    def run(self):
        while self.running:
            self.handle_events()
            self.update()

            self.screen.fill(BG_DARK)

            if self.active_mode == ACOApplication.MODE_TSP:
                self.vis_tsp.draw(self.screen)
            else:
                self.vis_grid.draw(self.screen)

            self.draw_header()

            if self.show_help:
                self.draw_help_modal()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = ACOApplication()
    app.run()
