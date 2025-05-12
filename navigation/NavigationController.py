from navigation import Screen

class NavigationController:
    def __init__(self):
        # TODO: Add views once implemented
        self.main_view = None
        self.table_view = None
        self.auto_clean_view = None
        self.analytics_view = None
        self.back_stack: list[Screen] = []

    def navigate(self, screen: Screen):
        # TODO: Define navigation logic
        pass

    def pop_back_stack(self):
        if self.back_stack:
            self.navigate(self.back_stack.pop())
