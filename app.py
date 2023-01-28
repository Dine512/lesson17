# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)



api = Api(app)
movies_ns = api.namespace('movies')
movie_ns = api.namespace('movie')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')
api.app.config["RESTX_JSON"] = {"ensure_ascii": False}


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")

        if director_id is not None and genre_id is not None:
            with app.app_context():
                all_movies_query = Movie.query.filter(Movie.director_id == director_id, Movie.genre_id == genre_id).all()

        elif director_id is not None:
            with app.app_context():
                all_movies_query = Movie.query.filter(Movie.director_id == director_id).all()

        elif genre_id is not None:
            with app.app_context():
                all_movies_query = Movie.query.filter(Movie.genre_id == genre_id).all()
        else:
            with app.app_context():
                all_movies_query = Movie.query.all()

        return movies_schema.dump(all_movies_query), 200


@movie_ns.route('/<int:id_movie>')
class MoviesView(Resource):
    def get(self, id_movie: int):
        with app.app_context():
            movie_query = Movie.query.get(id_movie)
        return movie_schema.dump(movie_query), 200


@director_ns.route('/')
class DirectorPostView(Resource):
    def post(self):
        new_director = Director(name=request.form['name'])
        with app.app_context():
            db.session.add(new_director)
            db.session.commit()


@director_ns.route('/<int:director_id>')
class DirectorView(Resource):
    def put(self, director_id):
        with app.app_context():
            director = Director.query.get(director_id)
            director.name = request.form['name']
            db.session.add(director)
            db.session.commit()

    def delete(self, director_id):
        with app.app_context():
            director = db.session.query(Director).get(director_id)
            db.session.delete(director)
            db.session.commit()


@genre_ns.route('/')
class GenrePostView(Resource):
    def post(self):
        new_genre = Genre(name=request.form['name'])
        with app.app_context():
            db.session.add(new_genre)
            db.session.commit()

@genre_ns.route('/<int:genre_id>')
class GenreView(Resource):
    def put(self, genre_id):
        with app.app_context():
            genre = db.session.query(Genre).get(genre_id)
            genre.name = request.form['name']
            db.session.add(genre)
            db.session.commit()

    def delete(self, genre_id):
        with app.app_context():
            genre = db.session.query(Genre).get(genre_id)
            db.session.delete(genre)
            db.session.commit()






if __name__ == '__main__':
    app.run(debug=True)
