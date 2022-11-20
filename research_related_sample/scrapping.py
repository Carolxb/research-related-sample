

# import the module
import tweepy
import json
import pandas as pd
import numbers as np
import math
import os
  
if __name__ == '__main__':
    consumer_key = "kA9PSnWrghf7ZwGb8pRgmTU2E"

    consumer_secret = "WFfw80q80XF2FtTbDqhnN7MjoDslZxuK6Rb5WzZD0BNBLNPhsC"

    access_token = "1293963781714792448-01eVAAHyoxBbzkX4NFaO8BYruHGeaV"
    access_token_secret = "UFZuhFzVUi7SBGT0vPRXrPaeMz8QWbotxix8Lo4My9tTq"


    # user.fields
    # # # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    # set access to user's access key and access secret 
    auth.set_access_token(access_token, access_token_secret)
    
    # calling the api 
    api = tweepy.API(auth)
    df=pd.read_csv('image_invalid.csv')

    # the screen name of the user

    if not ('new_valid_url' in df.columns):
        df['new_valid_url']=''
    # fetching the user
    for i in range(int(os.environ['PYTHON_ARG']), len(df)):
        try:
    #         user = api.get_user(screen_name = str(df['screen_name'][i]))
            user=api.get_user(user_id = math.floor(df['user_id'][i]), screen_name = str(df['screen_name'][i]))
            df['new_valid_url'][i]=user.profile_image_url
        except tweepy.errors.NotFound as e1:
            df['new_valid_url'][i]='not found'
        except tweepy.errors.TooManyRequests as e2:
            print(i+1)
            break
        except tweepy.errors.Forbidden as e3:
            df['new_valid_url'][i]='forbidden'
        except tweepy.errors.TwitterServerError as e4:
            df['new_valid_url'][i]='server error'
        except tweepy.errors.Unauthorized as e5:
            df['new_valid_url'][i]='unauthorized'
        except tweepy.errors.BadRequest as e6:
            df['new_valid_url'][i]='bad request'
        except ValueError as e7:
            df['new_valid_url'][i]='value error'
            print(i+1)
            break
    df.to_csv('image_invalid.csv', index=False)
