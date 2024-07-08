# Customizable Dock UI

A customizable dock UI for launching applications with actions, mainly designed for use with the Qtile window manager. This project includes a server-client model to control the dock visibility and functionality.

## Features

- Launch applications and their actions
- Toggle dock visibility with hotkeys
- Server-client model to control the dock

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/SRCthird/qtile_dock.git
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Starting the Dock

To start the dock, use the `launch` function. You can specify a list of applications to search for and whether to show the dock initially. This is not case sensative. `show` determines whether the dock will display on start or not: defaults to hidden on start. 

```python
import qtile_dock

search_apps = ["wezterm", "htop", "google chrome"]
launch(search_apps, show=True)
```

### Controlling the Dock

You can control the dock using the `call` function. This can be used to send commands to the running instance of the dock.

```python
import qtile_dock

qtile_dock.call("toggle")  # Toggle the visibility of the dock
qtile_dock.call("stop")    # Stop the dock and the server
```

### Example

Here's an example script to start and control the dock using qtile key-binds:

```python
import qtile_dock
from libqtile.config import Key
from libqtile import hook

@hook.subscribe.startup_once
def autostart():
    # Launch the dock with specific applications
    search_apps = ["wezterm", "steam", "google chrome"]
    qtile_dock.launch(search_apps, show=True)

keys = [
    # Toggle the dock visibility
    Key(["mod1"], "o", qtile_dock.call("toggle")),

    # Kill the dock
    Key(["mod1"], "q", qtile_dock.call("stop")),
]
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Stephen Chryn  
[Email](mailto:SRCthird@gmail.com)

## Version

1.0.0
