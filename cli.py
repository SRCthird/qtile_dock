import os
from .driver import launch, call
import argparse


def main():
    parser = argparse.ArgumentParser(description='Process some apps.')
    parser.add_argument('command', help='The command to run')
    parser.add_argument('-a', '--apps', nargs='+',
                        help='List of apps to launch')
    parser.add_argument('-c', '--cmd', type=str,
                        help='Cammand for the server')
    parser.add_argument('-C', '--config', type=str,
                        help='Path to the CSS for the dock')

    args = parser.parse_args()

    if args.command == 'launch' and args.apps:
        print(f"Launching with apps: {args.apps}")
        css_path = args.config if args.config else None
        launch(args.apps, show=True, config=css_path)
    elif args.command == 'restart':
        print("Restarting")
        call('stop')
    elif args.command == 'call' and args.cmd:
        print(f"Calling: {args.cmd}")
        call(args.cmd)
    else:
        print("No valid command or apps provided.")


if __name__ == '__main__':
    main()
