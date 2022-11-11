import json

from textual.app import App, ComposeResult
from textual.containers import Container, Content
from textual.widgets import Header, Footer, Input, Static
from napalm import get_network_driver
from rich.syntax import Syntax


class Login(Static):
    """A login Widget"""
    def compose(self) -> ComposeResult:
        """Compose the login widget"""
        yield Input(placeholder="Username", id="username")
        yield Input(placeholder="Password", password=True, id="password")


class CommandInput(Static):
    """A command input Widget"""
    def compose(self) -> ComposeResult:
        """Compose the command input widget"""
        yield Input(placeholder="Command")

    def on_input_submitted(self, message: Input.Submitted) -> None:
        """Runs when user hits enter"""
        if message.value:
            # Get device stuff
            self.get_device_info(message.value)

    def get_device_info(self, items) -> None:
        """Terrible looking function with a bunch of if statements"""
        things = items.split(" ")
        driver = get_network_driver("eos")
        with driver(things[0], "admin", "admin") as device:
            if things[1] == "config":
                stuff = device.get_config()["running"]

            elif things[1] == "facts":
                stuff = json.dumps(device.get_facts(), indent=2)

            elif things[1] == "diff":
                device.load_merge_candidate(filename=f"configs/{things[0]}.cfg")
                stuff = device.compare_config()

            elif things[1] == "interfaces":
                stuff = json.dumps(device.get_interfaces(), indent=2)

            elif things[1] == "cli":
                command = device.cli([" ".join(things[2:])])
                stuff = command[f"{' '.join(things[2:])}"]
            else:
                stuff = f"Sorry, '{things[1]}' is not supported"

        syntax = Syntax(stuff, "teratermmacro", theme="nord", line_numbers=True)
        self.query_one("#results", Static).update(syntax)


class ContextLI(App):
    """Textual App to check router cisco router connectivity"""

    CSS_PATH = "app.css"
    BINDINGS = [("ctrl+q", "quit", "Quit"), ("ctrl+d", "toggle_dark", "Dark Mode")]

    def compose(self) -> ComposeResult:
        """Compose the UI"""
        yield Header()
        yield Footer()
        yield Container(Login(), CommandInput())
        # yield Container(CommandInput())
        yield Content(Static(id="results"), id="results-container")

    def on_mount(self) -> None:
        """Called when app starts."""
        # Give the input focus, so we can start typing straight away
        self.query_one('#username').focus()

    def action_quit(self) -> None:
        """Quit the app"""
        self.exit()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode"""
        self.dark = not self.dark


if __name__ == "__main__":
    app = ContextLI()
    app.run()
