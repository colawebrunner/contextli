import json
import os

from textual.app import App, ComposeResult
from textual.containers import Container, Content
from textual.widgets import Header, Footer, Input, Static, Button
from napalm import get_network_driver
from rich.syntax import Syntax


# class Login(Static):
#     """A login Widget"""
#     def compose(self) -> ComposeResult:
#         """Compose the login widget"""
#         yield Input(placeholder="Username", id="username")
#         yield Input(placeholder="Password", password=True, id="password")
#         yield Button("Login", id="login")

#     def on_mount(self) -> None:
#         """Called when app starts."""
#         # Give the input focus, so we can start typing straight away
#         self.query_one('#username').focus()

#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         """Called when a button is pressed"""
#         if event.button.id == "login":
#             user = self.query_one('#username').value
#             password = self.query_one('#password').value
#             print(user, password)


# class GridResults(Static):
#     """A grid layout for results"""
#     def compose(self) -> ComposeResult:
#         yield Static(id="results_1", classes="box")
#         yield Static(id="results_2", classes="box")
#         yield Static(id="results_3", classes="box")
#         yield Static(id="results_4", classes="box")
#         yield Static(id="results_5", classes="box")
#         yield Static(id="results_6", classes="box")


class Results(Static):
    """A results widget"""
    def compose(self) -> ComposeResult:
        """Compose the results widget"""
        yield Static(id="results")


class CommandInput(Static):
    """A command input Widget"""
    def compose(self) -> ComposeResult:
        """Compose the command input widget"""
        yield Input(placeholder="Enter device hostname/IP and command: '<hostname/IP> <command>",id="command_input")
        yield Content(Results(), id="results-container")
        # yield Content(GridResults(), id="results-grid")

    def on_input_submitted(self, message: Input.Submitted) -> str:
        """Runs when user hits enter"""
        if message.value:
            # Pass submitted value to get_device_info
            self.get_device_info(message.value)

    def process_input(self, user_input: str) -> dict:
        """Break down the input"""
        user_input_array = user_input.split(" ")
        user_input_dict = {
            "device": user_input_array[0],
            "command": user_input_array[1],
            "args": user_input_array[2:]
        }
        return user_input_dict

    def get_device_info(self, user_input: str) -> None:
        """Use input to get device info"""
        processed_input = self.process_input(user_input)
        driver = get_network_driver("ios")
        user = os.environ.get("CONTEXTLI_USER")
        password = os.environ.get("CONTEXTLI_PASS")
        with driver(processed_input["device"], user, password) as device:
            if processed_input["command"] == "config":
                stuff = device.get_config()["running"]

            elif processed_input["command"] == "facts":
                stuff = json.dumps(device.get_facts(), indent=2)

            elif processed_input["command"] == "diff":
                hostname = processed_input["device"]
                device.load_merge_candidate(filename=f"configs/{hostname}.cfg")
                stuff = device.compare_config()

            elif processed_input["command"] == "interfaces":
                stuff = json.dumps(device.get_interfaces(), indent=2)

            elif processed_input["command"] == "check":
                stuff = json.dumps(device.get_bgp_config(), indent=2)

            elif processed_input["command"] == "cli":
                args = " ".join(processed_input["args"])
                command = device.cli([args])
                stuff = command[f"{args}"]
            else:
                command = processed_input["command"]
                stuff = f"Sorry, {command} is not supported"
        # if processed_input["command"] == "check":
        #     syntax = Syntax(stuff, "json", theme="monokai", line_numbers=True)
        #     self.query_one("#results_1").update(syntax)
        # else:
        #     syntax = Syntax(stuff, "teratermmacro", theme="nord", line_numbers=True)
        #     self.query_one("#results", Static).update(syntax)
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
        yield CommandInput()

    def on_mount(self) -> None:
        """Called when app starts."""
        # Give the input focus, so we can start typing straight away
        self.query_one('#command_input').focus()

    def action_quit(self) -> None:
        """Quit the app"""
        self.exit()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode"""
        self.dark = not self.dark


if __name__ == "__main__":
    app = ContextLI()
    app.run()
