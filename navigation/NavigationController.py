from PyQt6.QtWidgets import QMainWindow
from navigation import Screen
from view import AbstractView


class NavigationController:
    def __init__(self):
        self.window = None
        self.views = None
        self.back_stack: list[Screen] = []

    def initialize(self, window: QMainWindow, views: dict[Screen, AbstractView]):
        """Initialize the controller with the main window and views"""
        self.window = window
        self.views = views

    def navigate(self, screen: Screen):
        """Navigate to a specific view"""
        if not self.window or not self.views:
            raise RuntimeError("NavigationController not initialized")

        if screen in self.views:
            self.window.setCentralWidget(self.views[screen])
            self.back_stack.append(screen)

    def pop_back_stack(self):
        if not self.window or not self.views:
            raise RuntimeError("NavigationController not initialized")

        if self.back_stack:
            self.navigate(self.back_stack.pop())
