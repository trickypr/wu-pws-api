# wu-pws-api
A python API for uploading data from your personal weather station to Weather Underground

## Instalation
TODO: Upload to pypi.

Currently, if you are using git for your project, you can add this repository as a submodule. 

``` sh
git submodule add https://github.com/trickypr/wu-pws-api api
git add api
git commit -m "Add wu pws api"
```

Then you can import it into your code like this:

``` python
from api import API

api = API(key, password)
```

## Example
If you want an example of how you would implement this in one of your projects, check out [`pws-app`](https://github.com/trickypr/pws-app). This is a raspberry pi program that will upload data to weather underground.

