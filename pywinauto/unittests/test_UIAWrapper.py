from __future__ import print_function
from __future__ import unicode_literals

"Tests for UIAWrapper"

import time
#import pprint
#import pdb
#import warnings

import ctypes
import locale
import re

import sys, os
sys.path.append(".")
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python, is_x64_OS, UIA_support
if UIA_support:
    import pywinauto.uia_defines as uia_defs
    from pywinauto.controls.UIAWrapper import UIAWrapper
from pywinauto import findwindows
#from pywinauto import clipboard
from pywinauto import backend
from pywinauto.timings import Timings, TimeoutError
Timings.Defaults()

import unittest

wpf_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\WPF_samples")
if is_x64_Python():
    wpf_samples_folder = os.path.join(wpf_samples_folder, 'x64')
wpf_app_1 = os.path.join(wpf_samples_folder, u"WpfApplication1.exe")

if UIA_support:
    # Set backend to UIA

    class UIAWrapperTests(unittest.TestCase):
        "Unit tests for the UIAWrapper class"

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""

            # start the application
            self.app = Application(backend = 'uia')
            self.app = self.app.Start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.button = UIAWrapper(self.dlg.OK.element_info)
            self.edit = UIAWrapper(self.dlg.TestLabelEdit.element_info)
            self.label = UIAWrapper(self.dlg.TestLabel.element_info)

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testFriendlyClassName(self):
            "Test getting the friendly classname of the dialog"
            self.assertEqual(self.button.friendly_class_name(), "Button")

        def test_find_nontop_ctl_by_class_name_and_title(self):
            "Test getting a non-top control by a class name and a title"

            # Look up for a non-top button control with 'Apply' caption
            caption = 'Apply'
            wins = self.app.windows_(top_level_only = False,
                                     class_name = 'Button',
                                     title = caption)

            # Verify the number of found wrappers
            self.assertEqual(len(wins), 1)

            # Verify the caption of the found wrapper
            self.assertEqual(wins[0].texts()[0], caption)

        def test_find_top_win_by_class_name_and_title(self):
            "Test getting a top window by a class name and a title"

            # Since the top_level_only is True by default 
            # we don't specify it as a criteria argument
            caption = 'WPF Sample Application'
            wins = self.app.windows_(class_name = 'Window',
                                     title = caption)

            # Verify the number of found wrappers
            self.assertEqual(len(wins), 1)

            # Verify the caption of the found wrapper
            self.assertEqual(wins[0].texts()[0], caption)

        def testClass(self):
            "Test getting the classname of the dialog"
            self.assertEqual(self.button.class_name(), "Button")

        def testWindowText(self):
            "Test getting the window Text of the dialog"
            self.assertEqual(self.label.window_text(), u"TestLabel")

        def testControlID(self):
            self.assertEqual(self.button.control_id(), None)

        def testIsVisible(self):
            self.assertEqual(self.button.is_visible(), True)

        def testIsEnabled(self):
            self.assertEqual(self.button.is_enabled(), True)

        def testProcessID(self):
            self.assertEqual(self.button.process_id(), self.dlg.process_id())
            self.assertNotEqual(self.button.process_id(), 0)

        def testIsDialog(self):
            self.assertEqual(self.button.is_dialog(), False)

        def testParent(self):
            self.assertEqual(self.button.parent(), self.dlg.WrapperObject())

        def testTopLevelParent(self):
            self.assertEqual(self.button.top_level_parent(), self.dlg.WrapperObject())

        def testTexts(self):
            self.assertEqual(self.dlg.texts(), ['WPF Sample Application'])

        def testChildren(self):
            self.assertEqual(len(self.button.children()), 1)
            self.assertEqual(self.button.children()[0].class_name(), "TextBlock")

        def testIsChild(self):
            self.assertEqual(self.button.is_child(self.dlg.WrapperObject()), True)

        def testEquals(self):
            self.assertNotEqual(self.button, self.dlg.WrapperObject())
            self.assertEqual(self.button, self.button.element_info)
            self.assertEqual(self.button, self.button)

        #def testVerifyActionable(self):
        #    self.assertRaises()

        #def testVerifyEnabled(self):
        #    self.assertRaises()

        #def testVerifyVisible(self):
        #    self.assertRaises()

        def testIsKeyboardFocusable(self):
            self.assertEqual(self.button.is_keyboard_focusable(), True)
            self.assertEqual(self.edit.is_keyboard_focusable(), True)
            self.assertEqual(self.label.is_keyboard_focusable(), False)

        def testHasKeyboardFocus(self):
            self.edit.set_focus()
            self.assertEqual(self.edit.has_keyboard_focus(), True)

        def testSetFocus(self):
            self.edit.set_focus()
            self.assertEqual(self.edit.has_keyboard_focus(), True)

        def testTypeKeys(self):
            self.edit.type_keys("testTypeKeys")
            self.assertEqual(self.edit.window_text(), "testTypeKeys")

        def testNoPatternInterfaceError(self):
            "Test a query interface exception handling"
            elem = self.button.element_info.element
            self.assertRaises(
                    uia_defs.NoPatternInterfaceError,
                    uia_defs.get_elem_interface,
                    elem, 
                    "Selection",
                    )

        def testGetProperties(self):
            uia_props = set(['class_name',
                         'friendly_class_name',
                         'texts',
                         'control_id',
                         'rectangle',
                         'is_visible',
                         'is_enabled',
                         'control_count',
                         'is_keyboard_focusable',
                         'has_keyboard_focus',
                         ])
            props = set(self.edit.get_properties().keys())
            self.assertEqual(props, uia_props)

        # def testDrawOutline(self):
        #     """Test the outline was drawn."""
        #     # not sure why, but this extra call makes the test stable
        #     self.dlg.draw_outline()
        #
        #     # outline control
        #     self.button.draw_outline()
        #     img1 = self.button.capture_as_image()
        #     self.assertEqual(img1.getpixel((0, 0)), (0, 255, 0))  # green
        #
        #     # outline window
        #     self.dlg.draw_outline(colour="blue")
        #     img2 = self.dlg.capture_as_image()
        #     self.assertEqual(img2.getpixel((0, 0)), (0, 0, 255))  # blue

    class UIAWrapperMouseTests(unittest.TestCase):
        "Unit tests for mouse actions of the UIAWrapper class"

        def setUp(self):
            """
            Start the application set some data and ensure the application
            is in the state we want it.
            """

            self.app = Application(backend = 'uia')
            self.app = self.app.Start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.button = UIAWrapper(self.dlg.OK.element_info)
            self.label = self.dlg.TestLabel.WrapperObject()

        def tearDown(self):
            "Close the application after tests"

            self.app.kill_()

        #def testClick(self):
        #    pass

        def testClickInput(self):
            time.sleep(0.5)
            self.button.click_input()
            self.assertEqual(self.label.window_text(), "LeftClick")

        #def testDoubleClick(self):
        #    pass

        def testDoubleClickInput(self):
            self.button.double_click_input()
            self.assertEqual(self.label.window_text(), "DoubleClick")

        #def testRightClick(self):
        #    pass

        def testRightClickInput(self):
            time.sleep(0.5)
            self.button.right_click_input()
            self.assertEqual(self.label.window_text(), "RightClick")

        #def testPressMoveRelease(self):
        #    pass

    class ButtonWrapperTests(unittest.TestCase):
        "Unit tests for the ButtonWrapper class"

        def setUp(self):
            """Start the application, set some data and ensure the application
            is in the state we want it."""

            # start the application
            app = Application(backend = 'uia')
            self.app = app.Start(wpf_app_1)

            self.dlg = self.app.WPFSampleApplication
            self.button = self.dlg.Button

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testFriendlyClassNames(self):
            "Test getting friendly class names of button-like controls"
            friendly_name = self.dlg.CheckBox.FriendlyClassName()
            self.assertEqual(friendly_name, "CheckBox")

            friendly_name = self.dlg.Apply.FriendlyClassName()
            self.assertEqual(friendly_name, "Button")

            friendly_name = self.dlg.ToggleMe.FriendlyClassName()
            self.assertEqual(friendly_name, "Button")

            friendly_name = self.dlg.Yes.FriendlyClassName()
            self.assertEqual(friendly_name, "RadioButton")

        def testCheckBox(self):
            "Test 'toggle' and 'toggle_state' for the check box control"
            
            # Get a current state of the check box control
            cur_state = self.dlg.CheckBox.get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_inderteminate)
            
            # Toggle the next state
            cur_state = self.dlg.CheckBox.toggle().get_toggle_state()
            
            # Get a new state of the check box control
            self.assertEqual(cur_state, uia_defs.toggle_state_off)

        def testToggleButton(self):
            "Test 'toggle' and 'toggle_state' for the toggle button control"
            
            # Get a current state of the check box control
            cur_state = self.dlg.ToggleMe.get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_on)
            
            # Toggle the next state
            cur_state = self.dlg.ToggleMe.toggle().get_toggle_state()
            
            # Get a new state of the check box control
            self.assertEqual(cur_state, uia_defs.toggle_state_off)
            
            # Toggle the next state
            cur_state = self.dlg.ToggleMe.toggle().get_toggle_state()
            self.assertEqual(cur_state, uia_defs.toggle_state_on)

        def testButtonClick(self):
            "Test the click method for the Button control"

            label = UIAWrapper(self.dlg.TestLabel.element_info)
            self.dlg.Apply.click()
            self.assertEqual(label.window_text(), "ApplyClick")

        def testRadioButton(self):
            "Test 'select' and 'is_selected' for the radio button control"
            cur_state = self.dlg.Yes.is_selected()
            self.assertEqual(cur_state, False)

            cur_state = self.dlg.Yes.select().is_selected()
            self.assertEqual(cur_state, True)


    class EditTestCases(unittest.TestCase):
        """Unit tests for the EditWrapper class"""

        def setUp(self):
            """Start the application set some data and ensure the application
            is in the state we want it."""

            # start the application
            app = Application(backend = 'uia')
            app = app.start(wpf_app_1)

            self.app = app
            self.dlg = app.WPFSampleApplication

            from pywinauto.controls.uia_controls import EditWrapper
            self.edit = EditWrapper(self.dlg.TestLabelEdit.element_info)

        def tearDown(self):
            "Close the application after tests"
            self.app.kill_()

        def testFriendlyClassNames(self):
            "Test getting friendly class names of textbox-like controls"
            self.assertEqual(self.edit.friendly_class_name(), "Edit")

        def testSetText(self):
            "Test setting the text of the edit control"
            self.edit.set_edit_text("Some text")
            self.assertEqual(self.edit.text_block(), "Some text")

            self.edit.set_edit_text(579)
            self.assertEqual(self.edit.window_text(), "579")

            self.edit.set_edit_text(333, pos_start=1, pos_end=2)
            self.assertEqual(self.edit.window_text(), "53339")

        def testLineCount(self):
            "Test getting the line count of the edit control"
            self.edit.set_edit_text("Here is some text")

            self.assertEqual(self.edit.line_count(), 1)

        def testGetLine(self):
            "Test getting each line of the edit control"
            test_data = "Here is some text"
            self.edit.set_edit_text(test_data)

            self.assertEqual(self.edit.get_line(0), test_data)

        def testTextBlock(self):
            "Test getting the text block of the edit control"
            test_data = "Here is some text"
            self.edit.set_edit_text(test_data)

            self.assertEqual(self.edit.text_block(), test_data)

        def testSelect(self):
            "Test selecting text in the edit control in various ways"
            self.edit.set_edit_text("Some text")

            self.edit.select(0, 0)
            self.assertEqual((0, 0), self.edit.selection_indices())

            self.edit.select()
            self.assertEqual((0, 9), self.edit.selection_indices())

            self.edit.select(1, 7)
            self.assertEqual((1, 7), self.edit.selection_indices())

            self.edit.select(5, 2)
            self.assertEqual((2, 5), self.edit.selection_indices())

            self.edit.select("me t")
            self.assertEqual((2, 6), self.edit.selection_indices())


if __name__ == "__main__":
    if UIA_support:
        unittest.main()
