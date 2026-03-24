"""
Flappy Bird — pygame implementation using assets in ./sprites and ./audio.
"""
from __future__ import annotations

import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Literal, Optional

GameState = Literal["ready", "playing", "gameover"]

import pygame

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
SPRITES = os.path.join(ROOT, "sprites")
AUDIO = os.path.join(ROOT, "audio")

# -----------------------------------------------------------------------------
# Display (classic 288×512, scaled up for modern screens)
# -----------------------------------------------------------------------------
SCALE = 2
# Classic resolution 288×512, scaled for visibility
WINDOW_W, WINDOW_H = 288 * SCALE, 512 * SCALE

# -----------------------------------------------------------------------------
# Gameplay tuning
# -----------------------------------------------------------------------------
FPS = 60
# Physics values are tuned in native units, then multiplied by SCALE for window coords.
GRAVITY_NATIVE = 0.55
FLAP_NATIVE = -8.8
MAX_DOWN_NATIVE = 9.5
PIPE_SPEED = 2.8
PIPE_SPAWN_DISTANCE = 200  # px in native space between pipe pair origins
GAP_MIN = 110
GAP_MAX = 150
BIRD_HITBOX_SHRINK = 4  # pixels per side in native space

# Audio (pygame mixer volume per sound, 0.0–1.0)
WING_SOUND_VOLUME = 1.0
POINT_SOUND_VOLUME = 1.0
HIT_SOUND_VOLUME = 0.3
DIE_SOUND_VOLUME = 0.4
SWOOSH_SOUND_VOLUME = 0.4


def _apply_sound_volume(sound: Optional[pygame.mixer.Sound], volume: float) -> None:
    if sound:
        sound.set_volume(volume)


def load_image(name: str) -> pygame.Surface:
    path = os.path.join(SPRITES, name)
    img = pygame.image.load(path).convert_alpha()
    return img


def scale_surface(s: pygame.Surface) -> pygame.Surface:
    if SCALE == 1:
        return s
    w, h = s.get_size()
    return pygame.transform.scale(s, (w * SCALE, h * SCALE))


def load_sound(basename: str) -> Optional[pygame.mixer.Sound]:
    for ext in (".ogg", ".wav"):
        path = os.path.join(AUDIO, basename + ext)
        if os.path.isfile(path):
            return pygame.mixer.Sound(path)
    return None


@dataclass
class PipePair:
    x: float
    gap_center_y: float
    gap_half: float
    passed: bool = False


