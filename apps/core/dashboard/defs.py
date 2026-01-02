from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass(frozen=True)
class KpiDef:
    """Definición de una tarjeta KPI."""
    label: str
    value: str
    sub_label: str = ""
    badge_text: str = ""
    badge_color: str = "primary"  # primary, success, warning, danger, info, secondary
    icon: str = ""  # bi-icon-name

@dataclass(frozen=True)
class ChartDataset:
    label: str
    data: List[Union[int, float]]
    color: str = "primary"
    fill: bool = False

@dataclass(frozen=True)
class ChartDef:
    """Definición de un gráfico (Chart.js compatible)."""
    id: str
    title: str
    type: str  # line, bar, doughnut, pie
    labels: List[str]
    datasets: List[ChartDataset]
    height: int = 300
