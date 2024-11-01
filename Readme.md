Here's a well-structured `README.md` file for your project:

---

# KPI Management Project

This project is a Django-based application designed to manage Key Performance Indicators (KPIs), ingest and process messages from assets, and link assets to KPIs. The project features a RESTful API with Swagger documentation and supports operations like creating and listing KPIs, ingesting messages, linking assets to KPIs, and updating a configuration file with new equations.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Configuration](#configuration)
- [Swagger API Documentation](#swagger-api-documentation)
- [Project Structure](#project-structure)
---

## Project Overview
This application manages KPIs and processes messages sent from various assets. It supports the creation and management of KPIs, linking assets to KPIs, and processing messages using customizable equations defined in a configuration file.

## Features
- **Create and List KPIs**: Manage KPIs with flexible expressions.
- **Ingest Messages**: Process incoming messages from assets and store the results in the database.
- **Link Assets to KPIs**: Associate assets with KPIs.
- **Update Configuration**: Modify equations dynamically through an API endpoint.

---

## Technologies Used
- **Django**: Web framework for rapid development and clean, pragmatic design.
- **Django REST Framework (DRF)**: Powerful toolkit for building Web APIs.
- **drf-yasg**: Swagger/OpenAPI Documentation Generator.
- **SQLite**: Default development database.
- **Python**: Core programming language.

---

## Setup and Installation

### Prerequisites
- **Python 3.8+**: Ensure you have Python installed on your system.
- **pip**: Python package manager.

### Installation Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/hassaangamal/Software-task.git
   cd kpi-management
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   ```
   - **On Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **On macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

---

## Running the Project
1. Access the API at `http://127.0.0.1:8000/`.
2. Use the Django admin panel at `http://127.0.0.1:8000/admin/` for backend management (login with your superuser credentials).

---

## API Endpoints

### 1. KPI Management
- **GET /kpis/**: List all KPIs.
- **POST /kpis/**: Create a new KPI.

### 2. Message Ingestion
- **POST /messages/ingest/**: Ingest a message, process it, and save the result.

### 3. Link Asset to KPI
- **POST /kpis/link-asset/**: Link an asset to a KPI.

### 4. Update Configuration
- **POST /config/update/**: Update the equation in the configuration file.

---

## Testing
Run the test suite using:
```bash
python manage.py test
```

### Example Test Cases
- **Ingest Message Tests**: Validates message ingestion, handling of missing fields, and invalid formats.
- **KPI Tests**: Tests for creating, listing, and validating unique KPI names.
- **Link Asset Tests**: Tests for successful and unsuccessful linking of assets to KPIs.
- **Configuration Tests**: Tests for updating and validating equations in the config file.

---

## Configuration
- The equation used for processing messages is stored in a `config.json` file.
- **Default Location**: `config.json` in the project root directory.
- **Example Structure**:
  ```json
  {
      "equation": "ATTR + 5"
  }
  ```

---

## Swagger API Documentation
Swagger documentation is provided to help users understand and test the API endpoints.

### Accessing Swagger UI
1. Start the server:
   ```bash
   python manage.py runserver
   ```
2. Visit `http://127.0.0.1:8000/swagger/` for the interactive API documentation.
3. Visit `http://127.0.0.1:8000/redoc/` for an alternative documentation format.

---

## Project Structure
- **kpi/**: Contains the core application files.
  - **models.py**: Defines the data models (KPI, Asset, Message).
  - **views.py**: Contains API views for handling requests.
  - **serializers.py**: Serializers for converting data to and from JSON.
  - **test.py**: Unit tests for the application.
- **config.json**: Configuration file for equations.
- **requirements.txt**: List of dependencies.
- **manage.py**: Django management script.

