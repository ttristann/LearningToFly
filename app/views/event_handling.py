# app/views/event_handling.py
# Shared functionality that allows user interface components to receive events
# (e.g., the events returned from the p2app.engine package, or events that are
# internal to the user interface).

import tkinter



class EventHandler:
    def initiate_event(self, event):
        widget = self

        if not isinstance(widget, tkinter.Widget):
            pass

        while widget.master is not None:
            widget = widget.master

        if widget is not None:
            widget.initiate_event(event)


    def handle_event(self, event):
        self.on_event(event)

        if isinstance(self, tkinter.Tk) or isinstance(self, tkinter.Widget):
            for child in self.winfo_children():
                if not child.winfo_exists():
                    continue

                if isinstance(child, EventHandler):
                    child.handle_event(event)

        self.on_event_post(event)


    def on_event(self, event):
        pass


    def on_event_post(self, event):
        pass
