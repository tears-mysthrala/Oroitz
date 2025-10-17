"""TUI entry point for Oroitz."""

from oroitz.ui.tui import OroitzTUI


def main():
    """Run the Oroitz TUI application."""
    app = OroitzTUI()
    app.run()


if __name__ == "__main__":
    main()
