# Invoice Management System

A containerized Django application for managing and viewing customer invoices, with hierarchical navigation through customers, years, months, and detailed invoice information.

## Overview

This Invoice Management System is a Docker-containerized Django web application that allows users to explore invoice data through a structured interface. Users can drill down from customer lists to specific years, months, and ultimately view detailed invoice information including financial metrics.

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
- Containerized deployment with Docker and Docker Compose

## Technology Stack

- Django 5.1.7
- PostgreSQL database
- Docker and Docker Compose
- GitHub Actions for CI
- CSS with 98.css for Windows 98-style UI

## Project Structure

```
.
├── .github/workflows   # GitHub Actions workflow configurations
├── src/                # Django application source code
│   ├── invoices/       # Main application directory
│   │   ├── models.py   # Contains the Invoice model definition
│   │   ├── views.py    # Handles request processing and data aggregation
│   │   └── ...
│   └── ...
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
├── Makefile            # Utility commands
└── README.md           # This file
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile commands)

### Quick Start

1. Clone the repository
   ```
   git clone <repository-url>
   cd invoice-management-system
   ```

2. Start the application
   ```
   make up
   ```

3. Access the application at http://localhost:8080

### Default Credentials

The system comes with two types of users:
- **Admin**: Can view all customers and their invoices
  - Username: `admin`
  - Password: `admin`
- **Customer users**: Can only view their own invoices
  - Username: `<customer name>`
  - Password: `1234`

## Available Make Commands

```
make list             - Show all available commands
make up               - Build and run the containerized application
make build            - Build the container image
make down             - Stop the containerized application
make test             - Run tests in the containerized application
make clean            - Stop and remove the database volume
make fclean           - Stop and remove all containers and volumes
make re               - Clean up all and run the containerized application
```

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

## Financial Calculations

The application performs several key financial calculations:
- Monthly invoices amount (total_adjusted_gross_value)
- Available advance amount = total_adjusted_gross_value * (1 - monthly_haircut_percent / 100)
- Monthly fee amount = available_advance * (total_advance_fee / 100)

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

## Continuous Integration

The repository is configured with GitHub Actions to automatically run tests on push to the main branch.

## Development

For detailed information about the Django application structure and development, please refer to the [application README](src/README.md).
