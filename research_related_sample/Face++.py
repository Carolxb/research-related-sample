import csv
import re
import os
import collections
import numpy as np
import pandas as pd
from ethnicolr import census_ln, pred_census_ln
import emoji
import requests
from json import JSONDecoder
import argparse
from picture_preprocess import download_resize_img

TW_DEFAULT_PROFILE_IMG = ".cache/tw_default_profile.png"

http_url = 'https://api-us.faceplusplus.com/facepp/v3/detect'

# key = "E3y9boohYQCZFsm8ysX0WVpN-mlDDOyw"  # input key sign by face++
# secret = "K216VVatTDU_aD4eIl-JbPYGobCrK2D2"  # input secret sign by face++
key ="LYOy7-J298W8h2OjJrfwUxjw4FZZG5V-" # input key sign by face++
secret ="YxypCD5U22vOnHxiyZAZvQ8N09c77-kP"# input secret sign by face++

data = {"api_key": key, "api_secret": secret,
        "return_attributes": "gender,age,ethnicity,emotion,smiling"}
df = pd.read_csv('user_face.csv')


def face(url):
    r = requests.get(url)  # 12
    if 'jpg' in url:
        with open('profile.jpg', 'wb') as f:
            f.write(r.content)
            filepath1 = 'profile.jpg'
    elif 'jpeg' in url:
        with open('profile.jpeg', 'wb') as f:
            f.write(r.content)
            filepath1 = 'profile.jpeg'
    elif 'png' in url:
        with open('profile.png', 'wb') as f:
            f.write(r.content)
            filepath1 = 'profile.png'
    else:
        return {'error_message': 'not a photo'}
    files = {"image_file": open(filepath1, "rb")}
    response = requests.post(http_url, data=data, files=files)
    req_con = response.content.decode('utf-8')
    face_info = JSONDecoder().decode(req_con)

    return face_info

def face_local(url, user_id):

    # get the downloaded pictures and resize the pictures
    img_local = download_img(url, './.cache/', user_id)
    if img_local == TW_DEFAULT_PROFILE_IMG:
        return {'error_message': 'unable to get the img'}
    files = {"image_file": open(img_local, "rb")}
    response = requests.post(http_url, data=data, files=files)
    req_con = response.content.decode('utf-8')
    face_info = JSONDecoder().decode(req_con)
    return face_info

def download_img(img_path, cache_dir, user_id):
    img_path = img_path.replace("_normal", "_400x400")
    dotpos = img_path.rfind(".")
    img_file_full = "{}/{}.{}".format(cache_dir, str(user_id), img_path[dotpos + 1:])
    img_file_resize = "{}/{}_224x224.{}".format(cache_dir, str(user_id), img_path[dotpos + 1:])
    if not os.path.isfile(img_file_resize):
        download_resize_img(img_path, img_file_resize)
    # check if an error occurred and the image was not downloaded
    if not os.path.exists(img_file_resize):
        img_file_resize = TW_DEFAULT_PROFILE_IMG
    return img_file_resize


def check_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def ethnic(name):
    temp_name = name
    # remove emoji (worked)
    temp_name = re.sub(emoji.get_emoji_regexp(), r"", temp_name)
    # remove parenthsis
    temp_name = re.sub(r'\([^)]*\)', '', temp_name)
    # remove all the content behind ,
    if "," in temp_name:
        punc_idx = temp_name.index(",")
        temp_name = temp_name[:punc_idx]
    # remove special character
    temp_name = re.sub("[^A-Za-z]+", " ", temp_name)
    print(temp_name)
    name_part = temp_name.split(" ")
    if len(name_part) <= 1:
        preprocessed_name = temp_name
    elif len(name_part) == 2:
        preprocessed_name = name_part[-1]
    else:
        preprocessed_name = name_part[1]
    frame = [[preprocessed_name]]
    data = pd.DataFrame(frame, columns=['clean_name'])
    data = census_ln(data, 'clean_name')

    if check_float(data.loc[0, "pctwhite"]) and float(
            data.loc[0, "pctwhite"]) > 50:
        return 'white'
    elif check_float(data.loc[0, "pctblack"]) and float(data.loc[0, "pctblack"]) > 50:
        return 'black'
    elif check_float(data.loc[0, "pctapi"]) and float(data.loc[0, "pctapi"]) > 50:
        return 'asian'
    elif check_float(data.loc[0, "pctaian"]) and float(data.loc[0, "pctaian"]) > 50:
        return "American Indian or Alaska Native"
    elif check_float(data.loc[0, "pcthispanic"]) and float(data.loc[0, "pcthispanic"]) > 50:
        return "hispanic"
    else:
        return "false"

if __name__ == "__main__":

    parse = argparse.ArgumentParser()
    parse.add_argument('--download', action='store_true', default=True, required=False)
    parse.add_argument('--save', action='store_true', default=False, required=False)
    args = parse.parse_args()

    src = pd.read_csv('user_with_valid_url.csv')
    out = pd.DataFrame()
    total_count = 0
    count1 = 0
    count2 = 0
    for index, row in src.iterrows():
        total_count += 1
        user_id = row['user_id']
        if not args.save:
            user_id = 1
        if not args.download:
            faceinfo = face(row['image_url'])
        else:
            faceinfo = face_local(row['image_url'], user_id)
        if 'error_message' in faceinfo.keys():
            continue
        if faceinfo['face_num'] == 1:
            count1 += 1
            race = ethnic(row['user_name'])
            print(race)
            print('total count:' + str(total_count))
            print('count1: ' + str(count1))
            count2 += 1
            gender = faceinfo['faces'][0]['attributes']['gender']['value']
            age = faceinfo['faces'][0]['attributes']['age']['value']
            out = out.append(pd.Series([row['user_id'], race, age,
                    gender, row['user_name'], row['image_url']]), ignore_index=True)
            out.to_csv('user_output.csv', index=False)

    print('total count:' + str(total_count))
    print('count1: ' + str(count1))
    print('count2: ' + str(count2))
    out.reset_index()
    out.columns = ['index', 'user_id', 'race', 'user_name',
                'age', 'gender', 'user_name', 'image_url']
    out.to_csv('user_output.csv', index=False)
