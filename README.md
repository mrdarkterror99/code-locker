USE THIS TO RETRIEVE SNIPPETS : 

R LANUAGE : 

library(httr)
library(jsonlite)


SERVER_URL <- "https://code-locker-99.onrender.com"


get_code <- function(unique_name) {
  url <- paste0(SERVER_URL, "/get_code/", URLencode(unique_name, reserved = TRUE))
  response <- GET(url)
  content <- fromJSON(content(response, "text", encoding = "UTF-8"))
  cat(content$code)
}


get_code("SM")



PYTHON LANGUAGE : 

import requests

def get_code(unique_name):
    SERVER_URL = "https://code-locker-99.onrender.com"
    url = f"{SERVER_URL}/get_code/{unique_name}"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        print(response.json()['code'])
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

get_code("your_unique_name")
