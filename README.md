# [PR-DKE] Strecken-Informationssystem SIS

## Prerequisite

```Python 3.8``` and ```pip``` (usually already bundled with Python) are needed to run this project. Instructions are Linux specific.

Open the terminal and set the root of the project as the working directory or simply open the terminal in the root of the project. 

Install dependencies by running (preferably using a virtual environment):
```
pip install -r requirements.txt
```

## Run the application

In the same terminal, start the application by running:
```
flask run
```

If needed, a specific port for the app can be assigned.
E.g. in order to run the app on port ```8080```, run:

```
flask run --port=8080
```

Done!


## API access

Information about railways, sections, stations and warnings can be requested through API endpoints.


> To request information about an item with a specific id:
```
/get-{item}/{id}
```


> To request information about all (similar) items:
```
/get-{item}s
```
 

<br/>

E.g. in order to request information about the railway with ID 1, use the endpoint:

```
/get-railway/1
```

And to request information about all railways, use the endpoint:

```
/get-railways
```


