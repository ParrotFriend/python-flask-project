import requests

def main():
    #gets users from api
    URL= "http://127.0.0.1:2224/users"

    # Get request to url and stores repsonse
    response = requests.get(URL)

    # turns response to python object
    users = response.json()
    
    #prints users in database
    print(users)

if __name__ == "__main__":
        main()