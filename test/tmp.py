from rich.console import Console
from rich.prompt import Prompt
from rich.prompt import Confirm
from rich.prompt import IntPrompt
from rich.prompt import FloatPrompt
from rich.progress import track
from rich.json import JSON
from rich import print_json
import json
from rich.console import Console, OverflowMethod
import readline
from time import sleep
from rich.__main__ import make_test_card
from rich.console import Console
from rich.align import Align
from rich.text import Text
from rich.panel import Panel
console = Console()
    
def main():
    # with console.pager():
    #     console.print(make_test_card())

    # with console.screen(style="bold white on red") as screen:
    #     for count in range(5, 0, -1):
    #         text = Align.center(
    #             Text.from_markup(f"[blink]Don't Panic![/blink]\n{count}", justify="center"),
    #             vertical="middle",
    #         )
    #         screen.update(Panel(text))
    #         sleep(1)
        
    mass = FloatPrompt.ask("Enter mass", default="1e10")
    radius = FloatPrompt.ask("Enter radius", default="1e3")
    color = Prompt.ask("Enter color (RGB)", default="255,255,255")
    #console.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")
    Prompt.ask("What is [i]your[/i] [bold red]name[/]? :smiley: ")

    # Convert inputs
    mass = float(mass)
    radius = float(radius)
    color = tuple(map(int, color.split(',')))


    console.print([1,2,3])
    console.print("[blue underline]Looks like a link")
    console.print(locals())
    console.print("FOO", style="bold red on white")

    console.log("Hello, World!")
    console.log(JSON('{ "key": ["foo", "bar"]}'))

    d = { 'key': ['foo', 'bar'] }
    print_json(json.dumps(d, indent=2))

    console.rule("[bold red]Chapter 2")

    console.print(f"Updated body: mass={mass}, radius={radius}, color={color}")

    with console.status("Monkeying around...", spinner="monkey"):
        sleep(2)

    #console = Console(width=14)
    supercali = "supercalifragilisticexpialidocious"
    console.print(supercali, overflow="ellipsis")

if __name__ == "__main__":
    main()
