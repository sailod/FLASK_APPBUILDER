import requests
from celery import Celery, Task
from celery import shared_task
from .models import Movie
from . import db


def celery_init_app(app) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


@shared_task()
def fetch_movies_data():
    # Set up the endpoint URL and the SPARQL query
    endpoint_url = "https://query.wikidata.org/sparql"
    query = """
        SELECT DISTINCT ?imdb_id ?movieLabel (GROUP_CONCAT(DISTINCT ?genreLabel; SEPARATOR=", ") AS ?genres) (GROUP_CONCAT(DISTINCT ?directorLabel; SEPARATOR=", ") AS ?directors) ?duration $release_date
        WHERE {
            ?movie wdt:P31 wd:Q11424.
            ?movie wdt:P345 ?imdb_id.
            ?movie wdt:P136 ?genre.
            ?movie wdt:P57 ?director.
            ?movie wdt:P577 ?release_date.
            ?movie wdt:P2047 ?duration.
            ?genre rdfs:label ?genreLabel. FILTER (lang(?genreLabel) = "en")
            ?director rdfs:label ?directorLabel. FILTER (lang(?directorLabel) = "en")
            FILTER (YEAR(?release_date) > 2016)
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        GROUP BY ?imdb_id ?movieLabel ?duration ?release_date
    """

    # Set up the HTTP headers for the request
    headers = {"Accept": "application/sparql-results+json", "Cache-Control": "no-cache"}

    # Set up the HTTP parameters for the request
    params = {"query": query}
    # Send the HTTP request to the Wikidata Query Service API endpoint
    response = requests.get(endpoint_url, headers=headers, params=params)

    # Parse the JSON response into a Python object
    results = response.json()["results"]["bindings"]
    ingest_movies(results)


def ingest_movies(movies):
    # Print the results
    count = 0

    for movie_record in movies:
        try:
            name = movie_record.get("movieLabel", {"value": "notFound"})["value"]
            duration = movie_record.get("duration", {"value": "notFound"})["value"]
            genres = movie_record.get("genres", {"value": "notFound"})["value"]
            directors = movie_record.get("directors", {"value": "notFound"})["value"]
            imdb_id = movie_record.get("imdb_id", {"value": "notFound"})["value"]
            release_date = movie_record.get("release_date", {"value": "notFound"})[
                "value"
            ]
            print(f"adding movie {name} with id {imdb_id}")
            movie = Movie(
                id=imdb_id,
                name=name,
                directors=directors,
                genres=genres,
                duration=duration,
                release_date=release_date,
            )
            db.session.merge(movie)
            db.session.commit()
            count += 1
        except Exception as err:
            print(f"failed to process {movie_record}: {err}")
    print(f"finished upserting {count} movies to DB")
