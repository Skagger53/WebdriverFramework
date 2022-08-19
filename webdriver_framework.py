import sys

import selenium.webdriver.remote.webelement

if __name__ == "__main__":
    print("This is a supporting file. Do not execute.")
    sys.exit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import os
from datetime import timedelta
from time import sleep

# from bs4 import BeautifulSoup
# import requests

class WebdriverMain:
    def __init__(self):
        self.window_size = (1200, 900)
        self.error_col = [] # Error collection
        self.new_driver()

    # ----------------------------MAIN WEBDRIVER METHODS----------------------------
    # Attempts to reach provided url.
    # If fails, logs the error, informs user, recommends starting a new driver, and returns False.
    def get_url(self, window_handle, url):
        if isinstance(url, str) == False: raise InvalidTypePassed("url", type(url), str)

        if self.switch_window(self.main_win_handle, window_handle) == False: return False

        try:
            self.driver.get(url)
        except Exception as get_url_e:
            self.display_err_msg(get_url_e, f"Failed to reach desired URL:\n{url}\n\nTry restarting driver?\n\nPress Enter.\n")
            return False

    # Creates a new webdriver
    # Run at initialization. Can be run any other time as well.
    # Does not RE-start, only starts a new driver.
    def new_driver(self):
        print("\nStarting new webdriver...")

        self.driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

        self.driver.set_window_size(self.window_size[0], self.window_size[1])
        self.main_win_handle = self.driver.current_window_handle

    # Restarts driver. Attempts to close current driver and open a new one.
    def restart_driver(self):
        try: self.driver.quit()
        except: pass
        finally: self.new_driver()

    # If desired window handle is not the current window, attempts to switch
    # Failure will inform the user, log the error, and return False.
    def switch_window(self, curr_window_handle, new_window_handle):
        self.check_types_to_raise_exc((curr_window_handle, new_window_handle), (str, str), ("curr_window_handle", "new_window_handle"))

        # If the user's active window is the window they're trying to switch to, no action taken
        if curr_window_handle == new_window_handle: return

        try:
            self.driver.switch_to.window(new_window_handle)
        except Exception as win_switch_e:
            self.display_err_msg(win_switch_e, f"\nFailed to switch to handle {new_window_handle}.\n\nPress Enter.\n")
            return False

    # Easy way to close everything out.
    def close_out(self):
        self.err_log_dump()
        try: self.driver.quit()
        except: pass
        finally: sys.exit()

    # ----------------------------WORKING WITH ELEMENTS METHODS----------------------------
    # All the methods in this section work with elements (search, click, etc.)
    # Webdriver remains in the window_handle provided as an argument when all methods end
    # Use fail_msg argument to generate failure messages in this format: f"Failed to find {fail_msg}."
    # Failure returns False.

    # Searching for elements
    # Required arguments:
        # window_handle: handle of window to search within. The driver's active window will remain this window at the end of the method.
        # search_by: Determines the By method (selenium.webdriver.common.by) that will be used (accepted arguments: "id", "name", "xpath", "link_text", "partial_link_text", "tag_name", "class_name", "css_selector")
        # search_for: the string to search for
        # wait_time: the amount of time in seconds to wait (for WebDriverWait)
        # fail_msg: custom message to user upon a failure (see above comments)
    # Success returns the found webdriver object. Failure returns False.
    def find_ele(self, window_handle, search_by, search_for, wait_time, fail_msg):
        self.check_types_to_raise_exc(
            (window_handle, search_by, search_for, wait_time, fail_msg),
            (str, str, str, (float, int), str),
            ("window_handle", "search_by", "search_for", "wait_time", "fail_msg")
        )

        if search_for == "": return False

        # Switches windows if necessary
        if self.switch_window(self.driver.current_window_handle, window_handle) == False: return False

        # Sets up proper type object to use for search below based on search_by argument
        match search_by:
            case "id": search_by = By.ID
            case "xpath": search_by = By.XPATH
            case "link_text": search_by = By.XPATH
            case "partial_link_text": search_by = By.PARTIAL_LINK_TEXT
            case "tag_name": search_by = By.TAG_NAME
            case "class_name": search_by = By.CLASS_NAME
            case "css_selector": search_by = By.CSS_SELECTOR
            case other: raise InvalidSearchForElement(search_by)

        try:
            element = WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((search_by, search_for)))
        except Exception as search_for_id_e:
            self.display_err_msg(search_for_id_e, f"\nFailed to find {fail_msg}.\n\nPress Enter to continue.\n")
            return False
        else: return element

    # Attempts to click an element.
    # Parameter webd_ele is a webdriver object. Ideally use self.find_ele() to obtain the webdriver object and then pass that in.
    def click_ele(self, window_handle, webd_ele, fail_msg):
        self.check_types_to_raise_exc(
            (window_handle, webd_ele, fail_msg),
            (str, selenium.webdriver.remote.webelement.WebElement, str),
            ("window_handle", "webd_ele", "fail_msg")
        )

        # Switches windows if necessary
        if self.switch_window(self.driver.current_window_handle, window_handle) == False: return False

        try: webd_ele.click()
        except Exception as click_e:
            self.display_err_msg(click_e, f"\nFailed to find {fail_msg}.\n\nPress Enter")
            return False

    # Attempts to enter text into an element
    # Paremeter webd_ele is a webdriver element.
    def enter_text_ele(self, window_handle, webd_ele, text_to_enter, fail_msg):
        self.check_types_to_raise_exc(
            (window_handle, webd_ele, text_to_enter, fail_msg),
            (str, selenium.webdriver.remote.webelement.WebElement, str, str),
            ("window_handle", "webd_ele", "text_to_enter", "fail_msg")
        )

        # Switches windows if necessary
        if self.switch_window(self.driver.current_window_handle, window_handle) == False: return False

        try: webd_ele.send_keys(text_to_enter)
        except Exception as enter_text_e:
            self.display_err_msg(enter_text_e, f"Failed to enter text into {fail_msg}.\n\nPress Enter to continue.\n")
            return False

    # Attempts to press Enter on an element
    # Paremeter webd_ele is a webdriver element.
    def press_enter_ele(self, window_handle, webd_ele, fail_msg):
        self.check_types_to_raise_exc(
            (window_handle, webd_ele, fail_msg),
            (str, selenium.webdriver.remote.webelement.WebElement, str),
            ("window_handle", "webd_ele", "fail_msg")
        )

        # Switches windows if necessary
        if self.switch_window(self.driver.current_window_handle, window_handle) == False: return False

        try: webd_ele.send_keys(Keys.ENTER)
        except Exception as press_enter_e:
            self.display_err_msg(press_enter_e, f"\nFailed to press enter on {fail_msg}.\n\nPress Enter to continue.\n")
            return False

    # ----------------------------USER INPUT VALIDATION METHODS----------------------------
    # Validates user input against any criteria for numbers.
    # Set relevant parameters to False when calling this method to disallow those inputs (e.g., if you do NOT want to allow negative numbers, set negative_num = False). By default all rational numbers are allowed (all parameters are set to True).
    # Allows user to go back (returns "back") and to exit.
    # Returns False is failed. Returns the user's input as string if succeeds.
    def validate_user_input_num(self, user_input, float_num = True, negative_num = True, zero_num = True, positive_num = True):
        if isinstance(user_input, (str, int, float)) == False: raise InvalidTypePassed("user_input", type(user_input), f"({str}, {int}, {float})")

        # Checking if all criteria are set to False (nothing would pass this check)
        if negative_num == False and zero_num == False and positive_num == False:
            input("\nAll real numbers are excluded by this criteria.\n(Press Enter.)\n\n")
            return False

        # Invalid entry messages to user
        invalid_num = "\nYour input must be a number.\n\n(Press Enter.)\n"
        invalid_float_num = "\nYour input may not be a float. (Your input must be an integer).\n\n(Press Enter.)\n"
        invalid_negative_num = "\nYour input may not be negative.\n\n(Press Enter.)\n"
        invalid_zero_num = "\nYour input may not be zero.\n\n(Press Enter.)\n"
        invalid_positive_num = "\nYour input may not be positive.\n\n(Press Enter.)\n"

        user_input = user_input.strip().lower()
        orig_user_input = user_input

        if user_input == "": return False

        if user_input == "back": return "back"
        if user_input == "exit" or user_input == "close": self.close_out()

        # Checking that user's input is a number
        try: user_input = float(user_input)
        except ValueError:
            input(invalid_num)
            return False

        if float_num == False:
            if user_input != int(user_input):
                input(invalid_float_num)
                return False

        if negative_num == False:
            if user_input < 0:
                input(invalid_negative_num)
                return False

        if zero_num == False:
            if user_input == 0:
                input(invalid_zero_num)
                return False

        if positive_num == False:
            if user_input > 0:
                input(invalid_positive_num)
                return False

        return orig_user_input

    # Validates user input based on custom tuple in "acceptable" argument.
    # This does not loop; this should be called within a loop obtaining user's input.
    # user_input is not case-sensitive. Elements in acceptable list/tuple are case-sensitive. (Ideally elements in acceptable should each be all lower case or all upper case.)
    # Returns False for a failed check. Returns "back" if user wants to go back. Returns stripped user's input if succeeded.
    def validate_user_input_custom(self, user_input, acceptable):
        self.check_types_to_raise_exc((user_input, acceptable), (str, (list, tuple), str), ("user_input", "acceptable"))

        user_input = user_input.strip()
        user_input_l = user_input.lower()

        if user_input == "": return False

        if user_input_l == "back": return "back"
        if user_input_l == "exit" or user_input_l == "close": self.close_out()

        if user_input in acceptable or user_input.capitalize() in acceptable or user_input_l in acceptable: return user_input

        return False

    # Validates user input as a date.
    # This does not loop; this should be called within a loop obtaining user's input.
    # NOT case-sensitive. Commas do not matter.
    # Returns False for a failed check. Returns "back" if user wants to go back. Returns datetime object if succeeded.
    def validate_User_input_date(self, user_input):
        if isinstance(user_input, str) == False: raise InvalidTypePassed(user_input, type(user_input), str)

        if user_input == "": return False

        user_input = user_input.strip().lower().replace(",", "").replace("-", "/").replace(".", "/")

        if user_input == "back": return "back"
        if user_input == "exit" or user_input == "close": self.close_out()

        # Tuples to be cycled through for checks
        # no_year_input_test is testing when the user enters a month and day and the year will then be assumed to be the current year.
        no_year_input_test = (
            ("/" + str(datetime.datetime.now().year), "%m/%d/%Y"),
            (" " + str(datetime.datetime.now().year), "%B %d %Y"),
            (" " + str(datetime.datetime.now().year), "%b %d %Y")
        )

        # input_test is testing when the user enters a date including the year
        input_test = ("%m/%d/%Y", "%m/%d/%y", "%b %d %Y", "%b %d %y", "%B %d %Y", "%B %d %y")

        # Checks for instances when the user did not provide a year
        for check in no_year_input_test:
            try: time_obj = datetime.datetime.strptime(user_input + check[0], check[1])
            except: pass
            else: return time_obj

        # Checks for instances when the user provided the full date
        for check in input_test:
            try: time_obj = datetime.datetime.strptime(user_input, check)
            except: pass
            else: return time_obj

        return False

    # ----------------------------MISC METHODS----------------------------
    # Easy way to clear the console anytime.
    def clear_console(self): os.system("cls")

    # Logs an exception and displays the provided error message to the user (requiring Enter press). argument "error" should be a descriptive string or a captured exception.
    # No exception checking on "error" argument. There is no good way to validate the possible Exceptions that may be passed (could even be a custom exception from this module or an imported module)
    def display_err_msg(self, error, fail_msg):
        if isinstance(fail_msg, str) == False: raise InvalidTypePassed("fail_msg", type(fail_msg), str)
        
        self.error_col.append((datetime.datetime.now(), error))
        input(fail_msg)

    # Logs an error but does not inform the user. Should be a string or a captured exception.
    def log_err_no_msg(self, error):
        if isinstance(error, str) == False: raise InvalidTypePassed(error, type(error), str)

        self.error_col.append((datetime.datetime.now(), error))

    # This can be used to write errors collected in self.error_col list of tuples
    def err_log_dump(self):
        pass

    # Checks numerous variables to ensure they are the correct type. Raises exception if type is incorrect.
    # All arguments MUST be lists/tuples, even if they have only one element. (Note that if checking just one element, just doing the check directly, without check_to_raise_exc(), and then directly callin InvalidTypePassed(), is better.)
    # vars_to_check is a list/tuple of all variables to validate type
    # types_to_compare is a list/tuple of all types (must use type here, not string)
    # vars_as_strings is a list/tuple of strings of all variables being evaluated. This list visually is identical to vars_to_check except each element is a string (is in quotation marks).
    def check_types_to_raise_exc(self, vars_to_check, types_to_compare, vars_as_strings):
        # Before validating the data types provided, method first validates that the lists/tuples are the same length and that they are in fact lists or tuples.
        # Checks that the list lengths match (the lists will be zipped)
        if len(vars_to_check) != len(types_to_compare) or \
                len(types_to_compare) != len(vars_as_strings):
            raise InvalidListLength((vars_to_check, types_to_compare, vars_as_strings))

        # Checks that the arguments are lists or tuples
        validate_vars = zip((vars_to_check, types_to_compare, vars_as_strings), ("vars_to_check", "types_to_compare", "vars_as_strings"))
        for tup in validate_vars:
            if isinstance(tup[0], (list, tuple)) == False: raise InvalidTypePassed(tup[1], type(vars_to_check), (list, tuple))

        # Checks that the variables (vars_to_check) match the types provided (types_to_compare). Failure raises an Exception and informs the user of the problematic variable.
        list_to_check = zip(vars_to_check, types_to_compare, vars_as_strings)
        for checks in list_to_check:
            if isinstance(checks[0], checks[1]) == False: raise InvalidTypePassed(checks[2], type(checks[0]), checks[1])

