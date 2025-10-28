# # Imports

# %%
import requests as rq
import pandas as pd
import os
import numpy as np
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
import copy


# # Definitions

# %%
base_urls = {
    "films": "https://swapi.dev/api/films/",
    "people": "https://swapi.dev/api/people/",
    "planets": "https://swapi.dev/api/planets/",
    "species": "https://swapi.dev/api/species/",
    "starships": "https://swapi.dev/api/starships/",
    "vehicles": "https://swapi.dev/api/vehicles/"
}

categories = list(base_urls.keys())
categories


# Each category has different fields that contain information in the form of an url. I will extract the page id from those fields for each category. 

# %%
fields = {
    'films' : ["characters", "planets", "starships", "vehicles", "species"],
    'people' : ["homeworld", "films", "species", "vehicles", "starships"],
    'planets' : ['residents', 'films'],
    'species' : ['people', 'films', 'homeworld'],
    'vehicles' : ['pilots', 'films'],
    'starships' : ['pilots', 'films']
    }


# # Consume the API

# %%
def scrape_category(url):

    # skip the next url for the first page of pager
    next = url    
    items_list = []

    while next:
        # get the content of the url
        response = rq.get(next)

        # success
        if response.status_code == 200:
            content = response.json()
        elif response.status_code == 404:
            print(f'{url} not found!')
            return
        
        next = content['next']
        items = content['results']

        for item in items:
                    
            # remove created and edited fields
            try:
                del(item['created'])
                del(item['edited'])
            except:
                pass
            
            items_list.append(item)            

    return items_list


# ## Scrape all the categories and store in *starwars_raw.json*
# (it takes 12.9 seconds)

# %%
if not os.path.exists('../data/starwars_raw.json'):
    raw_dict = {cat : scrape_category(base_urls[cat]) for cat in categories}
    
    os.makedirs('../data')
    # store into a json file
    with open('../data/starwars_raw.json', 'w') as file:
        json.dump(raw_dict, file, indent=4 )
    print('Content from Star Wars API stored in a json file!')

else:
    print('The content already exists in a json file!')
    with open('../data/starwars_raw.json', 'r') as file:
        raw_dict = json.load(file)


# Function to process the information of an item from a category.
# Ex. one character, one planet or one film.

# %%
def process_item(item, fields):

    # create a copy of the item dictionary
    item = copy.deepcopy(item)

    # parse the links from starships, vehicles and species
    for field in fields:
        #print(f'Processing field: {field}')
        id_values = []
                        
        if item[field]:  # if the field is not empty
            
            # parse the homeworld (just a single string value)
            if field == 'homeworld':
                item[field] = int(item[field].split('/')[-2])

            # the content of the item[field] is a list
            # of links (empty or just one link in case of species)
            else:
                # species field needs special treatment
                if field == 'species':
                    item['species'] = int(item['species'][0].split('/')[-2])
                    # process done, keep on with next field
                    # species contains only one value,
                    # so don't convert into tuple
                    continue

                # traverse the list of links for fields
                # other than homeworld and species
                else:
                    for link in item[field]:
                        # parse the id value in the link    
                        id_values.append(int(link.split('/')[-2]))

                # add the id values into the corresponding field key
                # convert list into tuple, as tuples are hashable
                item[field] = tuple(id_values)
                    
        # field has no values (empty list)
        else:
            # species field may be empty, but that means
            # she/he is a human, so set species = 1
            if field == 'species':
                item['species'] = 1
            # otherwise, it is a field supposed to be empty
            else:
                item[field] = ()
    
    # add the id, extracted from the url
    item['id'] = int(item['url'].split('/')[-2])
    
    # remove created and edited fields
    try:
        del(item['created'])
        del(item['edited'])
    except:
        pass

    return item


# # Store the processed data

# %%
if not os.path.exists('../data/starwars_processed_items.json'):
    # dictionary to store the processed categories
    processed_dict = {}
    
    # process each item for all the categories
    for k,v in raw_dict.items():
        items_processed = []
        for item in v:
            try:
                items_processed.append(process_item(item, fields[k]))
                processed_dict[k] = items_processed
            except:
                print(f'Error in {k}')
    
    # store the information in a json file
    with open('../data/starwars_processed_items.json', 'w') as file:
        json.dump(processed_dict, file, indent = 4)

