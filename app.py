#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from asyncio.windows_events import NULL
from contextlib import redirect_stderr
from doctest import FAIL_FAST
import sys
from email.policy import default
import json
from os import abort
from tracemalloc import start
from types import CoroutineType
from datetime import datetime
from wsgiref.handlers import format_date_time
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  db_venues = Venue.query.all()
  areas = []
  
  for venue in db_venues:
    if len(areas) == 0:
      area = {
        'city': venue.city,
        'state': venue.state,
        'venues' : [venue]
      }
      areas.append(area)

    else:
      new_area={}
      for area in areas:
        if area['city'] == venue.city and area['state'] == venue.state:
          area['venues'].append(venue)
        
        else:
          new_area['city'] = venue.city
          new_area['state'] = venue.state

      if new_area:
        new_area['venues']= [venue]
        areas.append(new_area)

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = search_term=request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
        "artist_id":show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time": show.start_time
    })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_query:
    upcoming_shows.append({
        "artist_id":show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time": show.start_time
    })  
  
  data = {
    "id" :venue.id,
    "name" :venue.name,
    "genres" :venue.genres,
    "city" :venue.city,
    "state" :venue.state,
    "phone" :venue.phone,
    "address" : venue.address,
    "facebok_link" :venue.facebook_link,
    "website_link" :venue.website,
    "seeking_talent" :venue.seeking_talent,
    "seeking_description" :venue.seeking_description,
    "image_link" :venue.image_link,
    "past_shows" : past_shows,
    "upcoming_shows" : upcoming_shows,
    "past_shows_count" : len(past_shows),
    "upcoming_shows_count" : len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  if  form.validate_on_submit():
    error = False
    try : 
      talent = request.form.get('seeking_talent')
      seeking_talent= False
      if talent == 'y':
        seeking_talent = True

      new_venue = Venue(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        address = request.form.get('address'),
        phone = request.form.get('phone'),
        genres = [request.form.get('genres')],
        facebook_link = request.form.get('facebook_link'),
        image_link = request.form.get('image_link'),
        website = request.form.get('website_link'),
        seeking_talent = seeking_talent,
        seeking_description = request.form.get('seeking_description')
      )

      # on successful db insert, flash success
      db.session.add(new_venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')
  
  else:
    for field,message in form.errors.items():
      flash(field + '-' + str(message), 'danger')
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  error= False
  print('method called')
  try:
    print('deleting')
    print(venue_id)
    venue = Venue.query.get(int(venue_id))
    print(venue)
    db.session.delete(venue)
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be deleted.')
  else:
    return redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = search_term=request.form.get('search_term', '')
  result = Venue.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
        "artist_id":show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "venue_id": show.venue_id,
        "venue_image_link": show.venue_image_link,
        "venue_name": show.venue_name,
        "start_time": show.start_time
    })

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_query:
    upcoming_shows.append({
        "artist_id":show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "venue_id": show.venue_id,
        "venue_image_link": show.venue_image_link,
        "venue_name": show.venue_name,
        "start_time": show.start_time
    })  
  
  data = {
    "id" : artist.id,
    "name" : artist.name,
    "genres" : artist.genres,
    "city" : artist.city,
    "state" : artist.state,
    "phone" : artist.phone,
    "facebok_link" : artist.facebook_link,
    "website_link" : artist.website,
    "seeking_venue" : artist.seeking_venue,
    "seeking_description" : artist.seeking_description,
    "image_link" : artist.image_link,
    "past_shows" : past_shows,
    "upcoming_shows" : upcoming_shows,
    "past_shows_count" : len(past_shows),
    "upcoming_shows_count" : len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    talent = request.form['seeking_venue']
    seeking_venue= False
    
    if talent == 'y':
      seeking_venue = True
     
    seeking_description = request.form.get('seeking_description')

    if seeking_description is NULL:
      seeking_description = ''

    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = [request.form.get('genres')]
    artist.facebook_link = request.form.get('facebook_link')
    artist.website_link = request.form.get('website_link')
    artist.image_link = request.form.get('image_link')
    artist.seeking_talent = seeking_venue
    artist.seeking_description = seeking_description
    
    db.session.add(artist)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
    
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    talent = request.form.get('seeking_talent')
    seeking_talent= False
    seeking_description= ''
    if talent == 'y':
      seeking_talent = True
      seeking_description = request.form.get('seeking_description') or ''

    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = [request.form.get('genres')]
    venue.facebook_link = request.form.get('facebook_link')
    venue.website_link = request.form.get('website_link')
    venue.image_link = request.form.get('image_link')
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    
    db.session.add(venue)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
    
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue could not be updated.')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  if form.validate_on_submit():
    error = False
    try: 
      talent = request.form.get('seeking_venue')
      seeking_venue= False
      if talent == 'y':
        seeking_venue = True
      print(talent)
      new_artist = Artist(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        phone = request.form.get('phone'),
        genres = [request.form.get('genres')],
        facebook_link = request.form.get('facebook_link'),
        image_link = request.form.get('image_link'),
        website = request.form.get('website_link'),
        seeking_venue = seeking_venue,
        seeking_description = request.form.get('seeking_description')
      )
      print(new_artist)
      db.session.add(new_artist)
      db.session.commit()
    except:
      error = True
      print(sys.exc_info)
      db.session.rollback()
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist could not be listed.')
    else:
    # on successful db insert, flash success
      flash('Artist ' + request.form.get('name') + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')

  else:
    for field, message in form.errors.items():
      flash(field+ '-' +str(message), 'danger')
  return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    start_time = request.form.get('start_time')
    new_show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id= request.form.get('venue_id'),
      start_time = start_time
    )

    print(new_show)
    db.session.add(new_show)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  else:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
