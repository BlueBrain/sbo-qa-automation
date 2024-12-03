# Copyright (c) 2024 Blue Brain Project/EPFL
#
# SPDX-License-Identifier: Apache-2.0

import os
import json


def load_config():
    try:
        # Check if running in CI (e.g., GitHub Actions)
        if os.getenv('CI'):
            print("Running in CI environment (GitHub Actions)")
            # Use GitHub Secrets - these need to be set in the GitHub repository settings
            username = os.environ.get("OBI_USERNAME")
            password = os.environ.get("OBI_PASSWORD")
            if not username or not password:
                raise ValueError("USERNAME or PASSWORD not set in GitHub Secrets.")
            config = {
                'username': username,
                'password': password
            }
        else:
            # Running locally, use config.json file
            print("Running locally")
            base_dir = os.path.abspath(os.path.dirname(__file__))
            config_path = os.path.join(base_dir, '..', 'util', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)

        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


# def load_config():
#     try:
#         if os.getenv('CI'):
#             print(""" Running in GitLab CI/CD pipeline""")
#             username = os.environ['USERNAME']
#             password = os.environ['PASSWORD']
#             config = {
#                 'username': username,
#                 'password': password
#             }
#         else:
#             print("""Running locally""")
#             base_dir = os.path.abspath(os.path.dirname(__file__))
#             config_path = os.path.join(base_dir, '..', 'util', 'config.json')
#             with open(config_path, 'r') as f:
#                 config = json.load(f)
#         return config
#     except Exception as e:
#         print(f"Error loading config: {e}")
#         return None




