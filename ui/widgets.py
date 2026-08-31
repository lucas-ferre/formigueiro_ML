"""
Componentes de Interface Gráfica Interativa (Widgets) em Pygame.
Botões, Sliders, Controles de Abas e Caixas de Estatísticas.
"""
from typing import Callable, Optional, Tuple, Any
import pygame
from ui.colors import (
    SURFACE, SURFACE_LIGHT, SURFACE_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    PRIMARY, PRIMARY_HOVER, PRIMARY_ACTIVE
)


class Button:
    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        callback: Optional[Callable[[], None]] = None,
        bg_color: Tuple[int, int, int] = SURFACE_LIGHT,
        hover_color: Tuple[int, int, int] = PRIMARY_HOVER,
        text_color: Tuple[int, int, int] = TEXT_PRIMARY,
        font_size: int = 15,
        border_radius: int = 6,
        is_toggle: bool = False,
        toggled: bool = False
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.border_radius = border_radius
        self.is_toggle = is_toggle
        self.toggled = toggled

        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.SysFont("Segoe UI, Arial, sans-serif", font_size, bold=True)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Processa eventos de mouse. Retorna True se o botão foi clicado."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.is_toggle:
                    self.toggled = not self.toggled
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
        return False

    def draw(self, surface: pygame.Surface):
        if self.is_toggle and self.toggled:
            color = PRIMARY
        elif self.is_pressed:
            color = PRIMARY_ACTIVE
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.bg_color

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, SURFACE_BORDER, self.rect, width=1, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Slider:
    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        label: str,
        min_val: float,
        max_val: float,
        initial_val: float,
        step: Optional[float] = None,
        callback: Optional[Callable[[float], None]] = None,
        format_str: str = "{:.2f}"
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.step = step
        self.callback = callback
        self.format_str = format_str

        self.dragging = False
        self.font_label = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)
        self.font_value = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)

        self.track_height = 6
        self.handle_radius = 8

    def _get_track_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.rect.x,
            self.rect.y + self.rect.height - 12,
            self.rect.width,
            self.track_height
        )

    def _get_handle_pos(self) -> Tuple[int, int]:
        track = self._get_track_rect()
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        hx = int(track.x + ratio * track.width)
        hy = int(track.centery)
        return (hx, hy)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Processa eventos de arrastar slider."""
        track = self._get_track_rect()
        hitbox = track.inflate(16, 20)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hitbox.collidepoint(event.pos):
                self.dragging = True
                self._update_val_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_val_from_mouse(event.pos[0])
            return True
        return False

    def _update_val_from_mouse(self, mouse_x: int):
        track = self._get_track_rect()
        ratio = max(0.0, min(1.0, (mouse_x - track.x) / track.width))
        raw_val = self.min_val + ratio * (self.max_val - self.min_val)
        if self.step:
            raw_val = round(raw_val / self.step) * self.step
        self.value = max(self.min_val, min(self.max_val, raw_val))
        if self.callback:
            self.callback(self.value)

    def set_value(self, val: float):
        self.value = max(self.min_val, min(self.max_val, val))

    def draw(self, surface: pygame.Surface):
        label_surf = self.font_label.render(self.label, True, TEXT_SECONDARY)
        val_surf = self.font_value.render(self.format_str.format(self.value), True, PRIMARY)

        surface.blit(label_surf, (self.rect.x, self.rect.y))
        surface.blit(val_surf, (self.rect.right - val_surf.get_width(), self.rect.y))

        track = self._get_track_rect()
        pygame.draw.rect(surface, SURFACE_LIGHT, track, border_radius=3)

        hx, hy = self._get_handle_pos()
        active_rect = pygame.Rect(track.x, track.y, hx - track.x, track.height)
        pygame.draw.rect(surface, PRIMARY, active_rect, border_radius=3)

        pygame.draw.circle(surface, TEXT_PRIMARY, (hx, hy), self.handle_radius)
        pygame.draw.circle(surface, PRIMARY, (hx, hy), self.handle_radius - 2)


class SegmentedControl:
    """Controle de alternância entre múltiplas opções (Tabs / Modos)."""
    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        options: list[str],
        selected_index: int = 0,
        callback: Optional[Callable[[int], None]] = None
    ):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.selected_index = selected_index
        self.callback = callback
        self.font = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                seg_width = self.rect.width / len(self.options)
                clicked_idx = int((event.pos[0] - self.rect.x) // seg_width)
                if 0 <= clicked_idx < len(self.options) and clicked_idx != self.selected_index:
                    self.selected_index = clicked_idx
                    if self.callback:
                        self.callback(self.selected_index)
                    return True
        return False

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, SURFACE, self.rect, border_radius=8)
        pygame.draw.rect(surface, SURFACE_BORDER, self.rect, width=1, border_radius=8)

        n = len(self.options)
        seg_width = self.rect.width / n

        for i, text in enumerate(self.options):
            item_rect = pygame.Rect(
                int(self.rect.x + i * seg_width),
                self.rect.y,
                int(seg_width),
                self.rect.height
            )

            if i == self.selected_index:
                pygame.draw.rect(surface, PRIMARY, item_rect.inflate(-4, -4), border_radius=6)
                txt_color = TEXT_PRIMARY
            else:
                txt_color = TEXT_MUTED

            t_surf = self.font.render(text, True, txt_color)
            t_rect = t_surf.get_rect(center=item_rect.center)
            surface.blit(t_surf, t_rect)
