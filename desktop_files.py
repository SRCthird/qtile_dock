import re
import os


class DesktopFiles:
    def find_icon_path(self, icon_name):
        icon_dirs = [
            "/usr/share/icons",
            "/usr/share/pixmaps",
            "/var/lib/flatpak/exports/share/icons",
            os.path.expanduser("~/.icons"),
            os.path.expanduser("~/.local/share/icons"),
            os.path.expanduser("~/.local/share/flatpak/exports/share/icons")
        ]

        for icon_dir in icon_dirs:
            for root, dirs, files in os.walk(icon_dir):
                for file in files:
                    base_name, ext = os.path.splitext(file)
                    if base_name == icon_name and ext in ('.svg', '.png', '.xpm'):
                        return os.path.join(root, file)
        return None

    def parse_desktop_file(self, desktop_file_content):
        def parse_section(section):
            name_match = re.search(
                r'^Name(?:\[.*\])?=(.*)$', section, re.MULTILINE)
            exec_match = re.search(r'^Exec=(.*)$', section, re.MULTILINE)
            icon_match = re.search(r'^Icon=(.*)$', section, re.MULTILINE)

            name = name_match.group(1) if name_match else None
            exec_command = exec_match.group(1) if exec_match else None
            icon_name = icon_match.group(1) if icon_match else None

            icon_path = self.find_icon_path(icon_name) if icon_name else None

            return {
                'Name': name,
                'Exec': exec_command,
                'Icon': icon_path
            }

        # Split the file into sections
        sections = re.split(r'\n\[', desktop_file_content)
        sections = ['[' + s for s in sections if s.strip()]

        main_entry = parse_section(sections[0])
        actions = []

        for section in sections[1:]:
            if section.startswith('[Desktop Action'):
                actions.append(parse_section(section))

        return {
            'Main Entry': main_entry,
            'Actions': actions
        }

    def __init__(self, search_terms=[]) -> None:
        self.search_terms = [term.lower() for term in search_terms]

    def get(self):
        desktop_dirs = [
            "/usr/share/applications",
            "/var/lib/flatpak/exports/share/applications",
            os.path.expanduser("~/.local/share/applications"),
            os.path.expanduser(
                "~/.local/share/flatpak/exports/share/applications")
        ]

        all_parsed_data = []

        for desktop_dir in desktop_dirs:
            for root, dirs, files in os.walk(desktop_dir):
                for file in files:
                    if file.endswith('.desktop'):
                        desktop_file_path = os.path.join(root, file)
                        with open(desktop_file_path, 'r', encoding='utf-8') as f:
                            desktop_file_content = f.read()
                            parsed_data = self.parse_desktop_file(
                                desktop_file_content)
                            app_name = parsed_data['Main Entry'].get('Name')
                            if app_name and (not self.search_terms or any(term in app_name.lower() for term in self.search_terms)):
                                all_parsed_data.append(parsed_data)

        return all_parsed_data
