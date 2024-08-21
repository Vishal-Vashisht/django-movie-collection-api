# Django Movie Collection API

## Overview

This is a Django-based API for managing movie collections. The API allows users to create, update, list, and delete movie collections. Each collection can have multiple movies associated with it. The API also implements JWT authentication for securing endpoints.

## Features

- JWT authentication for secure access
- Create, update, list, and delete movie collections
- List movies in a collection
- Pagination for movie listing
- Scalable request count middelware
## Setup and Installation

### Prerequisites

- Python 3.8+
- Django 3.2+
- virtualenv (optional but recommended for managing virtual environments)
- Docker (optional for containerized setup)

### Clone the Repository

```sh
git clone git@github.com:Vishal-Vashisht/django-movie-collection-api.git
cd django-movie-collection-api


python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Create a .env file in the project root and add the following environment variables:
```sh
# development # production
# Leave this field blank for default setting
ENVIRONMENT = 

# For testing can use this otherwise change this
SECRET_KEY = 'django-insecure-8yjg1)b$2=6gpv6)62)re+-t*)8o0w%#j6o=nqyzcw3j7%sk(q'

# Get the below variables from Example env file document
MOVIE_API = 
MOVIE_API_PASSWORD =
MOVIE_API_USERNAME = 

# If using docker can set to 'redis' for in memory leave the field blank
CACHE_BACKEND =

```

### Apply the migrations
```sh
python manage.py makemigrations
python manage.py migrate

```

### Run the Development server
```sh
python manage.py runserver
```
### Run test
```sh
Python manage.py test
```
## Build with docker

- Create .env file as mentioned in above step

### Run the below command in directory where docker-compose file is located
```sh
docker-compose up --build

```
### Kill container
```sh

docker-compose down

```

### Up the container
```
docker-compose up

```
```sh
API Endpoints

----------------------------------- Collections -----------------------------------

    - GET /collections/ - List all collections
      
      Response

        {
            "is_success": true,
            "data": {
                "collections": [
                    {
                        "uuid": "77e4a5a4-bf6a-468e-a8c8-d8b6ca25dd2f",
                        "title": "Queerama",
                        "description": "50 years after decriminalisation."
                    }
                ],
                "favourite_genres": [
                    "Action"
                ]
            }

    - POST /collections/ - Create a new collection
      
      Payload:

        {
            "title": "Queerama update 3",
            "description": "50 years after decriminalisation.",
            "movies": [
            {
                "uuid": "1c4f88ee-aafb-4fa1-8f55-6d12696dc02f",
                "title": "Queerama update",
                "description": "50 years after decriminalisation.",
                "genres": "Action"
            }]
                    
        }

      Response:
        
        {
            “collection_uuid”: <uuid of the collection item>
        }




    - GET /collections/<uuid>/ - Retrieve a collection by UUID

        Response
         
        {
            "uuid": "77e4a5a4-bf6a-468e-a8c8-d8b6ca25dd2f",
            "title": "Queerama",
            "description": "50 years after decriminalisation.",
            "movies": []
        }

    - PUT /collections/<uuid>/ - Update a collection by UUID

        Payload
        {
            "title": "Queerama Updated",
            "description": "50 years after decriminalisation of homosexuality in the UK",
            "movies": []
        }

        Response

        {
            "title": "Queerama Updated",
            "description": "50 years after decriminalisation of homosexuality in the UK",
            "movies": []
        }

    - DELETE /collections/<uuid>/ - Delete a collection by UUID

----------------------------------- Register -----------------------------------
    - POST /register/
        Payload 
            {
                "username":"username",
                "password":"password"
            }
        Response
            {
                “access_token”: <Access Token>
            }

----------------------------------- Movies -----------------------------------
    - GET /movies/
    
        Response
        {
            "count": 45466,
            "next": "http://127.0.0.1:8000/movies/?page=2",
            "previous": null,
            "results": [
                {
                    "title": "Queerama",
                    "description": "50 years after decriminalisation.",
                    "genres": "Action",
                    "uuid": "57baf4f4-c9ef-4197-9e4f-acf04eae5b4d"
                }
            ]
        }

----------------------------------- Requests -----------------------------------

    - Get  /request-count/
        Response:
        {
            “requests”: <number of requests served by this server till now>.
        }

    - POST /request-count/reset/

        Response:
        {
            “message”: “request count reset successfully”
        }

```