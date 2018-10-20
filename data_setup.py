from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('postgresql://catalog:password@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user = User(user_id="dskym0@gmail.com")
session.add(user)
session.commit()

# Initialize Category list.
categoryList = ['Soccer', 'Basketball', 'Baseball', 'Frisbee',
              'Snowboarding', 'Rock Climbing', 'Football', 'Skating', 'Hockey']

categories = {}

# Insert category data into category table.
for category in categoryList:
    tempCategory = Category(name=category)
    session.add(tempCategory)
    session.commit()

    categories[category] = tempCategory

# Insert item data into item table.
tempItem = Item(title="Soccer1",
                description="Soccer Item Description 1", category=categories['Soccer'], user=user)
session.add(tempItem)
session.commit()

tempItem = Item(title="Soccer2",
                description="Soccer Item Description 2", category=categories['Soccer'], user=user)
session.add(tempItem)
session.commit()

tempItem = Item(title="Soccer3",
                description="Soccer Item Description 3", category=categories['Soccer'], user=user)
session.add(tempItem)
session.commit()


tempItem = Item(title="Basketball1",
                description="Basketball Item Description 1", category=categories['Basketball'], user=user)
session.add(tempItem)
session.commit()

tempItem = Item(title="Basketball2",
                description="Basketball Item Description 2", category=categories['Basketball'], user=user)
session.add(tempItem)
session.commit()
tempItem = Item(title="Basketball3",
                description="Basketball Item Description 3", category=categories['Basketball'], user=user)
session.add(tempItem)
session.commit()


tempItem = Item(title="Baseball1",
                description="Baseball Item Description 1", category=categories['Baseball'], user=user)
session.add(tempItem)
session.commit()

tempItem = Item(title="Baseball2",
                description="Baseball Item Description 2", category=categories['Baseball'], user=user)
session.add(tempItem)
session.commit()
tempItem = Item(title="Basketball3",
                description="Baseball Item Description 3", category=categories['Baseball'], user=user)
session.add(tempItem)
session.commit()


tempItem = Item(title="Frisbee1",
                description="Frisbee Item Description 1", category=categories['Frisbee'], user=user)
session.add(tempItem)
session.commit()

tempItem = Item(title="Frisbee2",
                description="Frisbee Item Description 2", category=categories['Frisbee'], user=user)
session.add(tempItem)
session.commit()
tempItem = Item(title="Frisbee3",
                description="Frisbee Item Description 3", category=categories['Frisbee'], user=user)
session.add(tempItem)
session.commit()
