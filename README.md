# Restore Deleted Entities in Port

This script is designed to restore deleted entities in Port using data from audit logs. It fetches logs for specific blueprints (e.g., `sonarQubeProject`, `pagerdutyService`, `newRelicAlert`) within a specified timeframe and restores the entities that were deleted.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Error Handling](#error-handling)
- [Example](#example-output)

## Features

- Fetches audit logs from the [PORT API](https://docs.getport.io/api-reference/get-audit-logs) for specific blueprints.
- Restores deleted entities based on the fetched logs.
- Logs the process for easy debugging.

## Requirements

- Python 3.11+

### Python Packages

- `httpx` for making asynchronous HTTP requests
- `loguru` for logging
- `asyncio` for asynchronous programming
- `python-decouple` for loading configuration variables

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/port-labs/restore-port-data.git
   cd restore-port-data
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt`, you can manually install the dependencies:
   ```bash
   pip install httpx loguru python-decouple
   ```

## Configuration

The script uses environment variables for data like API URLs and tokens. You can set up a `.env` file or export the variables manually.

### Required Environment Variables

- `PORT_API_URL`: Base URL of Port API. Default is https://api.getport.io/v1
- `PORT_CLIENT_ID`: Port client ID for authentication
- `PORT_CLIENT_SECRET`: Port client secret for authentication
- `PORT_API_TIMEOUT`: Timeout in seconds. Default is 300
- `BLUEPRINT_IDENTIFIERS`: A comma separated list of blueprint identifiers to restore data for
- `DAYS_TO_RECOVER`: Number of days to look back when fetching audit logs. Default is 1 day

To set these variables, you can create a `.env` file in the project directory:
```env
PORT_API_URL=https://api.getport.io/v1
PORT_CLIENT_ID=your_client_id
PORT_CLIENT_SECRET=your_client_secret
BLUEPRINT_IDENTIFIERS=your_blueprint_identifier_1,your_blueprint_identifier_2
```

## Usage

Run the script with the following command:

```bash
python app.py
```

## Error Handling

The script has basic error handling with logging for the following common issues:

1. **ReadTimeout**: If the request to fetch audit logs times out, the error is logged. You may consider increasing the `PORT_API_TIMEOUT` timeout duration.
3. **Authorization Error**: Ensure your access token is valid. If it expires, the script will need to be restarted.


## Example Output

```text
2024-11-15 15:11:42.671 | INFO     | __main__:restore_deleted_entities:83 - Starting the process to restore deleted entities...
2024-11-15 15:11:43.325 | INFO     | __main__:fetch_audit_logs:37 - Fetching audit logs for blueprint 'sonarQubeProject'...
2024-11-15 15:12:43.929 | ERROR    | __main__:restore_deleted_entities:118 - An error occurred: Expecting value: line 1 column 1 (char 0)
```