# ----------------------------EXCEPTIONS CLASS----------------------------
# Only used for WebdriverMain() method find_ele().
# If an invalid search_by is passed in (which sets up selenium.webdriver.common.by), this exception is raised.
class InvalidSearchForElement(Exception):
    def __init__(self, search_by):
        message = f"Your provided argument of '{search_by}' is not a valid argument to search for an element. Must use one of these (as string): 'id', 'name', 'xpath', 'link_text', 'partial_link_text', 'tag_name', 'class_name', 'css_selector'."
        super().__init__(message)

# This exception is available for any method to check a variable type. An invalid type will raise this error.
# To check multiple variables at once, use WedriverMain() method check_types_to_raise_exc(). That method loops and checks each variable with the below class.
# relevant_variable is a string that can be printed to the user to identify which variable is invalid
# type_passed is the actual type of the variable (valid or invalid). Use type() around the variable i question for this.
# type_needed is the type itself that the code requires (e.g., just type "str" or "float" but without quotation marks)
class InvalidTypePassed(Exception):
    def __init__(self, relevant_variable, type_passed, type_needed):
        message = f"Argument {relevant_variable} must be {type_needed}. Received {type_passed}."
        super().__init__(message)

# Exception if lists/tuples provided to a method have unmatched lengths when they must match (e.g., they will be zipped).
class InvalidListLength(Exception):
    def __init__(self, lists_tuples):
        lists_tuples_to_user = ", ".join([l_t for l_t in lists_tuples])
        message = f"These lists/tuples have unmatched lengths: {lists_tuples_to_user}. Lengths must match."
        super().__init__(message)