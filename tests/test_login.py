# Copyright (c) 2024 Blue Brain Project/EPFL
#
# SPDX-License-Identifier: Apache-2.0


import pytest
import time


@pytest.mark.usefixtures("setup", "logger", "login")
class TestLogin:
    @pytest.mark.run(order=1)
    def test_login_process(self, setup, logger):
        """Test the login process"""
        browser, wait, base_url = setup
        # Validate the user is logged in
        print("Login process completed via fixture")
        assert "explore/interactive" in browser.current_url, \
            f"Unexpected URL after login: {browser.current_url}"

        logger.info(f"Successfully logged in. Current page URL: {browser.current_url}")


