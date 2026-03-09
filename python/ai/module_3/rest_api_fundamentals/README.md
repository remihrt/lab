# FastAPI Books API Documentation

## Overview

This is a simple REST API for managing books. It demonstrates basic REST principles and Pydantic validation using FastAPI.

A REST API is a way for computers to communicate over the internet by sending requests to URLs (endpoints) using standard HTTP methods like GET (fetch data) and POST (create data).

## API Endpoints

### List All Books
**GET** `/books`

Retrieves all books in the library.

```bash
curl http://localhost:8000/books
```

Example Response:
```json
[
  {
    "id": 1,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "pages": 180
  }
]
```

### Create a New Book
**POST** `/books`

Creates a new book entry.

#### Valid Request Example
```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "pages": 180
  }'
```

Success Response (Status 201):
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "pages": 180
}
```

## Error Examples

### Invalid Data Type
When sending invalid data types (e.g., string for pages instead of integer):

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "pages": "180"
  }'
```

Error Response (Status 422):
```json
{
  "detail": [
    {
      "type": "integer_type",
      "loc": ["body", "pages"],
      "msg": "Input should be a valid integer"
    }
  ]
}
```

### Missing Required Field
When omitting a required field (e.g., author):

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "pages": 180
  }'
```

Error Response (Status 422):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "author"],
      "msg": "Field required"
    }
  ]
}
```

## Running the API

1. Using Python directly:
```bash
pip install fastapi uvicorn pydantic
python main.py
```

2. Using Docker Compose:
```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`, and the interactive documentation can be accessed at `http://localhost:8000/docs`.