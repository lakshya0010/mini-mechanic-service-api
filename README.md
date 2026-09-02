# Mini Mechanic Service API

A backend for a mechanic-service platform, built with **Django + Django REST Framework**
and **PostgreSQL**. Users can view mechanics and their services, and customers can
create service requests against a mechanic.

## Tech Stack

- Django 5 + Django REST Framework
- PostgreSQL
- drf-spectacular (Swagger / OpenAPI docs)
- django-filter (search & filtering)

## Project Structure

```
mechanic_service/
├── manage.py
├── requirements.txt
├── .env.example
├── mechanic_service/        # project settings, root urls
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── mechanics/                # the app: models, serializers, views
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── exceptions.py         # consistent error response format
    └── tests.py
```

## Data Model

**Service** (lookup table, e.g. "Oil Change", "Tyre Repair")
- id, name

**Mechanic**
- id, name, phone, location, rating, is_open
- services → many-to-many with `Service` (a mechanic can offer several services)

**ServiceRequest**
- id, customer_name, customer_phone, vehicle_number
- mechanic → foreign key to `Mechanic`
- service → foreign key to `Service` (validated: must be a service the chosen mechanic offers)
- problem_description
- status → PENDING / ACCEPTED / IN_PROGRESS / COMPLETED / CANCELLED (default `PENDING`)
- created_at

Relationship: **Mechanic (1) → ServiceRequest (many)**.

## Setup Instructions

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/lakshya0010/mini-mechanic-service-api
cd mini-mechanic-service-api
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up PostgreSQL

Create a database and user (adjust as needed):

```sql
CREATE DATABASE mechanic_service;

ALTER USER postgres WITH PASSWORD 'admin';

GRANT ALL PRIVILEGES ON DATABASE mechanic_service TO postgres;
```

### 3. Configure environment variables

```bash
cp .env.example .env
# edit .env with your actual DB credentials
```

### 4. Run migrations and start the server

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

API is now live at `http://127.0.0.1:8000/api/`.

### 5. API Docs

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- Raw schema: `http://127.0.0.1:8000/api/schema/`

### 6. Run tests

```bash
python manage.py test
```

## API Endpoints

### Mechanics

| Method | Endpoint                | Description                          |
|--------|--------------------------|---------------------------------------|
| GET    | `/api/mechanics/`        | List all mechanics (paginated)        |
| GET    | `/api/mechanics/{id}/`   | Get a mechanic by ID                  |
| POST   | `/api/mechanics/`        | Add a new mechanic                    |
| PUT    | `/api/mechanics/{id}/`   | Full update                           |
| PATCH  | `/api/mechanics/{id}/`   | Partial update                        |
| DELETE | `/api/mechanics/{id}/`   | Delete a mechanic                     |

Query params: `?search=<name or location>`, `?is_open=true`, `?ordering=-rating`

### Service Requests

| Method | Endpoint                       | Description                     |
|--------|---------------------------------|----------------------------------|
| GET    | `/api/service-requests/`        | List all requests (paginated)    |
| GET    | `/api/service-requests/{id}/`   | Get one request                  |
| POST   | `/api/service-requests/`        | Create a new service request     |
| PATCH  | `/api/service-requests/{id}/`   | Update status, etc.              |
| DELETE | `/api/service-requests/{id}/`   | Delete a request                 |

Query params: `?status=PENDING`, `?mechanic=<id>`

## Sample Requests

### Create a mechanic

`POST /api/mechanics/`

```json
{
  "name": "Ravi Kumar",
  "phone": "9876543210",
  "location": "Delhi",
  "rating": 4.5,
  "is_open": true,
  "services": ["Oil Change", "Tyre Repair"]
}
```

**Response — 201 Created**
```json
{
  "id": 1,
  "name": "Ravi Kumar",
  "phone": "9876543210",
  "location": "Delhi",
  "rating": "4.5",
  "is_open": true,
  "services": ["Oil Change", "Tyre Repair"]
}
```

### Create a service request

`POST /api/service-requests/`

```json
{
  "customer_name": "Amit Sharma",
  "customer_phone": "9988776655",
  "vehicle_number": "KA01AB1234",
  "mechanic_id": 1,
  "service": "Oil Change",
  "problem_description": "Engine oil needs replacement."
}
```

**Response — 201 Created**
```json
{
  "id": 1,
  "customer_name": "Amit Sharma",
  "customer_phone": "9988776655",
  "vehicle_number": "KA01AB1234",
  "mechanic_id": 1,
  "service": "Oil Change",
  "problem_description": "Engine oil needs replacement.",
  "status": "PENDING",
  "created_at": "2026-09-02T10:30:00Z"
}
```

### Error examples

**Mechanic doesn't exist — 400**
```json
{
  "error": true,
  "message": "Validation failed.",
  "details": {
    "mechanic_id": ["Mechanic with the given ID does not exist."]
  }
}
```

**Invalid service for that mechanic — 400**
```json
{
  "error": true,
  "message": "Validation failed.",
  "details": {
    "service": ["Invalid service. 'Engine Rebuild' is not offered by mechanic 'Ravi Kumar'. Services offered: Oil Change, Tyre Repair."]
  }
}
```

**Missing required field — 400**
```json
{
  "error": true,
  "message": "Validation failed.",
  "details": {
    "customer_name": ["This field is required."]
  }
}
```

**Invalid vehicle number — 400**
```json
{
  "error": true,
  "message": "Validation failed.",
  "details": {
    "vehicle_number": ["Invalid vehicle number. Expected a format like 'KA01AB1234'."]
  }
}
```

## Design Notes

- `Service` is a normalized lookup table rather than a free-text field, so a
  service request is validated against the actual list of services a mechanic offers.
- A custom DRF exception handler (`mechanics/exceptions.py`) wraps all error
  responses in a consistent `{error, message, details}` shape.
- Pagination, search, and ordering are enabled by default on list endpoints via `django-filter`.
- Swagger/OpenAPI docs are auto-generated from the serializers via `drf-spectacular`.