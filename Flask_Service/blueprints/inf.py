import json

temp_codes=[]
with open('./user.json') as fp:
    user_dict = json.load(fp)