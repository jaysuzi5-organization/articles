# Documentation for articles
### fastAPI: manages RSS article summary including rating of relevance and urgency


This application has two generic endpoints:

| Method | URL Pattern           | Description             |
|--------|-----------------------|--------------------|
| GET    | /api/v1/articles/info         | Basic description of the application and container     |
| GET    | /api/v1/articles/health    | Health check endpoint     |



## CRUD Endpoints:
| Method | URL Pattern           | Description             | Example             |
|--------|-----------------------|--------------------|---------------------|
| GET    | /api/v1/articles         | List all articles     | /api/v1/articles       |
| GET    | /api/v1/articles/{id}    | Get articles by ID     | /api/v1/articles/42    |
| POST   | /api/v1/articles         | Create new articles    | /api/v1/articles       |
| PUT    | /api/v1/articles/{id}    | Update articles (full) | /api/v1/articles/42    |
| PATCH  | /api/v1/articles/{id}    | Update articles (partial) | /api/v1/articles/42 |
| DELETE | /api/v1/articles/{id}    | Delete articles        | /api/v1/articles/42    |


### Access the info endpoint
http://home.dev.com/api/v1/articles/info

### View test page
http://home.dev.com/articles/test/articles.html

### Swagger:
http://home.dev.com/api/v1/articles/docs