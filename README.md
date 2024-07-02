# GlucoseMonitorAPI

## Overview
GlucoseMonitorAPI is a Django-based backend service for storing and retrieving blood glucose levels. It provides endpoints for querying, filtering, and exporting glucose data. Features include pagination, sorting, data pre-population via API, and export to JSON, CSV, and Excel.

## API Endpoints

### Retrieve a list of glucose levels
- **URL:** `/api/v1/levels/`
- **Method:** `GET`
- **Description:** Retrieves a list of glucose levels for a given `user_id`, with optional filtering by `start` and `stop` timestamps. Supports pagination, sorting, and limiting the number of glucose levels returned.
- **Parameters:**
  - `user_id` (UUID, required)
  - `start` (DateTime, optional)
  - `stop` (DateTime, optional)
  - `page` (int, optional)
  - `page_size` (int, optional)
  - `ordering` (string, optional) - Order by `glucose_history_mg_dl`, `glucose_scan_mg_dl`, or `device_timestamp`
- **Example Request:**

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/levels/?user_id=<user_uuid>&start=2023-01-01T00:00:00Z&stop=2023-01-31T23:59:59Z&ordering=device_timestamp"
```

### Retrieve a specific glucose level

- **URL:** `/api/v1/levels/<id>/`
- **Method:** `GET`
- **Description:** Retrieves a particular glucose level by `id`.
- **Example Request:**
    
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/levels/1/"    
```
    

### Upload glucose levels via CSV

- **URL:** `/api/v1/levels/upload/`
- **Method:** `POST`
- **Description:** Uploads a CSV file to populate the glucose levels in the database.
- **Parameters:**
    - `file` (File, required) - CSV file containing glucose data
- **Example Request:**
    
```bash
curl -X POST -F "file=@path_to_file.csv" "http://127.0.0.1:8000/api/v1/levels/upload/"
```
    

### Retrieve minimal and maximum glucose levels

- **URL:** `/api/v1/levels/aggregates/minmax/`
- **Method:** `GET`
- **Description:** Retrieve minimal and maximum glucose levels for  a given `user_id`, with optional filtering by `start` and `stop` timestamps. 
- **Parameters:**
  - `user_id` (UUID, required)
  - `start` (DateTime, optional)
  - `stop` (DateTime, optional)
- **Example Request:**
    
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/levels/aggregates/minmax/?user_id=<user_uuid>&start=2023-01-01T00:00:00Z&stop=2023-01-31T23:59:59Z"
```

## Commands

### Load Sample Data from CSV

To load sample data from a CSV file into the Level model, you can use the custom management command `load_sample_data`. This command processes the CSV file and populates the database with the glucose data.

**Command:**

```bash
python manage.py load_sample_data <path_to_csv_file> --chunk_size=<chunk_size>
```

**Example:**

```bash
python manage.py load_sample_data sample_data/aaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa.csv --chunk_size=10000
```

## Running Auto-tests

To run the automated tests, you can use `pytest`. Make sure you have all the dependencies installed and the Docker services running.

**Command:**

```bash
pytest .
```

## Local Development Setup

### Prerequisites

- Docker
- Docker Compose

### Steps to Deploy Locally

1. **Clone the Repository**
    
    ```bash
    git clone <repository_url>
    cd glucose-monitor-api
    ```
    
2. **Set Up Environment Variables**
    - Create a `.env` file in the root directory with the following content:
        
    ```
    SECRET_KEY=<your_secret_key>
    DEBUG=True
    DB_NAME=glucose-monitor
    DB_USER=django-dev
    DB_PASSWORD=django-dev
    DB_HOST=db
    DB_PORT=5432 
    ```
        
3. **Build and Run Docker Containers**
    
    ```bash
    docker-compose up --build
    ```

5. **Load Sample Data (Optional)**
    - You can load sample data using the custom management command as described in the Commands section.
6. **Access the Application**
    - The application should be running at `http://127.0.0.1:8000/`.
7. **Access Adminer**
    - You can access Adminer at `http://127.0.0.1:8080/` to manage your database.
