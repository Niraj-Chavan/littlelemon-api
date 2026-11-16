# Little Lemon API — Django Back-End Capstone

REST back-end for the Little Lemon restaurant: menu management and table
booking with authentication, throttling, and a database rule that blocks
double bookings.

## Tech stack

- Python 3 + Django
- MySQL
- Django REST Framework
- Djoser (registration + token auth)
- Insomnia (API testing)

## Setup

```bash
# 1. Create a virtual environment and install packages
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Create the MySQL database and user
mysql -u root -p
#   CREATE DATABASE littlelemon;
#   CREATE USER 'admindjango'@'localhost' IDENTIFIED BY 'yourpassword';
#   GRANT ALL ON littlelemon.* TO 'admindjango'@'localhost';
#   GRANT ALL ON `test_littlelemon`.* TO 'admindjango'@'localhost';  -- for tests

# 3. Configure secrets (never commit this file)
cp .env.example .env                # then edit the MySQL password

# 4. Migrate and run
python manage.py migrate
python manage.py runserver
```

## Endpoints

| Method | URL | Auth | Description |
|---|---|---|---|
| GET | `/restaurant/` | none | Static welcome page |
| GET / POST | `/restaurant/menu/` | none | List all menu items / add one |
| GET / PUT / PATCH / DELETE | `/restaurant/menu/<id>/` | none | Read / update / delete one item |
| GET / POST | `/restaurant/booking/tables/` | token | List bookings / create one |
| GET / PUT / PATCH / DELETE | `/restaurant/booking/tables/<id>/` | token | Manage one booking |
| POST | `/auth/users/` | none | Register a user (Djoser) |
| POST | `/auth/token/login/` | none | Log in, returns auth token |
| POST | `/auth/token/logout/` | token | Log out |
| POST | `/api-token-auth/` | none | DRF token endpoint (peer review) |
| GET | `/admin/` | staff | Django admin |

Authorization header format: `Authorization: Token <your-token>` (the word
`Token`, not `Bearer`).

## Double-booking rule

`Booking` has a `UniqueConstraint` on (`table_number`, `booking_date`), so
MySQL physically cannot store two reservations for the same table at the
same time. The serializer turns the constraint into a clean `400 Bad
Request` response.

## Tests

```bash
python manage.py test
```

15 tests: menu model + `str()`, booking model, full menu CRUD through the
API, the 401/201/400 booking security flow, and Djoser registration/login.

## Insomnia

Import `LittleLemon_Insomnia_Collection.json` (in this repo) and run the
requests top to bottom: register → login (copy token) → GET menu → POST
booking without token (**401**) → with token (**201**) → again (**400**).
