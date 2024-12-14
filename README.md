## Getting Started

### Prerequisites
- Docker
- Python 3.10+
- Poetry

### Setup

1. Clone the repository
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
   
3. Run the container:
   ```bash
   docker compose up --build
   ```
   
4. Apply database migrations:
   ```bash
   alembic upgrade head
   ```



## Project Structure

```
.
├── Dockerfile
├── README.md
├── alembic.ini
├── deploy
│   └── docker-compose.dev.yml
├── docker-compose.yml
├── migration
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
├── poetry.lock
├── pyproject.toml
└── simple_transactions
    ├── auth
    │   ├── db
    │   │   ├── dao
    │   │   ├── models
    │   │   └── repositories
    │   ├── services
    │   └── web
    │       ├── api
    │       │   └── v1
    │       │       ├── auth
    │       │       └── monitoring
    │       ├── application.py
    │       └── lifespan.py
    └── operation
        ├── db
        │   ├── dao
        │   ├── models
        │   └── repositories
        ├── services
        └── web
            ├── api
            │   └── v1
            │       ├── operation
            │       └── monitoring
            ├── application.py
            └── lifespan.py
```

### Environment Variables

Configure environment variables in `.env` file, example given in `.example.env`.
You can also modify specific parameters given in `settings.py` for each service,
but env parameters are overriding it.


## Usage

### API Endpoints
Auth service runs at 8000 and transaction service runs at 8001 by default.

#### Auth Service
- **POST /api/v1/auth/register**: Register a new user.
- **POST /api/v1/auth/login**: Authenticate a user and obtain JWT token.
- **POST /api/v1/auth/change-password**: Change the user password with JWT token.
- **GET /api/v1/auth/username/{username}**: Get user by username
- **POST /api/v1/auth/verify-token**: Verify JWT token with given user
#### Operation Service
- **POST /operation/transaction**: Transfer funds between users, apply JWT token for transaction initiator.
- **GET /operation/browse**: List transactions with filters.