# the file already exists, so load it
else:
    with open('../data/starwars_processed_items.json', 'r') as file:
        processed_dict= json.load(file)

        # convert lists into tuples after reading from json file
        for cat in categories:
            for item in processed_dict[cat]:
                for field in fields[cat]:
                    try:
                        item[field] = tuple(item[field])
                    # the content of the field is an integer
                    # and not a list. Cannot create a tuple from
                    # an integer using tuple(int)
                    except:
                        pass  # do not convert into a tuple, leave it as integer

    print('Processed data already existed, so the *categories_dict_processed* dictionary will be created from json file.')


# # Dataframes


# ## Create the dataframes
# Create a dictionary to store the dataframes from each category

# %%
dataframes = dict.fromkeys(categories)

# %%
for cat in categories:
    df = pd.DataFrame(processed_dict[cat])
    #df['id'] = df.index + 1

    # rename columns to add '_id' to the "fields"
    rename_dict = {field : f'{field}_id' for field in fields[cat]}
    rename_dict.update({'id' : f'{cat}_id'})
    df.rename(columns = rename_dict, inplace = True)

    # reorder the columns to place id in first place
    all_columns_but_cat_id = [col for col in df.columns if col != f'{cat}_id']
    sorted_columns = [f'{cat}_id'] + all_columns_but_cat_id
    dataframes[cat] = df[sorted_columns]


# ## Rename some columns
# Make some renamings to the column names

# %%
col_rename_dict= {
    
    'films': {
        'characters_id': 'character_id',
        'films_id': 'film_id',
        'planets_id': 'planet_id',
        'episode_id': 'episode',
        'starships_id': 'starship_id',
        'vehicles_id': 'vehicle_id',
    },
    
    'people': {
        'people_id': 'character_id',
        'films_id': 'film_id',
        'vehicles_id': 'vehicle_id',
        'starships_id': 'starship_id'
    },

    'planets': {
        'planets_id': 'planet_id',
        'films_id': 'film_id'
    },

    'species': {
        'people_id': 'character_id',
        'films_id': 'film_id'
    },

    'vehicles': {
        'pilots_id': 'pilot_id',
        'vehicles_id': 'vehicle_id',
        'films_id': 'film_id'
    },

    'starships': {
        'pilots_id': 'pilot_id',
        'starships_id': 'starship_id',
        'films_id': 'film_id'
    }
}

# %%
for cat in categories:
    dataframes[cat].rename(columns=col_rename_dict[cat], inplace=True)


# ## Clean the datasets


# ### Clean people

# %%
df = dataframes['people']
df.sample(5)

# %%
df.dtypes

# %%
df.mass = df.mass.replace('unknown', np.nan)
df.mass = df.mass.str.replace(',', '', regex=False)
df.mass = df.mass.astype('float') 

# %%
df.height = df.height.replace('unknown', np.nan).astype('float')

# %%
df.hair_color = df.hair_color.replace('n/a', np.nan)

# %%
df.birth_year = df.birth_year.str.replace('BBY', ' BBY')


# ### Clean films

# %%
df = dataframes['films']
df.sample(5)

# %%
df.species_id.unique()

# %%
df.dtypes

# %%
df.release_date = pd.to_datetime(df.release_date)


# ### Clean planets

# %%
df = dataframes['planets']
df.sample(5)

# %%
df.dtypes

# %%
for col in ['rotation_period', 'orbital_period', 'diameter', 'surface_water', 'population']:
    df[col] = df[col].replace('unknown', np.nan).astype('float')

# %%
df.population = df.population / 1E6
df.rename(columns = {'population' : 'population_millions'}, inplace = True)

# %%
df.gravity.unique()

# %%
df.gravity = df.gravity.str.replace(' standard', '').str.replace(df.gravity[5], '1.5')
df.gravity = df.gravity.replace('unknown', np.nan)


# ### Clean species

# %%
df = dataframes['species']
df.sample(5)

# %%
df.dtypes

# %%
df.average_height = df.average_height.replace('unknown', np.nan).replace('n/a', np.nan).astype('float')

