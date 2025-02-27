# FastReferral - Secure Authentication & Referral System API

![image](https://github.com/user-attachments/assets/dee92333-8fdc-45e3-bf29-141e7d2cc0bc)

## Overview

FastReferral is a robust API built with FastAPI that provides a complete authentication system with an integrated referral program. This production-ready backend solution manages user registration, authentication, password management, and a fully-featured referral tracking system with rewards.

## Key Features

- **Complete Authentication System**
  - Secure user registration with validation
  - JWT-based authentication
  - Password hashing with bcrypt
  - Password strength verification

- **Password Management**
  - Secure password reset workflow
  - Temporary password generation
  - Email-based password recovery

- **Referral System**
  - Unique referral code generation
  - Referral tracking
  - Referral statistics
  - Referral reward management

- **Security**
  - Email validation
  - Password strength validation
  - Protection against common security vulnerabilities
  - CORS middleware support

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Password Security**: bcrypt
- **Email**: SMTP with Gmail support

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register a new user |
| POST | `/api/login` | Authenticate user and receive JWT token |
| POST | `/api/forgot-password` | Request password reset |
| POST | `/api/reset-password` | Reset password with credentials |
| GET | `/api/referrals` | Get list of referred users |
| GET | `/api/referral-stats` | Get referral statistics |

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vansh3140/FastReferral---Secure-Authentication-Referral-System-API.git
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory with the following variables:
   ```
   DB_CONNECT=postgresql://username:password@localhost:5432/dbname
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   EMAIL=your_email@gmail.com
   PASSWORD=your_app_password
   ```

5. **Initialize the database**
   ```bash
   python database.py
   ```

6. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

## Database Schema

The system uses three primary tables:

- **Users**: Stores user information, credentials, and referral codes
- **Referrals**: Tracks referral relationships between users
- **Rewards**: Manages referral bonuses and reward statuses
![image](https://github.com/user-attachments/assets/7afdc0d6-6004-4d5f-a7ff-5ee5fcdf9b42)
![image](https://github.com/user-attachments/assets/5bdebef0-4439-48cd-be73-ac897651d0de)
![image](https://github.com/user-attachments/assets/a07b94b5-49a9-4360-b3d1-fce0dd505f4b)

## Testing

FastReferral includes comprehensive test coverage with both unit tests and integration tests to ensure reliable functionality.

### Test Structure

```
tests/
├── integration-tests/
│   ├── test_login_api.py        # Tests for login functionality
│   ├── test_registration_api.py # Tests for user registration
│   └── test_referral_system_api.py  # Tests for referral system endpoints
└── unit-tests/
    ├── test_password.py         # Tests for password handling (hash, verify, strength, temp password)
    ├── test_jwt.py              # Tests for JWT token generation & verification
    ├── test_database.py         # Tests for database connections
    └── test_referral.py         # Tests for referral code generation and handling
```

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit-tests/ -v

# Run integration tests only
pytest tests/integration-tests/ -v

# Run with coverage report
pytest --cov=. tests/
```

## Usage Examples

### User Registration
![image](https://github.com/user-attachments/assets/30fb1251-1625-41ef-a015-56fec761b300)

```python
import requests
import json

url = "http://localhost:8000/api/register"
payload = {
    "username": "newuser",
    "password": "StrongPass123!",
    "email": "user@example.com",
    "referral_code": "ABC123"  # Optional
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=4))
```

### Authentication
![image](https://github.com/user-attachments/assets/4df88573-883d-484b-903f-eb9b5b676b9f)

```python
import requests

url = "http://localhost:8000/api/login"
data = {
    "username": "newuser",
    "password": "StrongPass123!"
}

response = requests.post(url, data=data)
token = response.json()["access_token"]
print(f"Your access token: {token}")
```

### Getting Referral Statistics
![image](https://github.com/user-attachments/assets/3cadf267-0d57-43ee-b7a2-509b5398ab38)

```python
import requests

url = "http://localhost:8000/api/referral-stats"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
print(json.dumps(response.json(), indent=4))
```

## Security Considerations

This API implements several security best practices:

- Passwords are hashed using bcrypt
- Authentication uses JWT with expiration
- Email validation uses regex pattern matching
- Password strength checking ensures secure passwords
- Temporary passwords are securely generated with entropy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing API framework
- [JWT](https://jwt.io/) for secure token-based authentication
- [bcrypt](https://github.com/pyca/bcrypt/) for password hashing

---

Made with ❤️ by Vansh
