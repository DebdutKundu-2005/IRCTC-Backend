# 🚆 IRCTC Backend

A REST API backend for a railway ticket booking system built with
**Python, Django, Django REST Framework, PostgreSQL, Redis, and
Celery**. It models key railway-booking workflows such as train
management, passenger details, seat allocation, PNR lookup, booking
cancellation, payment records, and asynchronous booking-confirmation
emails.

> **Project status:** Under development. Check the source code for the
> currently implemented endpoints and configuration before using this
> project in production.

------------------------------------------------------------------------

## ✨ Features

### 👤 User & API Access

-   User authentication and protected API endpoints.
-   REST APIs built with Django REST Framework.

### 🚉 Train & Station Management

-   Store train details such as train number, name, source, destination,
    timings, and seat capacity.
-   Store station-related information.
-   Configure train distance for fare calculation.

### 🎟️ Booking & Passenger Management

-   Create and view bookings.
-   Associate passenger details with bookings.
-   Allocate seats and check occupied seats.
-   Generate a PNR for a booking.
-   Search bookings using PNR.
-   Cancel bookings and track booking status.

### 💳 Payment Management

-   Create payment records associated with bookings.
-   Track payment status: `PENDING`, `COMPLETED`, and `FAILED`.
-   Validate payment amount and booking ownership.
-   Guard against duplicate payment processing.

### ⚙️ Background Tasks

-   Use **Celery** for asynchronous booking-confirmation email tasks.
-   Use **Redis** as the supporting broker/service where configured.

### 📚 API Documentation & Testing

-   OpenAPI schema documentation with **drf-spectacular**.
-   Automated API tests for booking-related workflows.

------------------------------------------------------------------------

## 🧰 Tech Stack

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  Python                              Programming language

  Django                              Backend framework

  Django REST Framework               REST API development

  PostgreSQL                          Relational database

  Redis                               Celery broker / supporting service,
                                      depending on configuration

  Celery                              Background task processing

  Simple JWT                          JWT authentication, if enabled in
                                      the current settings

  drf-spectacular                     OpenAPI schema and API
                                      documentation

  Git & GitHub                        Version control
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 🏗️ Architecture

``` text
Client / API Consumer
        |
        v
Django REST Framework API
        |
        +--> Accounts
        +--> Trains
        +--> Stations
        +--> Bookings -----> Passenger & Seat Allocation
        +--> Payments
        |
        v
    PostgreSQL

Booking workflow
        |
        v
   Celery Task
        |
        v
Booking Confirmation Email
        |
        v
      Redis
```

The exact request flow and service configuration depend on the current
project settings.

------------------------------------------------------------------------

## 📁 Project Structure

``` text
IRCTC/
├── accounts/
├── bookings/
├── config/
├── payments/
├── stations/
├── trains/
├── manage.py
├── requirements.txt
├── schema.yml
├── README.md
└── .gitignore
```

------------------------------------------------------------------------

## 🚀 Getting Started

### 1. Clone the repository

``` bash
git clone https://github.com/DebdutKundu-2005/IRCTC-Backend.git
cd IRCTC-Backend
```

### 2. Create and activate a virtual environment

**macOS / Linux**

``` bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

``` bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file or configure environment variables according
to your project settings. **Do not commit real credentials or secret
keys.**

Example placeholders:

``` env
SECRET_KEY=replace-with-a-local-secret-key
DEBUG=True
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

> These names are examples. Confirm the exact variable names expected by
> `config/settings.py` and your environment-loading setup.

### 5. Set up PostgreSQL

Create a PostgreSQL database and user, then update your local
configuration. Make sure PostgreSQL is running before starting Django.

### 6. Run migrations

``` bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser (optional)

``` bash
python manage.py createsuperuser
```

### 8. Start the development server

``` bash
python manage.py runserver
```

The local API server will normally be available at
`http://127.0.0.1:8000/`. Use the routes configured in the project to
access individual endpoints.

------------------------------------------------------------------------

## 🔄 Running Background Tasks

If Celery and Redis are configured locally, start Redis first, then run
a Celery worker in a separate terminal:

``` bash
celery -A config worker --loglevel=info
```

This command assumes `config` is the Celery app path. If your Celery app
is configured differently, use the path from your source code.

------------------------------------------------------------------------

## 🧪 Run Tests

``` bash
python manage.py test
```

If the project uses additional test configuration, follow the
instructions in the relevant test files.

------------------------------------------------------------------------

## 📖 API Documentation

The project uses `drf-spectacular` for OpenAPI schema generation. The
exact documentation URL depends on the configured URL patterns.

Common routes may look like:

``` text
/api/schema/
/api/docs/
```

If these routes do not open, check `config/urls.py` for the actual
schema and Swagger UI paths.

------------------------------------------------------------------------

## 🔐 Security Notes

-   Keep `.env` files, database passwords, Django secret keys, tokens,
    and production credentials out of Git.
-   Keep `DEBUG=False` in production.
-   Configure `ALLOWED_HOSTS` and trusted origins for the deployment
    environment.
-   Use strong, unique credentials and rotate any secret that has been
    exposed.
-   Apply authorization checks to booking and payment operations.
-   Use HTTPS and production-grade email/database settings before
    deployment.

------------------------------------------------------------------------

## 🛣️ Possible Future Improvements

-   Complete and verify fare rules for different train types and travel
    classes.
-   Add more booking lifecycle and waiting-list scenarios.
-   Expand payment integration and refund workflows.
-   Add broader unit and integration test coverage.
-   Add Docker-based local development and deployment.
-   Set up CI checks and production deployment documentation.

------------------------------------------------------------------------

## 👨‍💻 Author

**Debdut Kundu**

-   GitHub: [@DebdutKundu-2005](https://github.com/DebdutKundu-2005)
-   LinkedIn: [Debdut Kundu](https://www.linkedin.com/in/debdut-kundu-79632a37b/)

------------------------------------------------------------------------

⭐ If you find this project useful, consider giving the repository a
star.
