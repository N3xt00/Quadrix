"""Sistema de partículas para efeitos visuais do Quadrix."""

import math
import random

import pygame


class Particle:
    """Partícula individual usada em explosões e impactos."""

    def __init__(self, x, y, color, velocity=None, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.life = life  # frames de vida
        self.max_life = life
        if velocity is None:
            # Velocidade aleatória em todas as direções
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        else:
            self.velocity = velocity

    def update(self):
        """Atualiza a posição e vida da partícula."""
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        # Aplicar alguma resistência do ar
        self.velocity[0] *= 0.98
        self.velocity[1] *= 0.98
        return self.life > 0

    def draw(self, surface):
        """Desenha a partícula na superfície."""
        if self.life <= 0:
            return

        # Calcular alpha baseado na vida restante (fade out)
        alpha = int(255 * (self.life / self.max_life))
        # Tornar a partícula menor à medida que envelhece
        size = max(1, int(3 * (self.life / self.max_life)))

        # Criar superfície com alpha
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), (size, size), size)
        surface.blit(particle_surface, (int(self.x - size), int(self.y - size)))


class ParticleSystem:
    """Gerencia grupos de partículas."""

    def __init__(self):
        self.particles = []

    def add_particle(self, particle):
        """Adiciona uma partícula ao sistema."""
        self.particles.append(particle)

    def add_particles(self, count, x, y, color, velocity_range=None):
        """Adiciona múltiplas partículas com propriedades similares."""
        for _ in range(count):
            if velocity_range is None:
                velocity = None  # Velocidade aleatória
            else:
                velocity = [
                    random.uniform(velocity_range[0][0], velocity_range[0][1]),
                    random.uniform(velocity_range[1][0], velocity_range[1][1]),
                ]
            particle = Particle(x, y, color, velocity)
            self.add_particle(particle)

    def update(self):
        """Atualiza todas as partículas e remove as mortas."""
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        """Desenha todas as partículas."""
        for particle in self.particles:
            particle.draw(surface)

    def clear(self):
        """Remove todas as partículas."""
        self.particles.clear()
