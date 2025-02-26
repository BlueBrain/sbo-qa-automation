> [!WARNING]
> The Blue Brain Project concluded in December 2024, so development has ceased under the BlueBrain GitHub organization.
> Future development will take place at: https://github.com/openbraininstitute/sbo-qa-automation

# UI Tests with Selenium Python Pytest
# Documentation

## Features
- The tests use setup/teardown methods for the session. 
- Test with Chrome and Firefox (also in headless).
- Possibility to visually see the execution.
- Possibility to see the screenshots of the errors.
- A html report generated at each test run.

## Install

### Prerequisites:
- Python 3.x installed
- pip package manager installed
- Make sure pip is installed in your system (please see the instructions below).
- Install virtual environment.
- A json file with login credentials would need to be created. 

**Linux/Unix:**
- Run `sudo apt update && sudo apt install python3-pip`

### Setting Up Virtual Environment:
It's recommended to use a virtual environment to manage dependencies. Follow these steps:

**Windows/Linux/Unix:**
1. Install virtualenv if not already installed: 
    ```
    pip install virtualenv
    ```
   or use Python's built-in venv module:
    ```
    python -m venv myenv
2. Create a virtual environment:
    ```
    virtualenv myenv
    ```
3. Activate the virtual environment:
    - **Windows:**
        ```
        myenv\Scripts\activate
        ```
    - **Linux/Unix:**
        ```
        source myenv/bin/activate
        ```
4. Upgrade pip:
    ```
    python -m pip install --upgrade pip
    ```
5. Install dependencies
    ```
    pip install -r requirements.txt
    ```
   
Make sure to replace `myenv` with your preferred name for the virtual environment.

### JSON File for Login Credentials:
Create a JSON file with login credentials to authorize test execution.

### Running Tests:

You can run the tests using pytest. Navigate to the directory containing your test files and run:
   ```
   pytest tests/ -sv or pytest --headless tests -s -v --cache-clear
   ```

### Accessing the reports and screenshots
* The screenshot of an error is in the 'screenshot' directory.
* The html reports are in the tests/.
* The report.log is in allure_reports/.


## The current execution run tests on:

### Homepage
* The display of: 
  * Main titles
  * Small titles
  * Top nav buttons
  * Logos
  

### Explore 
  * The display of:
    * Titles, eg. experimental data types, model data etc.
    * Number of records (resources)
    * Neurons panel & m-types
    * 3D Atlas (fullscreen)
  * Searching for a specific brain region
  

### Explore experimental data tabs:
* Morphology
* Electrophysiology
* Neuron density
* Model data page
  * The display of column headers
  * Ticking check boxes
  * Using the free text search and the filter for searching for M-types
  * Verifying the presence of thumbnails
  * Clicking on rows to see the detail view
  * Verifying the presence of detail view headers and metadata

## Spelling/Links

This README file has been checked for spelling errors and links have been verified.

### Acknowledgment

The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government's ETH Board of the Swiss Federal Institutes of Technology.

Copyright (c) 2024 Blue Brain Project/EPFL
