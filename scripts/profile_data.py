"""Datos del perfil (single source of truth para el neofetch del SVG).

Separados del generador para poder editarlos sin tocar la lógica de render.
Los datos provienen del perfil real de GitHub: DevLuisManuel.
"""
from __future__ import annotations

# Paleta del tema (dark, estilo terminal).
THEME = {
    "bg": "#0d1117",
    "titlebar": "#161b22",
    "border": "#30363d",
    "fg": "#c9d1d9",
    "dim": "#8b949e",
    "accent": "#39d353",   # verde prompt
    "cyan": "#39c5cf",      # labels
    "yellow": "#e3b341",    # valores destacados
    "magenta": "#bc8cff",   # secciones
    "red": "#ff7b72",
    "close": "#ff5f56",
    "min": "#ffbd2e",
    "max": "#27c93f",
}

USER = "devluismanuel"
HOST = "dvloper"
TITLE = f"{USER}@{HOST}: ~/profile"
PROMPT_USER = f"{USER}@{HOST}"

# Cada entrada: (label, value). Un label vacío = línea de sección/espaciado.
# Estructurado como neofetch: secciones con ~/... como encabezado.
SECTIONS: list[dict] = [
    {
        "header": "luis manuel zuñiga moreno",
        "rows": [
            ("Role", "Senior Backend Engineer · Tech Lead"),
            ("Exp", "10+ years · Founder @ DVLOPER (2016)"),
            ("Loc", "Montería, Colombia · Remote · EN/ES"),
            ("Now", "Fintech · SaaS · AI-driven backends"),
        ],
    },
    {
        "header": "~/stack",
        "rows": [
            ("Lang", "PHP · JavaScript · SQL · Python"),
            ("Backend", "Laravel · Symfony · REST · GraphQL"),
            ("Queues", "Redis · Horizon · Webhooks · Async jobs"),
            ("Data", "MySQL · PostgreSQL · Redis"),
            ("Cloud", "AWS (S3/Lambda/RDS) · GCP · Docker"),
        ],
    },
    {
        "header": "~/focus",
        "rows": [
            ("Arch", "Multi-tenant SaaS · Fintech · Event-driven"),
            ("Lead", "Led teams · code review · standards"),
            ("AI", "OpenAI API · RAG · Prompt engineering"),
            ("CI/CD", "GitHub Actions · Jenkins · Docker Swarm"),
        ],
    },
    {
        "header": "~/highlights",
        "rows": [
            ("Fintech", "fiat <-> stablecoin flows @ Flusso"),
            ("Migrate", "Laravel 6→11 · PHP 7.2→8.1 · +30% perf"),
            ("Lead", "backend team of 4 @ VML"),
        ],
    },
    {
        "header": "~/reach",
        "rows": [
            ("Web", "dvloper.com.co"),
            ("GitHub", "github.com/DevLuisManuel"),
            ("LinkedIn", "linkedin.com/in/devluism"),
            ("Mail", "ing.luiszunigam@gmail.com"),
        ],
    },
]

FOOTER = "~ open to Tech Lead / Senior Backend / AI-integration roles"
