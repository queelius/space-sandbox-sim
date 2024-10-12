from rich import print
from rich.layout import Layout
from rich.console import Console
from rich.panel import Panel

layout = Layout()

layout.split_row(
    Layout(Panel("Hello")),
    Layout(name="right"),
)

layout["right"].split_column(
    Layout(Panel("Top")),
    Layout(Panel("Bottom")),
)

console = Console()
console.print(layout)