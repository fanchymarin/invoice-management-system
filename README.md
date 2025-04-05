# Invoice Management System

A Django-based application for managing and viewing invoices, featuring hierarchical navigation through customers, years, months, and detailed invoice information.

## Overview

This project is a Django web application that allows users to explore invoice data through a structured interface. Users can drill down from customer lists to specific years, months, and ultimately view detailed invoice information including financial metrics.

## Features

- Hierarchical data exploration:
  - Browse customers
  - View years with invoices for a specific customer
  - Browse months within a year
  - View detailed invoice information grouped by revenue source
- REST API support via JSON responses
- Responsive UI with retro Windows 98-inspired styling
- Unit tests for all API endpoints

## Technology Stack

- Django 5.1.7
- SQLite database
- CSS with 98.css for Windows 98-style UI

## Project Structure

- `invoices/`: Main application directory
  - `models.py`: Contains the Invoice model definition
  - `views.py`: Handles request processing and data aggregation
  - `tests.py`: Comprehensive test suite
  - `templates/invoices/`: HTML template for invoices page
- `static`: CSS and other static files
- `templates/registration/`: HTML template for login page

## Installation and Setup

### Prerequisites

- Python 3.x
- Make (for using the Makefile commands)

### Getting Started

1. Clone the repository

2. Set up the environment and start the server:
   ```
   make up
   ```
   This will:
   - Create a virtual environment
   - Install dependencies from requirements.txt
   - Run database migrations
   - Import data from dump.sql (if available)
   - Create Django superuser
   - Create users from imported data
   - Start the development server

### Available Make Commands

```
make list             - Show all available commands
make up               - Run the server
make migrate-invoices - Run migrations for invoices app
make debug            - Run python shell
make debugdb          - Run database shell
make test             - Run tests
make clean            - Clean up database
make fclean           - Clean up database and virtual environment
make re               - Clean up all and run the server
```

## API Usage

The application provides a REST API for accessing invoice data. Set the `Accept: application/json` and `Authorization: Basic <base64-encoded-credentials>` headers in your requests to receive JSON responses.

### Endpoints

1. **Get all customers**
   ```
   GET /invoices/
   ```
   > [!NOTE]
   > Superuser credentials are required to access this endpoint.
   
2. **Get customer invoices by year**
   ```
   GET /invoices/?customer_id=<id>
   ```

   customer_id: The ID of the customer whose invoices you want to retrieve.

3. **Get customer invoices by year and month**
   ```
   GET /invoices/?customer_id=<id>&year=<year>
   ```
   customer_id: The ID of the customer whose invoices you want to retrieve.
   year: The year for which you want to retrieve invoices.

4. **Get customer invoices by year, month, and revenue source**
   ```
   GET /invoices/?customer_id=<id>&year=<year>&month=<month>
   ```
   customer_id: The ID of the customer whose invoices you want to retrieve.
   year: The year for which you want to retrieve invoices.
   month: The month for which you want to retrieve invoices.

## Data Model

The `Invoice` model includes the following fields:
- `id`: Primary key
- `adjusted_gross_value`: Decimal (10,2)
- `haircut_percent`: Decimal (5,2)
- `daily_advance_fee`: Decimal (10,2)
- `advance_duration`: Integer
- `customer_name`: String (max 20 chars)
- `customer_id`: Integer
- `revenue_source_id`: Integer
- `revenue_source_name`: String (max 30 chars)
- `currency_code`: String (3 chars)
- `invoice_date`: Date

## Financial Calculations

The application performs several key financial calculations:
- Monthly haircut percentage (average across invoices)
- Available advance amount (adjusted for haircut)

## Testing

Run the test suite with:
```
make test
```

The test suite covers all API endpoints and includes tests for:
- Invoice creation
- Invoice counts
- Customer queries
- Year queries
- Month queries
- HTTP error code handling

## Limitations

- The application is designed for demonstration purposes and may not be suitable for production use.
- The API endpoints are hosted within the same domain as the web application, which might not scale well for larger systems.
- The application currently uses SQLite for simplicity.
