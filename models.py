
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime)

  @hybrid_property
  def artist_image_link(self):
    artist = Artist.query.get(self.artist_id)
    return artist.image_link
    
  @hybrid_property
  def artist_name(self):
    artist = Artist.query.get(self.artist_id)
    return artist.name
     
  @hybrid_property
  def venue_image_link(self):
    venue = Venue.query.get(self.artist_id)
    return venue.image_link

  @hybrid_property
  def venue_name(self):
    venue = Venue.query.get(self.artist_id)
    return venue.name

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.PickleType())
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', cascade="all, delete")
  
    @hybrid_property
    def upcoming_shows(self):
      list_of_shows = []
      now = datetime.now()
      list_of_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==self.id).where(Show.start_time > now).all()
      print(list_of_shows)
      return list_of_shows

    @hybrid_property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)
      
    @hybrid_property
    def past_shows(self):
      list_of_shows = []
      now = datetime.now()
      list_of_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==self.id).where(Show.start_time < now).all()
      return list_of_shows

    @hybrid_property
    def past_shows_count(self):
      return len(self.past_shows) 

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.PickleType())
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', collection_class=list)


    @hybrid_property
    def upcoming_shows(self):
      list_of_shows = []
      now = datetime.now()
      list_of_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==self.id).where(Show.start_time > now).all()
      print(list_of_shows)
      return list_of_shows

    @hybrid_property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)

    @hybrid_property
    def past_shows(self):
      list_of_shows = []
      now = datetime.now()
      list_of_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==self.id).where(Show.start_time < now).all()
      return list_of_shows
    
    @hybrid_property
    def past_shows_count(self):
      return len(self.past_shows)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
