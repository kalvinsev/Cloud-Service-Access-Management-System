# Cloud Service Access Management System

A backend system built with FastAPI and MongoDB that enforces role-based access control (RBAC) and subscription-based quotas on simulated cloud service endpoints.

## Tech Stack

* **FastAPI** for the web framework
* **Pydantic v2** for data validation and schema generation
* **MongoDB** (Motor AsyncIOMotorClient) for data storage
* **JWT (jose)** for authentication
* **passlib.bcrypt** for password hashing
* **AsyncIO** for asynchronous operations

## Setup & Run

1. **Clone the repository**

   ```bash
   git clone <your repo
   cd cloud_access_mgmt
   ```
2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** in the project root. You need a running MongoDB instance—either locally or via Atlas.

   * **Local MongoDB** (no authentication):

     ```ini
     MONGO_URI=mongodb://localhost:27017/cloud_gateway_proj
     JWT_SECRET=your-very-secret-key
     ```

   * **MongoDB Atlas** (with authentication):

     ```ini
     MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/cloud_gateway_proj?retryWrites=true&w=majority
     JWT_SECRET=your-very-secret-key
     ```

   Replace `<username>` and `<password>` with the credentials for your Atlas database user.
5. **Start the server**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. **Open** `http://localhost:8000/docs` for Swagger UI

## Authentication

* **`POST /auth/token`**

  * **Body (x‑www‑form‑urlencoded)**: `username`, `password`
  * **Response**: `{ "access_token": "<JWT>", "token_type": "bearer" }`
  * Use the returned token in `Authorization: Bearer <JWT>` for all protected endpoints.

## API Endpoints

### Built‑in Services & Permissions

| Permission Name | Endpoint                  | Description         |
| --------------- | ------------------------- | ------------------- |
| `compute`       | `/services/compute`       | Simulated compute   |
| `storage`       | `/services/storage`       | Simulated storage   |
| `email`         | `/services/email`         | Simulated e-mail    |
| `analytics`     | `/services/analytics`     | Simulated analytics |
| `search`        | `/services/search`        | Simulated search    |
| `notifications` | `/services/notifications` | Simulated alerts    |

## API Endpoints

### Users (Admin only)

* **`POST /users`**

  * Create a new user
  * **Body**: `{ "username": string, "password": string, "role": "admin"|"customer" }`
  * **Response**: `{ "_id": string, "username": string, "role": string }`

### Permissions (Admin only)

* **`POST /permissions`**
* **`GET /permissions`**
* **`GET /permissions/{permission_id}`**
* **`PUT /permissions/{permission_id}`**
* **`DELETE /permissions/{permission_id}`**

Each permission record has:

```json
{ "_id": string, "name": string, "endpoint": string, "description": string }
```

### Plans (Admin only)

* **`POST /plans`**
* **`GET /plans`**
* **`GET /plans/{plan_id}`**
* **`DELETE /plans/{plan_id}`**

Each plan record has:

```json
{
  "_id": string,
  "name": string,
  "description": string,
  "permissions": [string],    // list of permission IDs
  "limits": { <permission_name>: number, ... }
}
```

### Subscriptions

* **`POST /subscriptions`** (Customer)

  * Subscribe the current user to a plan
  * **Body**: `{ "plan_id": string }`
  * **Response**: subscription object

* **`GET /subscriptions/me`** (Customer)

  * View your subscription details

* **`GET /subscriptions`** (Admin)

  * List all subscriptions

* **`PUT /subscriptions/{user_id}`** (Admin)

  * Assign or change a user’s plan

### Services (Customer)

* **`GET /services/{service_name}`**

  * Simulate a cloud service call
  * Enforces per-month quota defined in the user's plan
  * **Response**:

    ```json
    {
      "service": string,
      "usage_this_month": number,
      "data": string
    }
    ```

### Access Check (Customer)

* **`GET /access/{service_name}`**

  * Check if the user has permission and quota
  * **Response**:

    ```json
    {
      "service": string,
      "allowed": boolean,
      "limit": number,
      "used": number
    }
    ```

### Usage (Reporting)

* **`GET /usage/me`** (Customer)

  * List your usage records

* **`GET /usage`** (Admin)

  * List all usage records

Each record:

```json
{
  "_id": string,
  "user_id": string,
  "permission_name": string,
  "count": number,
  "last_reset": ISO8601 datetime
}
```

## Testing

Use Postman or curl. Set environment variables for:

* `base_url` → `http://localhost:8000`
* `token_admin`, `token_user`
* `perm_<name>_id`, `plan_id`

Example flow:

1. **POST /auth/token** (admin) → save `token_admin`
2. **POST /permissions** → capture `perm_<name>_id`
3. **POST /plans** → capture `plan_id`
4. **POST /users** (admin) → create customer
5. **POST /auth/token** (customer) → save `token_user`
6. **POST /subscriptions** → subscribe customer
7. **GET /services/{name}** → test quota enforcement
8. **GET /access/{name}**, **GET /usage/me**, **GET /usage**

## Contributors

Kalvin Sevillano
 

---

*This README was generated as part of the Cloud Service Access Management System.*

## .gitignore Recommendations

Add a `.gitignore` file in your repo root to prevent committing generated files and sensitive data. Example `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*.egg
*.egg-info/

# Virtual environment
env/
.venv/

# IDE settings
.vscode/

# Environment variables
.env

# MacOS
.DS_Store
```
