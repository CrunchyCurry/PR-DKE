# PR-DKE (instructions pending)

## Prerequisite

The ```FLASK_APP``` environment variable has to be set to run the application.

1. Open the terminal in the root of the project.
2. Set the ```FLASK_APP``` environment variable to ```railway_system```. For Linux use:
```
export FLASK_APP=railway_system
```
You can check if the environment variable has been successfully set by printing it with ```echo $FLASK_APP```.

## Run the project

In the same terminal, start the application by running:
```
flask run
```

Environment varibles are only valid for that terminal session. 

If you want to re-run the application, you do not have to repeat the first two steps as long as you do not close the terminal.
