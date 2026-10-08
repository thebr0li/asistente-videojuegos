"""Modelos del dominio de hardware."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HardwareProfile:
    """Equipo del usuario con los valores ya traducidos a niveles comparables."""

    ram: int
    vram: int
    gpu_level: int
    cpu_level: int


@dataclass(frozen=True)
class Spec:
    """Requisitos de RAM, VRAM y niveles de GPU y CPU."""

    ram: int
    vram: int
    gpu: int
    cpu: int

    def is_met_by(self, profile: HardwareProfile) -> bool:
        return (
            profile.ram >= self.ram
            and profile.vram >= self.vram
            and profile.gpu_level >= self.gpu
            and profile.cpu_level >= self.cpu
        )


@dataclass(frozen=True)
class GameRequirements:
    """Requisitos minimos y recomendados de un juego."""

    minimum: Spec
    recommended: Spec


@dataclass(frozen=True)
class GpuSpec:
    """Nivel y VRAM de una placa de video."""

    level: int
    vram: int


@dataclass
class DetectedParts:
    """Componentes reconocidos en los pedidos del usuario.

    Se van completando a medida que el usuario los dice de a uno.
    """

    gpu_model: str | None = None
    cpu_model: str | None = None
    ram: int | None = None

    def merge(self, other: DetectedParts) -> None:
        """Lo recien detectado pisa lo anterior, como hacia el `dict.update`."""
        if other.gpu_model is not None:
            self.gpu_model = other.gpu_model
        if other.cpu_model is not None:
            self.cpu_model = other.cpu_model
        if other.ram is not None:
            self.ram = other.ram

    @property
    def is_empty(self) -> bool:
        return self.gpu_model is None and self.cpu_model is None and self.ram is None

    @property
    def missing_components(self) -> tuple[str, ...]:
        return tuple(
            name
            for name, value in (("gpu", self.gpu_model), ("cpu", self.cpu_model), ("ram", self.ram))
            if value is None
        )
