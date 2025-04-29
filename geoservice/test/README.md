# GeoService Tests

This document provides instructions for running the tests for the GeoService project.

## Prerequisites

Ensure you have the following installed:
- pytest

## Running the Tests
Navigate to the tests directory:
```sh
cd geoservice/test
```

To run the tests, use the following command:
```sh
pytest
```
You can run the test (from root directory) without changing directory with the following command:
```sh
pytest geoservice/test
```

This will execute all the test cases and provide a summary of the results.

## Additional Options

- To run a specific test file:
    ```sh
    pytest path/to/test_file.py
    ```

- To see detailed output:
    ```sh
    pytest -v
    ```

- To generate a coverage report:
    ```sh
    pytest --cov=geoservice
    ```

## Troubleshooting

If you encounter any issues, ensure that all dependencies are installed correctly and that you are using the correct version of Python.

For further assistance, refer to the project's documentation or open an issue on GitHub.