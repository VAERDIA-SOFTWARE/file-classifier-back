# API Documentation

This is the documentation for the Flask API. The API provides endpoints
to manage files, categories, and societes in a MySQL database.

## Table of Contents

- [Home](#home)
- [Create Files](#create-files)
- [GetFiles](#get-files)
- [Export Sheet](#export-sheet)
- [GetCategories](#get-categories)
- [Get Societes](#get-societes)

## Home

### Description

This endpoint is used to check if the API is running successfully.

- **URL**: `/`
- **Method**: GET
- **Response**: "Home"

### Example

``` GET / ```

## Create Files

### Description

This endpoint is used to create new files in the database.

- **URL**: `/files`
- **Method**: POST
- **RequestBody**: Array of file objects
  - `path` (string): The file path 
  - `date` (string): The file date
  - `name` (string): The file name 
  - `adresse` (string): The file adresse
  - `societe` (string): The file societe
  - `categorie` (string, optional): The file categorie
  - `phone_number` (string, optional): The file phone number
- **Response**: JSON object with a message indicating the status of the operation

### Example

```json POST /files

Request Body: [
    { 
    "path": "/path/to/file1", 
    "date":"2023-06-09", 
    "name": "File 1",
    "adresse": "Address 1",
    "societe": "Societe 1",
    "categorie": "Category 1",
    "phone_number": "1234567890" }, 
    {
    "path": "/path/to/file2",
    "date": "2023-06-10",
    "name": "File 2",
    "adresse": "Address2",
    "societe": "Societe 2",
    "categorie": "Category 2",
    "phone_number": "0987654321" } ]
 ```

## Get Files

### Description

This endpoint is used to retrieve files from the database.

- **URL**: `/files`  $
- **Method**: GET - **QueryParameters**:  
  - `query` (string, optional): Search query to filterfiles
  - `categorie` (string, optional): Filter files by categorie
  - `societe` (string, optional): Filter files by societe
  - `page`(integer, optional): Page number for pagination (default: 1)
  - `per_page` (integer, optional): Number of items per page (default:1)
  
- **Response**: JSON object with the list of files and pagination information

### Example

``` GET /files?query=keyword&categorie=Category&page=1&per_page=10
```

## Export Sheet

### Description

This endpoint is used to export files as an Excel sheet.

- **URL**: `/files/exportsheet`
- **Method**: GET - **QueryParameters**:
  - `query` (string, optional): Search query to filterfiles
  - `categorie` (string, optional): Filter files by categorie
  - `societe` (string, optional): Filter files by societe -
- **Response**: Excel file attachment

### Example

``` GET /files/exportsheet?query=keyword&categorie=Category ```

## Get Categories

### Description

This endpoint is used to retrieve the list of categories

from the database.

- **URL**: `/categories`
- **Method**: GET
- **Response**: JSON array with the list of categories

### Example

``` GET /categories ```

## Get Societes

### Description

This endpoint is used to retrieve the list of societes from the
database.

- **URL**: `/societes`
- **Method**: GET
- **Response**: JSON array with the list of societes

### Example

``` GET /societes ```
