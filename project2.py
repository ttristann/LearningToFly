
# project2.py
# This is the main module that runs the entire program.

from app import EventBus
from app import Engine
from app import MainView


def main():
    event_bus = EventBus()
    engine = Engine()
    main_view = MainView(event_bus)

    event_bus.register_engine(engine)
    event_bus.register_view(main_view)

    main_view.run()


if __name__ == '__main__':
    main()
