from unittest.mock import Mock
from navigation import Screen, NavigationController

nav_controller: NavigationController = NavigationController()
fake_main_view = Mock()
fake_data_table_view = Mock()
fake_auto_clean_view = Mock()
fake_analytics_view = Mock()

fake_window = Mock()
stack = Mock()
fake_window.stack = stack

def initialize_nav_controller():
    nav_controller.initialize(
        window = fake_window,
        views = {
            Screen.MAIN: fake_main_view,
            Screen.DATA_TABLE: fake_data_table_view,
            Screen.AUTO_CLEAN: fake_auto_clean_view,
            Screen.ANALYTICS: fake_analytics_view,
        }
    )

def test_navigate():
    initialize_nav_controller()
    nav_controller.navigate(Screen.DATA_TABLE)
    stack.setCurrentWidget.assert_called_with(fake_data_table_view)
    assert nav_controller.back_stack[-1] == Screen.DATA_TABLE


