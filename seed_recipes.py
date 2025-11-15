from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/recipe_db')
client = MongoClient(MONGO_URI)
db = client.get_default_database() if client else client['recipe_db']
recipes = db.get_collection('recipes')


sample = [
{
'title': 'Masala Omelette',
'ingredients': ['eggs', 'onion', 'tomato', 'green chili', 'salt', 'pepper', 'oil'],
'steps': 'Beat eggs. Chop veggies. Mix and fry in a pan until set.',
'tags': ['breakfast', 'quick']
},
{
'title': 'Tomato Pasta',
'ingredients': ['pasta', 'tomato', 'garlic', 'olive oil', 'salt', 'pepper'],
'steps': 'Boil pasta. Make tomato sauce by sauteing garlic and tomato. Mix and serve.',
'tags': ['pasta', 'dinner']
},
{
'title': 'Chickpea Salad',
'ingredients': ['chickpeas', 'onion', 'tomato', 'cucumber', 'lemon', 'salt', 'pepper'],
'steps': 'Mix all chopped veggies with chickpeas and dressing.',
'tags': ['vegan', 'salad']
}
]


recipes.delete_many({})
recipes.insert_many(sample)
print('Inserted sample recipes')



