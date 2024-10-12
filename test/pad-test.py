from rich import print
from rich.padding import Padding
test = Padding("Hello", (2, 4))
print(test)


from rich import print
from rich.padding import Padding
test = Padding("Hello", (2, 4), style="on blue", expand=False)
print(test)


from rich import print
from rich.panel import Panel
print(Panel("Hello, [red]World!",
                title="Example",
                subtitle="Demonstrating Panel",
                border_style="red",
                padding=(1, 2)))