from flask import jsonify, render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, BaseView, expose
from .utils import fetch_movies_data
from .models import Movie
from . import appbuilder, db


class MoviesView(ModelView):
    datamodel = SQLAInterface(Movie)
    list_columns = ["name", "genres", "directors", "duration", "release_date"]


class OperationsView(BaseView):
    route_base = "/operations"
    default_view='fetch_movies'

    @expose("/fetch_movies")
    def fetch_movies(self):
        try:
            task_id = fetch_movies_data.delay()

            return (
                jsonify(
                    {
                        "message": f"launched new movies data fetch, task ID in the background: {task_id}"
                    }
                ),
                202,
            )
        except Exception as err:
            return (
                jsonify(
                    {"error": f"failed to fetch movies records from wiki data: {err}"}
                ),
                206,
            )

    @expose("/fetch_status/<string:fetch_task_id>")
    def fetch_status(self, fetch_task_id):
        try:
            task = fetch_movies_data.AsyncResult(fetch_task_id)
            return (
                jsonify({"message": f"status of task: {task.status}"}),
                202,
            )
        except Exception as err:
            return (
                jsonify(
                    {"error": f"failed to fetch movies records from wiki data: {err}"}
                ),
                206,
            )


db.create_all()
appbuilder.add_view(MoviesView, "Show stored movies")

appbuilder.add_view(OperationsView, "Fetch Movies From Wiki Data ")



@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