@dataclass(frozen=True)
class State:
    """Snapshot of the game after one :meth:`Game.take_action` step.

    Positions use window pixels (origin top-left), same as pygame.

    Attributes:
        game_state: ``"ready"`` (title), ``"playing"``, or ``"gameover"``.
        score: Pipes cleared this run (0 on title / before first pipe).
        frame_counter: Total frames advanced this session; drives idle/animation timing.
        bird_x: Horizontal reference x for the bird (fixed play position, ~35% of window width).
        bird_y: Vertical **center** of the bird (matches physics / hitbox).
        bird_vel: Vertical velocity in px/frame (positive = falling, negative = moving up).
        next_pipe_gap_center_y: Vertical center of the **next** gap ahead, or ``None`` if there is no
            upcoming pipe (e.g. title screen or pipes not spawned yet).
        next_pipe_gap_half: Half the gap height (distance from center to top/bottom opening); ``None``
            if there is no next pipe.
        next_pipe_distance_x: Horizontal offset from ``bird_x`` to the **left edge** of the next pipe
            pair (``next_pipe.x - bird_x``). Can be negative if that edge is left of the anchor.
            ``None`` if there is no next pipe.
    """

    game_state: GameState
    score: int
    frame_counter: int
    bird_x: float
    bird_y: float
    bird_vel: float
    next_pipe_gap_center_y: Optional[float]
    next_pipe_gap_half: Optional[float]
    next_pipe_distance_x: Optional[float]


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Flappy Bird")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()

        # Graphics
        self.bg = scale_surface(load_image("background-day.png"))
        self.base_raw = load_image("base.png")
        self.base = scale_surface(self.base_raw)
        self.base_h = self.base.get_height()
        self.playable_h = WINDOW_H - self.base_h

        self.pipe_img = scale_surface(load_image("pipe-green.png"))
        self.pipe_w = self.pipe_img.get_width()
        self.pipe_h = self.pipe_img.get_height()
        self.pipe_top = pygame.transform.flip(self.pipe_img, False, True)

        bird_frames = [
            load_image("yellowbird-downflap.png"),
            load_image("yellowbird-midflap.png"),
            load_image("yellowbird-upflap.png"),
        ]
        self.bird_frames = [scale_surface(f) for f in bird_frames]
        self.bird_w = self.bird_frames[0].get_width()
        self.bird_h = self.bird_frames[0].get_height()

        self.msg_img = scale_surface(load_image("message.png"))
        self.gameover_img = scale_surface(load_image("gameover.png"))

        self.digit_imgs: list[pygame.Surface] = []
        for i in range(10):
            self.digit_imgs.append(scale_surface(load_image(f"{i}.png")))

        # Audio
        self.snd_wing = load_sound("wing")
        self.snd_point = load_sound("point")
        self.snd_hit = load_sound("hit")
        self.snd_die = load_sound("die")
        self.snd_swoosh = load_sound("swoosh")
        _apply_sound_volume(self.snd_wing, WING_SOUND_VOLUME)
        _apply_sound_volume(self.snd_point, POINT_SOUND_VOLUME)
        _apply_sound_volume(self.snd_hit, HIT_SOUND_VOLUME)
        _apply_sound_volume(self.snd_die, DIE_SOUND_VOLUME)
        _apply_sound_volume(self.snd_swoosh, SWOOSH_SOUND_VOLUME)

        self.font = pygame.font.Font(None, 42)

        self.reset_session()

    def reset_session(self) -> None:
        self.state = "ready"  # ready | playing | gameover
        self.score = 0
        self.pipes: list[PipePair] = []
        self.base_offset = 0.0
        self.bird_y = WINDOW_H * 0.4
        self.bird_vel = 0.0
        self.bird_frame = 0
        self.frame_counter = 0

    def start_play(self) -> None:
        self.state = "playing"
        self.score = 0
        self.pipes.clear()
        self.bird_y = WINDOW_H * 0.4
        self.bird_vel = 0.0
        self.base_offset = 0.0
        self._spawn_pipe(WINDOW_W * 0.65)
        self._spawn_pipe(WINDOW_W * 0.65 + PIPE_SPAWN_DISTANCE * SCALE)

    def _spawn_pipe(self, x: float) -> None:
        margin = 80 * SCALE
        gap_half = random.uniform(GAP_MIN * SCALE / 2, GAP_MAX * SCALE / 2)
        gap_center = random.uniform(
            margin + gap_half,
            self.playable_h - margin - gap_half,
        )
        self.pipes.append(PipePair(x=x, gap_center_y=gap_center, gap_half=gap_half))

    def bird_rect(self) -> pygame.Rect:
        bx = WINDOW_W * 0.35 - self.bird_w / 2
        r = pygame.Rect(int(bx), int(self.bird_y - self.bird_h / 2), self.bird_w, self.bird_h)
        r.inflate_ip(-BIRD_HITBOX_SHRINK * SCALE * 2, -BIRD_HITBOX_SHRINK * SCALE * 2)
        return r

    def flap(self) -> None:
        if self.snd_wing:
            self.snd_wing.play()
        self.bird_vel = FLAP_NATIVE * SCALE

    def die(self) -> None:
        if self.state != "playing":
            return
        self.state = "gameover"
        if self.snd_hit:
            self.snd_hit.play()
        if self.snd_die:
            self.snd_die.play()

    def update_ready(self) -> None:
        self.frame_counter += 1
        self.bird_frame = (self.frame_counter // 6) % 3
        self.bird_y = WINDOW_H * 0.4 + math.sin(self.frame_counter * 0.08) * (10 * SCALE)
        self.base_offset = (self.base_offset + 2) % self.base.get_width()

    def update_playing(self) -> None:
        self.frame_counter += 1
        self.bird_frame = (self.frame_counter // 5) % 3

        self.bird_vel = min(
            self.bird_vel + GRAVITY_NATIVE * SCALE,
            MAX_DOWN_NATIVE * SCALE,
        )
        self.bird_y += self.bird_vel

        self.base_offset = (self.base_offset + PIPE_SPEED * SCALE) % self.base.get_width()

        for p in self.pipes:
            p.x -= PIPE_SPEED * SCALE

        self.pipes = [p for p in self.pipes if p.x + self.pipe_w > -50 * SCALE]

        step = PIPE_SPAWN_DISTANCE * SCALE
        if self.pipes:
            rightmost = max(self.pipes, key=lambda p: p.x)
            if rightmost.x < WINDOW_W - step:
                self._spawn_pipe(rightmost.x + step)

        br = self.bird_rect()
        if br.top < 0 or br.bottom > self.playable_h:
            self.die()
            return

        for p in self.pipes:
            top_bottom = p.gap_center_y - p.gap_half
            bottom_top = p.gap_center_y + p.gap_half
            # Pipe bodies (native pipe image is tall; we crop visually by rect height)
            top_rect = pygame.Rect(
                int(p.x),
                int(top_bottom - self.pipe_h),
                self.pipe_w,
                self.pipe_h,
            )
            bottom_rect = pygame.Rect(
                int(p.x),
                int(bottom_top),
                self.pipe_w,
                self.pipe_h,
            )
            if br.colliderect(top_rect) or br.colliderect(bottom_rect):
                self.die()
                return

            if not p.passed and p.x + self.pipe_w < br.centerx:
                p.passed = True
                self.score += 1
                if self.snd_point:
                    self.snd_point.play()

    def update_gameover(self) -> None:
        self.base_offset = (self.base_offset + 1) % self.base.get_width()

    def _step_frame(self, flap: bool) -> None:
        """Advance the simulation by one frame. If ``flap`` is true, apply a tap / flap first (same semantics as space/click in ``run``)."""
        if self.state == "ready":
            if flap:
                if self.snd_swoosh:
                    self.snd_swoosh.play()
                self.start_play()
                self.flap()
            if self.state == "playing":
                self.update_playing()
            else:
                self.update_ready()
        elif self.state == "playing":
            if flap:
                self.flap()
            self.update_playing()
        elif self.state == "gameover":
            if flap:
                if self.snd_swoosh:
                    self.snd_swoosh.play()
                self.reset_session()
            if self.state == "ready":
                self.update_ready()
            else:
                self.update_gameover()

    def _poll_quit_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)

    def _build_state(self) -> State:
        bird_x = WINDOW_W * 0.35
        next_pipe: Optional[PipePair] = None
        for pipe in self.pipes:
            if pipe.x + self.pipe_w >= bird_x:
                if next_pipe is None or pipe.x < next_pipe.x:
                    next_pipe = pipe

        return State(
            game_state=self.state,
            score=self.score,
            frame_counter=self.frame_counter,
            bird_x=bird_x,
            bird_y=self.bird_y,
            bird_vel=self.bird_vel,
            next_pipe_gap_center_y=next_pipe.gap_center_y if next_pipe else None,
            next_pipe_gap_half=next_pipe.gap_half if next_pipe else None,
            next_pipe_distance_x=(next_pipe.x - bird_x) if next_pipe else None,
        )

    def take_action(self, flap: bool) -> State:
        """Step the game forward by one frame, optionally flapping. Redraws the window.

        Returns a :class:`State` snapshot after this step.
        ``state.game_state`` is one of ``"ready"``, ``"playing"``, or ``"gameover"``.
        After death, pass ``flap=True`` on a later step to return to the title screen (same as tap to retry).

        Use this for manual or scripted control; use :meth:`run` for normal real-time play.
        """
        self._poll_quit_events()
        self._step_frame(flap)
        self.draw()
        return self._build_state()

    def draw_score(self, y: int) -> None:
        s = str(self.score)
        total_w = sum(self.digit_imgs[int(c)].get_width() for c in s)
        x = (WINDOW_W - total_w) // 2
        for c in s:
            d = self.digit_imgs[int(c)]
            self.screen.blit(d, (x, y))
            x += d.get_width()

    def draw(self) -> None:
        self.screen.blit(self.bg, (0, 0))

        if self.state == "ready":
            bx = WINDOW_W * 0.35 - self.bird_frames[self.bird_frame].get_width() / 2
            by = self.bird_y - self.bird_frames[self.bird_frame].get_height() / 2
            for p in self._placeholder_pipes():
                self._draw_pipe_pair(p)
            self.screen.blit(self.bird_frames[self.bird_frame], (bx, by))
            mx = (WINDOW_W - self.msg_img.get_width()) // 2
            my = (WINDOW_H * 0.22)
            self.screen.blit(self.msg_img, (mx, my))

        elif self.state == "playing":
            for p in self.pipes:
                self._draw_pipe_pair(p)
            bx = WINDOW_W * 0.35 - self.bird_frames[self.bird_frame].get_width() / 2
            by = self.bird_y - self.bird_frames[self.bird_frame].get_height() / 2
            self.screen.blit(self.bird_frames[self.bird_frame], (bx, by))
            self.draw_score(40)

        elif self.state == "gameover":
            for p in self.pipes:
                self._draw_pipe_pair(p)
            bx = WINDOW_W * 0.35 - self.bird_frames[1].get_width() / 2
            by = self.bird_y - self.bird_frames[1].get_height() / 2
            self.screen.blit(self.bird_frames[1], (bx, by))
            self.draw_score(40)
            gox = (WINDOW_W - self.gameover_img.get_width()) // 2
            goy = WINDOW_H * 0.32
            self.screen.blit(self.gameover_img, (gox, goy))
            tip = self.font.render("Space / click to retry", True, (255, 255, 255))
            tr = tip.get_rect(center=(WINDOW_W // 2, goy + self.gameover_img.get_height() + 36))
            self.screen.blit(tip, tr)

        # Scrolling ground on top
        w = self.base.get_width()
        off = int(self.base_offset) % w
        self.screen.blit(self.base, (-off, self.playable_h))
        self.screen.blit(self.base, (w - off, self.playable_h))

        pygame.display.flip()

    def _placeholder_pipes(self) -> list[PipePair]:
        """Decorative pipes on title screen."""
        cy = WINDOW_H * 0.45
        gh = 130 * SCALE / 2
        return [
            PipePair(x=WINDOW_W * 0.75, gap_center_y=cy, gap_half=gh),
        ]

    def _draw_pipe_pair(self, p: PipePair) -> None:
        top_y = p.gap_center_y - p.gap_half - self.pipe_h
        self.screen.blit(self.pipe_top, (int(p.x), int(top_y)))
        bottom_y = p.gap_center_y + p.gap_half
        self.screen.blit(self.pipe_img, (int(p.x), int(bottom_y)))

    def run(self) -> None:
        while True:
            flap = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        flap = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    flap = True

            self._step_frame(flap)
            self.draw()
            self.clock.tick(FPS)


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
