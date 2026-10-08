"""Base de datos de juegos, placas de video y procesadores.

`gpu` y `cpu` son niveles comparables: permiten decidir si un juego corre con
componentes de distinta generacion usando un solo numero.
"""

from features.hardware.models import GameRequirements, GpuSpec, Spec

GAMES: dict[str, GameRequirements] = {
    "minecraft": GameRequirements(
        minimum=Spec(ram=2, vram=1, gpu=1, cpu=1),
        recommended=Spec(ram=4, vram=2, gpu=2, cpu=2),
    ),
    "league of legends": GameRequirements(
        minimum=Spec(ram=2, vram=1, gpu=1, cpu=1),
        recommended=Spec(ram=4, vram=2, gpu=2, cpu=2),
    ),
    "valorant": GameRequirements(
        minimum=Spec(ram=4, vram=1, gpu=2, cpu=2),
        recommended=Spec(ram=8, vram=2, gpu=3, cpu=3),
    ),
    "counter strike 2": GameRequirements(
        minimum=Spec(ram=8, vram=1, gpu=2, cpu=2),
        recommended=Spec(ram=8, vram=2, gpu=3, cpu=3),
    ),
    "fortnite": GameRequirements(
        minimum=Spec(ram=8, vram=2, gpu=3, cpu=3),
        recommended=Spec(ram=16, vram=6, gpu=6, cpu=5),
    ),
    "gta 5": GameRequirements(
        minimum=Spec(ram=4, vram=2, gpu=3, cpu=3),
        recommended=Spec(ram=8, vram=4, gpu=5, cpu=5),
    ),
    "cyberpunk 2077": GameRequirements(
        minimum=Spec(ram=8, vram=3, gpu=4, cpu=4),
        recommended=Spec(ram=16, vram=6, gpu=7, cpu=6),
    ),
    "elden ring": GameRequirements(
        minimum=Spec(ram=12, vram=3, gpu=4, cpu=4),
        recommended=Spec(ram=16, vram=6, gpu=6, cpu=6),
    ),
    "red dead redemption 2": GameRequirements(
        minimum=Spec(ram=8, vram=2, gpu=4, cpu=4),
        recommended=Spec(ram=12, vram=6, gpu=6, cpu=6),
    ),
    "god of war": GameRequirements(
        minimum=Spec(ram=8, vram=4, gpu=4, cpu=4),
        recommended=Spec(ram=16, vram=8, gpu=7, cpu=6),
    ),
}

GPUS: dict[str, GpuSpec] = {
    "integrada": GpuSpec(level=1, vram=1),
    "gtx 1050": GpuSpec(level=3, vram=2),
    "gtx 1650": GpuSpec(level=4, vram=4),
    "gtx 1660": GpuSpec(level=5, vram=6),
    "rx 580": GpuSpec(level=4, vram=8),
    "rtx 2060": GpuSpec(level=6, vram=6),
    "rx 6600": GpuSpec(level=6, vram=8),
    "rtx 3050": GpuSpec(level=5, vram=8),
    "rtx 3060": GpuSpec(level=7, vram=12),
    "rx 6700": GpuSpec(level=7, vram=12),
    "rtx 3070": GpuSpec(level=8, vram=8),
    "rtx 4060": GpuSpec(level=7, vram=8),
    "rtx 4070": GpuSpec(level=9, vram=12),
    "rtx 4090": GpuSpec(level=10, vram=24),
}

CPUS: dict[str, int] = {
    "athlon": 2,
    "core i3": 3,
    "core i5": 5,
    "core i7": 7,
    "core i9": 9,
    "ryzen 3": 3,
    "ryzen 5": 5,
    "ryzen 7": 7,
    "ryzen 9": 9,
}
