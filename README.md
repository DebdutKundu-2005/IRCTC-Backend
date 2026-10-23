# IRCTC Backend API

A railway ticket booking backend built using **Python, Django REST Framework, PostgreSQL, Redis, and Celery**.

## Features

- User authentication and protected API endpoints
- Train and station management
- Train route distance and configurable fare calculation
- Local and Express train fare configuration
- Travel-class-based fare configuration
- Ticket booking with PNR generation
- Passenger management and seat allocation
- Confirmed and waiting-list bookings
- Booking cancellation and waiting-list promotion
- Payment processing with amount validation
- Asynchronous booking confirmation emails using Celery
- Redis integration for background task processing
- API documentation using Swagger / OpenAPI
- Automated tests for core booking and payment workflows

## Tech Stack

- **Language:** Python
- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL
- **Background Tasks:** Celery
- **Message Broker / Cache:** Redis
- **API Documentation:** drf-spectacular / Swagger UI
- **Version Control:** Git and GitHub

## Project Structure

```text
IRCTC/
├── accounts/
├── bookings/
├── config/
├── payments/
├── stations/
├── trains/
├── manage.py
├── schema.yml
└── README.md
```

## Prerequisites

- Python 3
- PostgreSQL
- Redis
- Git

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/DebdutKundu-2005/IRCTC-Backend.git
cd IRCTC-Backend
```

### 2. Create and activate a virtual environment

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

Install the packages listed in your project's dependency file. If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a template. Configure your Django secret key, database credentials, email settings, and other required values.

**Never commit your real `.env` file, passwords, API keys, or secret keys.**

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start Redis

Ensure Redis is installed and running before starting background tasks.

Check the connection with:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

### 7. Start the Django server

```bash
python manage.py runserver
```

### 8. Start the Celery worker

In a separate terminal, activate the virtual environment and run:

```bash
celery -A config worker -l info
```

## API Documentation

When the development server is running, open the Swagger UI endpoint configured in `config/urls.py`.

The exact URL depends on the project's current URL configuration.

## Testing

Run the project's tests with:

```bash
python manage.py test
```

To run the booking and payment tests specifically:

```bash
python manage.py test payments.tests bookings.tests
```

## Fare Calculation

The project uses configurable demo fare rates based on train type and travel class. These are development rates and **are not official IRCTC fares**.

## Security Notes

- Keep `.env` private.
- Use a strong, randomly generated Django `SECRET_KEY`.
- Do not expose database credentials or email passwords.
- Set `DEBUG=False` and configure production security settings before deployment.

## Project Status

Under development. Features and configuration may change as development continues.

## Author

**Debdut Kundu**

GitHub: [DebdutKundu-2005](https://github.com/DebdutKundu-2005)