# %%
df.average_lifespan = df.average_lifespan.replace('unknown', np.nan).replace('indefinite', 9999).astype('float')

# %%
df.loc[1, 'homeworld_id'] = np.nan
df.homeworld_id = df.homeworld_id.astype('float')


# ### Clean vehicles

# %%
df = dataframes['vehicles']
df.sample(5)

# %%
df.cost_in_credits = df.cost_in_credits.replace('unknown', np.nan)
df.cost_in_credits = df.cost_in_credits.astype('float')

# %%
for col in ['max_atmosphering_speed' ,'crew', 'passengers', 'cargo_capacity']:
    df[col] = df[col].replace('unknown', np.nan).replace('none', np.nan)
    df[col] = df[col].astype('float')

# %%
df.length = df.length.replace('unknown', np.nan)
df.length = df.length.astype('float')

# %%
df.consumables = df.consumables.replace('0', 'none')


# ### Clean starships

# %%
df = dataframes['starships']
df.sample(5)

# %%
df.loc[0, 'crew'] = 165

# %%
for col in ['cost_in_credits', 'length', 'max_atmosphering_speed', 'crew', 'passengers', 'cargo_capacity', 'hyperdrive_rating', 'MGLT']:
    try:
        df[col] = df[col].replace('unknown', np.nan).replace('none', np.nan).replace('n/a', np.nan)
        df[col] = df[col].str.replace(',', '', regex = False).str.replace('km', '')
        #df[col] = df[col].astype('float')
    except Exception as e:
        print(f'Error in {col}: {e}')

# %%
for col in ['cost_in_credits', 'length', 'max_atmosphering_speed', 'crew', 'passengers', 'cargo_capacity', 'hyperdrive_rating', 'MGLT']:
    try:
        df[col] = df[col].astype('float')
    except:
        print(f'error with {col}')


# ## Export clean datasets into csv files

# %%
data_path = '../data'
for cat in categories:
    filename = f'{cat}_dataframe.csv'
    if os.path.exists(f'{data_path}/csv/{filename}'):
        print(f'File {filename} already exist!')
        pass
    else:
        os.makedirs(f'{data_path}/csv/', exist_ok=True)
        df = dataframes[cat]
        df.to_csv(f'{data_path}/csv/{cat}_dataframe.csv', index = False)
print(f'Dataframes of each normalized category are stored in {data_path}/csv/ as csv files!')


# # Junction tables
# 
# (many-to-many relationships in the database)
# 
# 1. **films_people**: Links films to the characters that appeared in them.
# 
#     - character_id: Foreign Key referencing the `people` table.
#     - film_id: Foreign Key referencing the films table.
# 
# 2. **films_planets**: Links films to the planets that appeared in them.
# 
#     - planet_id: Foreign Key referencing the `planets` table.
#     - film_id: Foreign Key referencing the `films` table.
# 
# 3. **films_starships**: Links films to the starships that appeared in them.
# 
#     - starship_id: Foreign Key referencing the `starships` table.
#     - film_id: Foreign Key referencing the `films` table.
# 
# 4. **films_vehicles**: Links films to the vehicles that appeared in them.
# 
#     - vehicle_id: Foreign Key referencing the `vehicles` table.
#     - film_id: Foreign Key referencing the `films` table.
# 
# 5. **films_species**: Links films to the species that appeared in them.
# 
#     - species_id: Foreign Key referencing the `species` table.
#     - film_id: Foreign Key referencing the `films` table.
# 
# 6. **people_starships**: Links people (pilots) to the starships they have piloted.
# 
#     - character_id: Foreign Key referencing the `people` table.
#     - starship_id: Foreign Key referencing the `starships` table.
# 
# 7. **people_vehicles**: Links people (pilots) to the vehicles they have piloted.
# 
#     - character_id: Foreign Key referencing the `people` table.
#     - vehicle_id: Foreign Key referencing the vehicles table.

# %%
junction_tables = [
    'people_vehicles', 
    'people_starships',
    
    'films_people',
    'films_planets',
    'films_starships',
    'films_vehicles',
    'films_species'
    ]

junction_tables_dict = {i:None for i in junction_tables}


# ## Junction tables for people:

