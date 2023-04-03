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


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        res = request.values.to_dict()
        print(res)
        if res:
            if 'director_id' in res:
                movies_by_director = Movie.query.filter(Movie.director_id == res['director_id'])
                return movies_schema.dump(movies_by_director), 200
            elif 'genre_id' in res:
                print(res['genre_id'])
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


if __name__ == '__main__':
    app.run(debug=True)
