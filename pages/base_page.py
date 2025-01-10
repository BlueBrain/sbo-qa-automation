# Copyright (c) 2024 Blue Brain Project/EPFL
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.usefixtures("setup", "logger")
class CustomBasePage:

    def __init__(self, browser, wait, base_url):
        self.browser = browser
        self.wait = wait
        self.base_url = base_url
        # self.base_url = "https://openbluebrain.com/app"
        self.browser.set_page_load_timeout(60)

    def go_to_page(self, page_url):
        url = self.base_url + page_url
        self.browser.get(url)

    def find_element(self, by_locator, timeout=10):
        return self.wait.until(EC.presence_of_element_located(by_locator), timeout)

    def element_visibility(self, by_locator, timeout=10):
        return self.wait.until(EC.visibility_of_element_located(by_locator), timeout)

    def visibility_of_all_elements(self, by_locator, timeout=10):
        return self.wait.until(EC.visibility_of_all_elements_located(by_locator), timeout)

    def find_all_elements(self, by_locator, timeout=10):
        return self.wait.until(EC.presence_of_all_elements_located(by_locator), timeout)

    def element_to_be_clickable(self, by_locator, timeout=10):
        self.wait.until(EC.element_to_be_clickable(by_locator), timeout)

    def assert_element_text(self, by_locator, expected_text):
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        assert element.text == expected_text

    def is_enabled(self, by_locator):
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        return element.is_enabled()

    def enter_text(self, by_locator, text):
        return self.wait.until(EC.visibility_of_element_located(by_locator)).send_keys(text)

    def is_visible(self, by_locator):
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        return bool(element)

    def wait_for_long_load(self, by_locator, timeout=60):
        return self.wait.until(EC.visibility_of_element_located(by_locator), timeout)

    def wait_for_page_ready(self, timeout=10):
        """
        Waits until the page's readyState is 'complete', indicating that the page has finished loading.

        Args:
            timeout (int): Maximum time to wait for the page to be ready.

        Returns:
            bool: True if the page is ready within the timeout, False otherwise.
        """
        return self.wait.until(
            lambda driver: self.browser.execute_script("return document.readyState") == "complete",
            f"Page did not reach ready state within {timeout} seconds"
        )

    def wait_for_condition(self, condition, timeout=60, message=None):
        """
        General-purpose wait function to wait for a specific condition.
        :param condition: The condition to wait for (e.g., element presence, URL contains).
        :param timeout: How long to wait before timing out.
        :param message: Custom error message if timeout occurs.
        :return: The result of the condition (e.g., an element or True).
        """
        try:
            return self.wait.until(condition, message)
        except TimeoutException as e:
            raise RuntimeError(message or f"Condition not met within {timeout} seconds") from e
