# Copyright (c) 2024 Blue Brain Project/EPFL
#
# SPDX-License-Identifier: Apache-2.0
import logging
import time

from selenium.common import TimeoutException
from selenium.webdriver import Keys

from locators.login_locators import LoginPageLocators
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import CustomBasePage


class LoginPage(CustomBasePage):
    def __init__(self, browser, wait, base_url):
        super().__init__(browser, wait, base_url)
        self.logger = logging.getLogger(__name__)

    def navigate_to_homepage(self):
        self.browser.delete_all_cookies()
        target_url = self.base_url
        # target_url = "https://openbluebrain.com/app"
        # target_url = "https://staging.openbluebrain.com/"
        self.browser.get(target_url)
        print("Starting URL from pages/login_page.py:", self.browser.current_url)
        return self.browser.current_url

    def find_login_button(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.LOGIN_BUTTON))

    def wait_for_login_complete(self, timeout=30):
        """Wait for login completion by checking a URL or element."""
        try:
            self.wait.until(EC.url_contains('explore/interactive'), timeout)
        except TimeoutException:
            print(
                f"Timeout waiting for URL to contain 'virtual-lab'. Current URL: "
                f"{self.browser.current_url}")
            raise

    def find_username_field(self):
        return self.wait.until(EC.presence_of_element_located(LoginPageLocators.USERNAME_FIELD))

    def find_password_field(self):
        return self.wait.until(EC.presence_of_element_located(LoginPageLocators.PASSWORD_FIELD))

    def find_signin_button(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.SIGN_IN))

    def find_logout_button(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.LOGOUT))

    def find_submit(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.SUBMIT))

    def perform_login(self, username, password):
        self.logger.info("Performing login with the provided credentials.")

        username_field = self.find_username_field()
        password_field = self.find_password_field()

        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.ENTER)
        print("Submitted login credentials")

        self.wait_for_login_complete()
        self.wait.until(EC.url_contains("/app/explore"))
        # self.wait.until(EC.url_contains("app/virtual-lab"))
