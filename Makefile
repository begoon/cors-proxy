.PHONY: shell

APP=cors-filter
BINDING=127.0.0.1:5000

all:

run:
	gunicorn wsgi:application --reload --bind $(BINDING) --chdir src/

logs:
	HEROKU_APP=$(APP) heroku logs --tail

shell:
	HEROKU_APP=$(APP) heroku ps:exec 

ps:
	HEROKU_APP=$(APP) heroku ps

info:
	HEROKU_APP=$(APP) heroku apps:info

set-web-concurrency:
	HEROKU_APP=$(APP) heroku config:set WEB_CONCURRENCY=1

get-web-concurrency:
	HEROKU_APP=$(APP) heroku config:get WEB_CONCURRENCY
