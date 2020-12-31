import curses
from copy import copy

from flask import request
from datetime import datetime as dt


class Palette:
    WHITE = 0
    BLACK = 1

    DARK_BLUE = 2
    BLUE = 10
    LIGHT_BLUE = 4

    CYAN = 12

    DARK_GREEN = 29
    GREEN = 3
    LIGHT_GREEN = 11

    DARK_RED = 23
    RED = 5
    LIGHT_RED = 13

    PURPLE = 6
    LIGHT_PURPLE = 14

    ORANGE = 7
    YELLOW = 15
    DARK_GRAY = 9


# noinspection PyPep8Naming
class FlaskLogger:
    def __init__(self, flask):
        # Shallow copy the flask instance
        self._flask = copy(flask)

        # Number of requests to the web server
        self._ttl = 0

        # Number of 200 requests
        self._200 = 0

        # Number of 404 requests
        self._404 = 0

        # Number of 404 requests
        self._404 = 0

        # Request History
        self._request_history = []

        # Logger screen settings
        self._offset = 3
        self._win = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, 255):
            curses.init_pair(i+1, i, -1)
        self._win.immedok(True)
        curses.curs_set(0)          # Hide cursor
        self.buildInterface()       # Show the interface

        # Callbacks
        self._callbacks = []

        # Refresh interface
        self._registerCallback(self.buildInterface)

        @flask.after_request
        def after_request(response):
            self.ttl += 1
            self._request_history.append({
                "at": dt.now().strftime("%d/%m/%Y - %H:%M:%S"),
                "status": response.status,
                "path": request.path,
                "args": request.args,
                "host": request.host,
                "method": request.method,
                "origin": request.referrer,
                "scheme": request.scheme
            })

            if response.status_code == 200:
                self._200 += 1
            elif response.status_code == 404:
                self._404 += 1
            self.buildInterface()
            return response

        # Wait for interrupt to exit
        # self.wait()

    def _registerCallback(self, callback):
        self._callbacks.append(callback)

    def runCallbacks(self):
        for callback in self._callbacks:
            callback()

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, newVal):
        if self._ttl != newVal:
            self._ttl = newVal
            self.runCallbacks()

    def _showString(self, y, x, val, colour=Palette.WHITE):
        self._win.attron(curses.color_pair(colour))
        self._win.addstr(y, x, str(val))
        self._win.attroff(curses.color_pair(colour))

    def _showRequestHistory(self):
        for i, req in enumerate(self._request_history[::-1][:curses.LINES - 2 - 15]):
            strings = [
                "{:5}".format(req["method"]),
                "{:20}".format(req["path"]),
                "{:40}".format(req["status"])
            ]
            for j in range(len(strings)):
                if j == 0:
                    self._showString(15 + i, self._offset, strings[j])
                else:
                    if "40" in strings[j]:
                        colour = Palette.LIGHT_RED
                    elif "20" in strings[j]:
                        colour = Palette.CYAN
                    elif "50" in strings[j]:
                        colour = Palette.ORANGE
                    else:
                        colour = Palette.WHITE
                    self._showString(15 + i, self._offset + len(strings[j-1]), strings[j], colour=colour)

    def buildInterface(self):
        self._win.clear()
        self._win.border(0)  # Border
        self._showString(0, 5, " Flask Logger by Shinyhero36 ")
        self._showString(3, self._offset, "Running on")
        self._showString(3, 30, "http://127.0.0.1:5000")  # TODO: Get host and port

        self._showString(7, self._offset, "Connections")

        self._showString(7, 30, "ttl")
        self._showString(8, 30, self._ttl)

        self._showString(7, 40, "200")
        self._showString(8, 40, self._200)

        self._showString(7, 50, "404")
        self._showString(8, 50, self._404)

        self._showString(12, self._offset, "HTTP Connections")
        self._showString(13, self._offset, "-" * len("HTTP Connections"))
        self._win.refresh()

        self._showRequestHistory()

    def close(self):
        curses.echo()
        curses.nocbreak()
        self._win.keypad(False)
        curses.endwin()

    def wait(self):
        key = self._win.getch()
        if key in [3, 26]:
            exit()  # Exit app if ^C or ^Z is hit
