import unittest
from unittest.mock import Mock, patch

from launcher.compatibility import CompatibilityWindow


class CompatibilityTests(unittest.TestCase):
    def window(self):
        window = object.__new__(CompatibilityWindow)
        window.app = Mock(busy=False)
        window.root = Mock()
        window.path = Mock()
        return window

    def test_save_checks_selected_folder(self):
        window = self.window()
        window.path.get.return_value = 'client'
        window.select()
        window.app.select.assert_called_once_with('client')
        window.app.start.assert_called_once_with('check')

    def test_invalid_selection_does_not_start_check(self):
        window = self.window()
        window.app.select.side_effect = ValueError('Not a client')
        window.select()
        window.app.start.assert_not_called()
        self.assertEqual(window.app.error, 'Not a client')

    def test_close_during_update_is_blocked(self):
        window = self.window()
        window.app.busy = True
        with patch('launcher.compatibility.messagebox.showinfo'):
            window.close()
        window.root.destroy.assert_not_called()

    def test_buttons_route_to_existing_backend(self):
        window = self.window()
        for action in ('check', 'recover', 'update', 'play'):
            window.start(action)
            window.app.start.assert_called_with(action)


if __name__ == '__main__':
    unittest.main()
