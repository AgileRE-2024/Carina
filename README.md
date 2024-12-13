# Carina Master - Interactive Journal Mapping System

## Introduction
Carina is a web-based system designed to provide an interactive mind map visualization of journals relevant to user search queries. It is particularly useful for researchers, academics, and students who need to navigate large volumes of academic literature efficiently.

## Features
- Interactive mind map visualization for journal navigation.
- User-friendly interface to filter and refine search results.
- Backend powered by robust data indexing to ensure accuracy and relevance.

## Prerequisites
Before you begin, ensure you have the following installed:
- Python (version 3.8 or later)
- pip (Python package manager)
- Git
- A virtual environment tool (e.g., venv is recommended)
- Node.js (for front-end dependencies, if applicable)

## Installation Steps
1. Clone the Repository
- Open a terminal or command prompt.
- Run the following command to clone the repository:
    ```sh
    git clone https://github.com/AgileRE-2024/Carina.git
    ```
- Navigate into the project directory:
    ```sh
    cd Carina
    ```

2. Install Dependencies
- Run the following command to install all required dependencies:
    ```sh
    pip install django
    ```
    ```sh
    pip install neo4j
    ```

3. Set Up Virtual Environment
- Activate the virtual environment:
    - On Windows:
        ```sh
        env/bin/activate
        ```
    - On Linux/Mac:
        ```sh
        source env/bin/activate
        ```
- Verify that the virtual environment is active by checking for a (venv) prefix in your terminal.

5. Run the Application
- Navigate into webapp:
    ```sh
    cd webapp
    ```
- Start the development server:
    ```sh
    py manage.py runserver
    ```
- Open your browser and navigate to:
http://127.0.0.1:8000

## Troubleshooting
- Ensure you are using a compatible version of Python.
- Verify that all dependencies are installed correctly.
- Confirm that the virtual environment is activated before running commands.
- Check the console for specific error messages and tracebacks.

## Contributing
If you wish to contribute to Carina, you are welcome to fork the repository, make your changes, and submit a pull request. Your contributions are highly appreciated!

## License
> This project was created by Group 5, Software Development (Practicum) I1 class, Information Systems study program, Airlangga University.
