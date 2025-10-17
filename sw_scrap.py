# %%
import requests as rq
import pandas as pd
import os
import numpy as np
import json

# %%
base_urls = {
    "films": "https://swapi.dev/api/films/",
    "people": "https://swapi.dev/api/people/",
    "planets": "https://swapi.dev/api/planets/",
    "species": "https://swapi.dev/api/species/",
    "starships": "https://swapi.dev/api/starships/",
    "vehicles": "https://swapi.dev/api/vehicles/"
}

# %%
categories = list(base_urls.keys())
categories

# %%
fields = {
    'people' : ["homeworld", "films", "species", "vehicles", "starships"],
    'planets' : ['residents', 'films'],
    'films' : ["characters", "planets", "starships", "vehicles", "species"],
    'species' : ['people', 'films'],
    'vehicles' : ['pilots', 'films'],
    'starships' : ['pilots', 'films']
    }

# %%
def get_page_items(url, fields):
        
    # get the content of the url
    response = rq.get(url)

    # success
    if response.status_code == 200:
        content = response.json()
    elif response.status_code == 404:
        print(f'{url} not found!')
        return
    
    items_list = []

    next = content['next']
    items = content['results']

    for item in items:

        for field in fields:
            id_values = []
                           
            if item[field]:  # if the field is not empty
                # parse the links from starships, vehicles and starships
                if field != 'homeworld':  
                    for link in item[field]:
                        # parse the id value in the link    
                        id_values.append(int(link.split('/')[-2]))
                    # add the id values into the corresponding field key
                    # convert list into tuple, as tuples are hashable
                    # each character belongs to only 1 species
                    if field != 'species':
                        item[field] = tuple(id_values)
                    else:
                        item[field] = id_values[0]
                        
                # parse the homeworld (just a single string value)
                else:
                    # get the homeworld id
                    item['homeworld'] = int(item['homeworld'].split('/')[-2])
            
            # parse species field
            # in case of human characters, the species field is an empty list
            elif field == 'species' and not item[field]:
                item[field] = 1
            
            # field has no values (empty list)
            else:
                item[field] = ()
                  
        # remove created and edited fields
        try:
            del(item['created'])
            del(item['edited'])
        except:
            pass
        
        items_list.append(item)

    return next, items_list

# %% [markdown]
# Scrape all the information from the Star Wars API, for all the available categories

# %%
if not os.path.exists('./data/starwars.json'):
    items = dict.fromkeys(categories)

    for category in categories:
        items_list = []
        url = base_urls[category]
        category_fields = fields[category]
        while url:
            url, page_items = get_page_items(url, category_fields)
            items_list.extend(page_items)
        
        items[category] = items_list

        print(f'{category} successfully scrapped!')

    print('\n\nWhole database fully scrapped!')
    print('\nNow the information will be stored in a json file...')

    # store the information in a json file
    filepath = './data/starwars.json'
    if not os.path.exists(filepath):
        with open(filepath, 'w') as file:
            json.dump(items, file, indent=4)

        # remove the carriage return character
        with open(filepath, 'r') as file:
            content = file.readlines()

        # replace the \\r\\n (the codes are escaped) string with just \\n
            for index, line in enumerate(content):
                content[index] = line.replace('\\r\\n', '\\n')

        # after replacement, store its content
        with open(filepath, 'w') as file:
            file.writelines(content)
        
        print(f'Scrapped content stored at: {filepath}')
    # The file already exists and will be read
    else:
        print('starwars.json file already exists!')
        print('Information will be read and stored in items dictionary.')
        items = {}
        with open(filepath, 'r') as file:
            items = json.load(file)
        print(f'Scrapped content will be stored at {filepath}')

# %% [markdown]
# ## Store the dataframes from each category in a dictionary

# %%
categories_dataframes = dict.fromkeys(categories)

# %% [markdown]
# ### Generate the dataframes

# %%
for cat in categories:
    df = pd.DataFrame(items[cat])
    df['id'] = df.index + 1

    # rename columns to add '_id' to the "fields"
    rename_dict = {field : f'{field}_id' for field in fields[cat]}
    rename_dict.update({'id' : f'{cat}_id'})
    df.rename(columns = rename_dict, inplace = True)

    # reorder the columns to place id in first place
    all_columns_but_cat_id = [col for col in df.columns if col != f'{cat}_id']
    sorted_columns = [f'{cat}_id'] + all_columns_but_cat_id
    categories_dataframes[cat] = df[sorted_columns]
#df.to_csv('./data/starwars_characters.csv', index = False)

# %% [markdown]
# ## Junction tables
# (many-to-many relationships in the database)
# 
# 1. people_films: Links people to the films they appeared in.
# 
#     - person_id: Foreign Key referencing the people table.
#     - film_id: Foreign Key referencing the films table.
# 
# 2. people_vehicles: Links people to the vehicles they have piloted.
# 
#     - person_id: Foreign Key referencing the people table.
#     - vehicle_id: Foreign Key referencing the vehicles table.
# 
# 3. people_starships: Links people to the starships they have piloted.
# 
#     - person_id: Foreign Key referencing the people table.
#     - starship_id: Foreign Key referencing the starships table.

# %%
junction_tables = ['people_films', 'people_vehicles', 'people_starships']
junction_tables = [f'{table}_junction_table' for table in junction_tables]
junction_tables

# %%
data = categories_dataframes['people'].loc[:, ['people_id', 'films_id', 'vehicles_id', 'starships_id']]

# junction table for people and films
people_film_junction = data.explode('films_id').drop(['vehicles_id', 'starships_id'], axis = 1)

# junction table for people and vehicles
people_vehicles_junction = data.explode('vehicles_id').drop(['films_id', 'starships_id'], axis = 1)

# junction table for people and starships
people_starships_junction = data.explode('starships_id').drop(['films_id', 'vehicles_id'], axis = 1)

# %% [markdown]
# ## Example of joined people and their vehicles

# %%
# df2 = pd.merge(people_vehicles_junction, categories_dataframes['people'], on='people_id', how = 'inner')
# df2.rename(columns={'vehicles_id_x' : 'vehicles_id'}, inplace=True)

# df2 = pd.merge(df2, categories_dataframes['vehicles'], on='vehicles_id')
# #df2.drop(['people_id', 'vehicles_id'], axis = 1)
# df2.head()


