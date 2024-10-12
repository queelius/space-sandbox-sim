from rich import print
from rich.console import Group
from rich.panel import Panel
from rich.console import Console

console1 = Console(width=20)
console2 = Console(width=30)
panel_group = Group(
    Panel("Hello", style="on blue", title="Panel 1"),
    Panel("World", style="on red"),
)
console1.print(Panel(panel_group, title="Grouped Panels"))
console2.print(Panel(panel_group, title="Grouped Panels", expand=True))