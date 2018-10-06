from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    url_for,
    flash,
    redirect
)
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Category, Item

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Test"

engine = create_engine('sqlite:///catagory.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# print JSON Response.
@app.route('/catalog.json')
def categoryJSON():
    categories = session.query(Category).all()

    jsonData = [category.serialize for category in categories]

    for index, category in enumerate(categories):
        items = session.query(Item).filter_by(category_id=category.id).all()
        jsonData[index]['Item'] = [item.serialize for item in items]

    return jsonify(Category=jsonData)

@app.route('/<categoryName>.json')
def itemJSON(categoryName):
    categoryId = session.query(Category).filter_by(name=categoryName).one().id
    items = session.query(Item).filter_by(category_id=categoryId).all()

    jsonData = [item.serialize for item in items]

    return jsonify(Item=jsonData)

# print Default Page.
@app.route('/')
@app.route('/catalog')
def default():
    categories = session.query(Category).all()
    rows = []

    for item, category in session. \
            query(Item, Category). \
            filter(Item.category_id == Category.id). \
            all():
        rows.append((item, category))

    return render_template('main.html', categories=categories, rows=rows)


# Show Category by Item.
@app.route('/catalog/<categoryName>/items')
def showCategory(categoryName):
    categories = session.query(Category).all()
    categoryByName = session.query(Category).filter_by(name=categoryName).one()
    items = session.query(Item). \
        filter_by(category_id=categoryByName.id).all()

    return render_template(
        'categoryItem.html',
        categories=categories,
        categoryByName=categoryByName,
        items=items)


# Show Item Detail.
@app.route('/catalog/<categoryName>/<itemTitle>')
def showItem(categoryName, itemTitle):
    categoryByName = session.query(Category).filter_by(name=categoryName).one()
    itemByTitle = session.query(Item).filter(
        and_(Item.category_id == categoryByName.id,
             Item.title == itemTitle)).one()
    description = itemByTitle.description

    return render_template(
        'detailItem.html',
        itemByTitle=itemByTitle,
        description=description)


# Add Item.
@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if username not in login_session:
        return redirect(url_for('default'))

    categories = session.query(Category).all()

    if request.method == 'POST':
        data = request.form

        categoryObject = session.query(Category).filter_by(
            name=data['category']).one()

        item = Item(title=data['title'],
                    description=data['description'], category=categoryObject)

        session.add(item)
        session.commit()
        return redirect(url_for('default'))
    else:
        return render_template('addItem.html', categories=categories)


# Edit Item.
@app.route('/catalog/<item>/edit', methods=['POST', 'GET'])
def editItem(item):
    if username not in login_session:
        return redirect(url_for('default'))
    categories = session.query(Category).all()
    itemToEdit = session.query(Item).filter_by(title=item).one()

    if request.method == 'POST':
        data = request.form

        categoryObject = session.query(Category).filter_by(
            name=data['category']).one()

        itemToEdit.title = data['title']
        itemToEdit.description = data['description']
        itemToEdit.category = categoryObject

        session.commit()

        return redirect(url_for('default'))
    else:
        return render_template(
            'editItem.html',
            categories=categories,
            item=itemToEdit)


# Delete Item.
@app.route('/catalog/<item>/delete', methods=['GET', 'POST'])
def deleteItem(item):
    if username not in login_session:
        return redirect(url_for('default'))

    itemToDelete = session.query(Item).filter_by(title=item).one()

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()

        return redirect(url_for('default'))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


# Login using Google OAuth2.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."),
            401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    return render_template('main.html', login_session=login_session)


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/logout')
def logout():
    access_token = login_session.get('access_token')

    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        categories = session.query(Category).all()
        rows = []

        for item, category in session.query(Item, Category). \
                filter(Item.category_id == Category.id).all():
            rows.append((item, category))

        return redirect(url_for('default'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'nG3d-G6QwZp8gH7tNc6Sjz2B'

    # Run flask app.
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
