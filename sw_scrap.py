import os
import requests as rq
import pandas as pd

def get_character(id):
    base_url = 'https://swapi.dev/api/people'
    try:
        content = rq.get(f'{base_url}/{id}').json()
    except Exception as e:
        print('URL not found!')
        return
    
    referred_fields = ['homeworld', 'films', 'species', 'vehicles', 'starships']

    for field in referred_fields:
        id_values = []
        try:
            if content[field]:
                if field != 'homeworld':
                    for link in content[field]:
                        id_values.append(int(link.split('/')[-2]))
                    content[field] = id_values
                # homeworld is a single url string
                else:
                    content[field] = int(content[field].split('/')[-2])
            elif field == 'species' and not content[field]:
                content[field] = 'human'
        except:
            print(f"{field} doesn't exist in character: {base_url}/{id}")
            pass
             
    # remove created and edited fields
    try:
        del(content['created'])
        del(content['edited'])
    except:
        print(f'Keys not found in content! ({base_url}/{id})')

    return content


# get_character(10)

# there are 82 different url for star wars characters
characters_list = [get_character(id) for id in range(1,83)]

# for index, value in enumerate(characters_list):
#     if 'detail' in value.keys():
#         print(f'Details found in character with id: {index + 1}')

# Remove character with id 17. It's a valid url!
del characters_list[16]

if not os.path.exists('./data/characters.csv'):
    characters_df = pd.DataFrame(characters_list)
    characters_df['id'] = characters_df.index + 1
    characters_df.to_csv('./data/characters.csv', index=False)






