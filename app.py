# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    id = fields.Integer(dump_only=True)
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.Float()
    genre_id = fields.Integer()
    director_id = fields.Integer()


class DirectorSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


class GenreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        res = request.values.to_dict()
        if res:
            if 'director_id' in res:
                movies_by_director = Movie.query.filter(Movie.director_id == res['director_id'])
                return movies_schema.dump(movies_by_director), 200
            elif 'genre_id' in res:
                movies_by_genre = Movie.query.filter(Movie.genre_id == res['genre_id'])
                return movies_schema.dump(movies_by_genre), 200
        else:
            all_movies = Movie.query.all()
            return movies_schema.dump(all_movies), 200


    def post(self):
        movie_json = request.json
        new_movie = Movie(**movie_json)

        with db.session.begin():
            db.session.add(new_movie)
            return '', 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid: int):
        try:
            movie_by_id = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(movie_by_id), 200
        except Exception as e:
            return str(e), 404


    def put(self, mid: int):
        try:
            update_movie = db.session.query(Movie).filter(Movie.id == mid).one()
            movie_json = request.json

            update_movie.title = movie_json.get('title')
            update_movie.description = movie_json.get('description')
            update_movie.trailer = movie_json.get('trailer')
            update_movie.year = movie_json.get('year')
            update_movie.rating = movie_json.get('rating')
            update_movie.genre_id = movie_json.get('genre_id')
            update_movie.director_id = movie_json.get('director_id')

            db.session.add(update_movie)
            db.session.commit()
            return '', 204
        except Exception as e:
            print(e)
            return str(e), 404


    def delete(self, mid: int):
        try:
            movie = Movie.query.get(mid)
            db.session.delete(movie)
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return directors_schema.dump(all_directors), 200


    def post(self):
        director_json = request.json
        new_director = Director(**director_json)

        with db.session.begin():
            db.session.add(new_director)
            return '', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did: int):
        try:
            director_by_id = db.session.query(Director).filter(Director.id == did).one()
            return director_schema.dump(director_by_id), 200
        except Exception as e:
            return str(e), 404


    def put(self, did: int):
        try:
            update_director = db.session.query(Director).filter(Director.id == did).one()
            director_json = request.json

            update_director.name = director_json.get('name')

            db.session.add(update_director)
            db.session.commit()
            return '', 204
        except Exception as e:
            print(e)
            return str(e), 404


    def delete(self, did: int):
        try:
            director = Director.query.get(did)
            db.session.delete(director)
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return genres_schema.dump(all_genres), 200


    def post(self):
        genre_json = request.json
        new_genre = Genre(**genre_json)

        with db.session.begin():
            db.session.add(new_genre)
            return '', 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid: int):
        try:
            genre_by_id = db.session.query(Genre).filter(Genre.id == gid).one()
            return genre_schema.dump(genre_by_id), 200
        except Exception as e:
            return str(e), 404


    def put(self, gid: int):
        try:
            update_genre = db.session.query(Genre).filter(Genre.id == gid).one()
            genre_json = request.json

            update_genre.name = genre_json.get('name')

            db.session.add(update_genre)
            db.session.commit()
            return '', 204
        except Exception as e:
            print(e)
            return str(e), 404


    def delete(self, gid: int):
        try:
            genre = Genre.query.get(gid)
            db.session.delete(genre)
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
