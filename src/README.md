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
- REST API support via JSON responses with Basic Authentication
- Responsive UI with retro Windows 98-inspired styling
- Unit tests for all API endpoints
- Role-based access control (admin vs customer users)

## Technology Stack

- Django 5.1.7
- PostgreSQL database
- CSS with 98.css for Windows 98-style UI

## Project Structure

- `invoices/`: Main application directory
  - `models.py`: Contains the Invoice model definition
  - `views.py`: Handles request processing and data aggregation
  - `middleware.py`: Custom middleware for authentication and access control
  - `tests.py`: Comprehensive test suite
  - `templates/invoices/`: HTML template for invoices page
- `static`: CSS and other static files
- `templates/registration/`: HTML template for login page

## Installation and Setup

### Prerequisites

- Python 3.x
- Make (for using the Makefile commands)
- PostgreSQL database

### Getting Started

1. Clone the repository

2. Set up the environment and start the server:
   ```
   make up
   ```
   This will:
   - Install dependencies from requirements.txt
   - Run database migrations
   - Import data from SQL dump file
   - Create Django superuser (username: `admin`, password: `admin`)
   - Create users from imported data (password: `1234` for all customer users)
   - Start the development server at `0.0.0.0:8000`

### Available Make Commands

```
make list             - Show all available commands
make up               - Run the server
make setup            - Create virtual environment and install dependencies
make shell            - Run python shell
make dbshell          - Run database shell
make test             - Run tests
make clean            - Clean up database
make fclean           - Clean up database and virtual environment
make re               - Clean up all and run the server
```

## Authentication

The system has two types of users:
- **Superuser**: Can view all customers and their invoices (username: admin, password: admin)
- **Customer users**: Can only view their own invoices (username: customer name, password: 1234)

## API Usage

The application provides a REST API for accessing invoice data. Set the `Accept: application/json` and `Authorization: Basic <base64-encoded-credentials>` headers in your requests to receive JSON responses.

### Endpoints

1. **Get all customers**
   ```
   GET /invoices/
   ```
   > **NOTE**: Superuser credentials are required to access this endpoint.
   
2. **Get customer invoices by year**
   ```
   GET /invoices/?customer_id=<id>
   ```

3. **Get customer invoices by year and month**
   ```
   GET /invoices/?customer_id=<id>&year=<year>
   ```

4. **Get customer invoices by year, month, and revenue source**
   ```
   GET /invoices/?customer_id=<id>&year=<year>&month=<month>
   ```

### Authentication Headers

API requests must include Basic Authentication:
```
Authorization: Basic <base64-encoded-credentials>
```

Example:
```
Authorization: Basic YWRtaW46YWRtaW4=  (for admin:admin)
```

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
- Monthly invoices amount (total_adjusted_gross_value)
- Available advance amount = total_adjusted_gross_value * (1 - monthly_haircut_percent / 100)
- Monthly fee amount = available_advance * (total_advance_fee / 100)

## Security Features

- Custom middleware for authentication and authorization
- Role-based access control
- Each customer can only access their own invoices
- Basic Authentication for API requests

## Testing

Run the test suite with:
```
make test
```

The test suite covers:
- Invoice creation
- Invoice counts
- Customer queries
- Year queries
- Month queries
- Authentication and authorization
- HTTP error code handling

## Limitations

- The application is designed for demonstration purposes, it is not meant to be used in a production environment