# %%
columns = ['vehicle_id', 'starship_id']
data = dataframes['people'].loc[:, columns + ['character_id']]

for col in columns:
    table_name = f'people_{col}'.replace('_id', 's')
    junction_tables_dict[table_name] = (data.loc[:, ['character_id', col]]
                                        .explode(col)
                                        .explode('character_id')
                                        .dropna()
                                        .reset_index(drop = True)
                                        .sort_values('character_id')
                                        )


# ## Junction tables for films:

# %%
columns = ['character_id', 'species_id', 'planet_id', 'vehicle_id', 'starship_id']
data = dataframes['films'].loc[:, columns + ['film_id']]

for col in columns:
    table_name = f'films_{col}'
    if col == 'species_id':
        table_name = table_name.replace('_id', '')
    elif col == 'character_id':
        table_name = 'films_people'
    else:
        table_name = table_name.replace('_id', 's')
        
    junction_tables_dict[table_name] = (data.loc[:, ['film_id', col ]]
                                        .explode(col)
                                        .reset_index(drop = True)
                                        .sort_values('film_id')
    )


# # Normalization
# Next step is to normalize the datasets in order to create the database.

# %%
dataframes_normalized = copy.deepcopy(dataframes)

# %%
columns_to_drop = {
    'films' : ['character_id', 'planet_id', 'species_id', 'vehicle_id', 'starship_id'],
    'people' : ['film_id', 'vehicle_id', 'starship_id'],
    'planets' : ['residents_id', 'film_id'],
    'species' : ['character_id', 'film_id'],
    'starships' : ['pilot_id', 'film_id'],
    'vehicles' : ['pilot_id', 'film_id'],
}  


# ### Drop the corresponding columns in order to normalize the tables

# %%
for cat in dataframes_normalized.keys():
    dataframes_normalized[cat].drop(columns_to_drop[cat], axis='columns', inplace = True)


# ## Store the normalized dataframes

# %%
data_path = '../data'
for cat in categories:
    filename = f'{cat}_dataframe.csv'
    if os.path.exists(f'{data_path}/csv_normalized/{filename}'):
        print(f'File {filename} already exist!')
        pass
    else:
        os.makedirs(f'{data_path}/csv_normalized/', exist_ok=True)
        df = dataframes_normalized[cat]
        df.to_csv(f'{data_path}/csv_normalized/{cat}_dataframe_normalized.csv', index = False)
print(f'Dataframes of each normalized category are stored in {data_path}/csv_normalized/ as csv files!')


# # Insert data into the database


# ## Load database parameters from `.env` file

# %%
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# ## Create the db connection

# %%
connection_string = (
    f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# --- 4. Create the SQLAlchemy Engine ---
try:
    engine = create_engine(connection_string)
    print("SQLAlchemy Engine created successfully. 🛠️")
except Exception as e:
    print(f"Error creating engine: {e}")


# ## Populate the data into the database
# 
# The order of tables to be filled must be:
# 1. planets
# 2. species
# 3. starships
# 4. vehicles
# 5. films
# 6. people

# %%
categories_sorted = ['planets', 'species', 'vehicles', 'starships', 'films', 'people']


# ### Insert the category tables into the database

# %%
def insert_category(cat, dictionary):
    df = dictionary[cat]
    try:
        df.to_sql(name=cat, con=engine, if_exists='append', index=False)
        print(f"DataFrame for category '{cat}' inserted successfully into the database. ✅\n")
    except Exception as e:
        print(f"\\ Error inserting DataFrame for category '{cat}': \n{e}\n\n")

# %%
for cat in categories_sorted:
    query = f'select * from {cat} limit 1 ;'
    # if table is empty, fill it with the corresponding data
    if pd.read_sql(query, con = engine).shape[0] == 0:
        insert_category(cat, dataframes_normalized)
    else:
        print(f'{cat} table already exists in database!')


# ### Insert junction tables

# %%
for table in junction_tables_dict.keys():
    query = f'select * from {table} limit 1 ;'
    # if table is empty, fill it with the corresponding data
    if pd.read_sql(query, con = engine).shape[0] == 0:
        insert_category(table, junction_tables_dict)
    else:
        print(f'{table} table already exists in database!') 

# %%
print('All the process finished successfully!!!')


