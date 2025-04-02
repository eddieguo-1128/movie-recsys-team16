"""
We have implemented a KS test for (1) all the users, i.e. the whole database to see if there's a drift after a certain date and (2) each user. 
The KS test compares the CDF for each set and to do this for each user we normalized the timestamp for the dataset and then found the midpoint of the timestamps for each user and split the data into 2 periods for each user. 
Then, fed this in for each user into the KS test metric and if the p-value was <0.05 (significance), flagged a drift else not.
"""
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

data = pd.read_csv('backend/model/cleaned_ratings.csv')
#data = pd.read_csv('backend/model/ratings.csv')
data['timestamp'] = pd.to_datetime(data['timestamp'])
#data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
#data.dropna(subset=['timestamp'], inplace=True)
data['date'] = data['timestamp'].dt.normalize()
###FOR THE GENERAL DISTRIBUTION
midpoint = data['date'].sort_values().iloc[len(data) // 2]
period1 = data[data['date'] <= midpoint]
period2 = data[data['date'] > midpoint]
ratings_period1 = period1['rating']
ratings_period2 = period2['rating']
ks_stat, p_value = ks_2samp(ratings_period1, ratings_period2)
if p_value < 0.05:
  print('Significant drift detected in rating distribution for all users')
else:
  print('No significant drift detected for all users')
print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
###FOR EACH USER
for user_id in data['user_id'].unique():
  user_id_to_check = user_id
  user_data = data[data['user_id'] == user_id_to_check]
  if user_data.empty:
      #print(f'User {user_id_to_check} not found in the dataset.')
      continue
  else:
      # Split based on user's own median date
      midpoint = user_data['date'].sort_values().iloc[len(user_data) // 2]
      period1 = user_data[user_data['date'] <= midpoint]
      period2 = user_data[user_data['date'] > midpoint]
      ratings_period1 = period1['rating']
      ratings_period2 = period2['rating']
      if len(ratings_period1) > 0 and len(ratings_period2) > 0:
          ks_stat, p_value = ks_2samp(ratings_period1, ratings_period2)
          # Output results
          #print(f'KS Statistic (User {user_id_to_check} Ratings Drift): {ks_stat:.4f}')
          #print(f'P-value: {p_value:.4f}')
          # Interpretation
          if p_value < 0.05:
              print(f"User {user_id_to_check} has {len(period1)} records in Period 1 and {len(period2)} records in Period 2.")
              print('Significant drift detected in rating distribution for this user')
              print(period1[['movie_id','rating','date']])
              print("-------")
              print(period2[['movie_id','rating','date']])
              print("############")
          else:
              continue
              #print(f"User {user_id_to_check} has {len(period1)} records in Period 1 and {len(period2)} records in Period 2.")
              #print('No significant drift detected for this user')
      else:
          #print("Not enough data in one of the periods to perform KS test")
          continue
"""
Outputs:
No significant drift detected for all users
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
User 72873 has 7 records in Period 1 and 6 records in Period 2.
Significant drift detected in rating distribution for this user
                     movie_id  rating       date
685     the+cutting+edge+1992       3 2025-01-15
695            backdraft+1991       3 2025-01-17
759  d2+the+mighty+ducks+1994       3 2025-01-20
768                 antz+1998       4 2025-01-22
807           armageddon+1998       3 2025-01-25
816        batman++robin+1997       2 2025-01-26
829              chicago+2002       4 2025-01-23
-------
                              movie_id  rating       date
964                    braveheart+1995       5 2025-02-01
974   back+to+the+future+part+iii+1990       4 2025-02-02
981                      the+cell+2000       4 2025-02-03
988    e.t.+the+extra-terrestrial+1982       4 2025-02-04
1013                almost+famous+2000       5 2025-02-07
1114                       cocoon+1985       4 2025-02-09
############
User 3616 has 6 records in Period 1 and 4 records in Period 2.
Significant drift detected in rating distribution for this user
                          movie_id  rating       date
1143            billy+madison+1995       4 2025-01-04
1158       the+princess+bride+1987       3 2025-01-10
1175                  titanic+1997       4 2025-01-14
1205                true+lies+1994       4 2025-01-12
1216  ferris+buellers+day+off+1986       5 2025-01-15
1242                  the+ref+1994       4 2025-01-18
-------
                            movie_id  rating       date
1255         the+wedding+singer+1998       3 2025-01-20
1389  terminator+2+judgment+day+1991       3 2025-01-31
1425                   airplane+1980       3 2025-01-30
1554                 serial+mom+1994       1 2025-02-08
############
User 39365 has 10 records in Period 1 and 8 records in Period 2.
Significant drift detected in rating distribution for this user
                                               movie_id  rating       date
1260   harry+potter+and+the+deathly+hallows+part+2+2011       4 2025-01-21
1268                                 jurassic+park+1993       5 2025-01-22
1281                           million+dollar+baby+2004       4 2025-01-23
1340                            once+were+warriors+1994       4 2025-01-25
1349  the+lord+of+the+rings+the+fellowship+of+the+ri...       5 2025-01-26
1370                                       aladdin+1992       4 2025-01-28
1386                                  first+knight+1995       3 2025-01-31
1411                                  a+single+man+2009       4 2025-01-29
1429                                          tron+1982       4 2025-01-31
1495                               schindlers+list+1993       4 2025-02-01
-------
                                          movie_id  rating       date
1456                          the+incredibles+2004       3 2025-02-03
1481          i+know+what+you+did+last+summer+1997       3 2025-02-05
1511                             forrest+gump+1994       4 2025-02-03
1522  harry+potter+and+the+philosophers+stone+2001       3 2025-02-04
1545                            batman++robin+1997       3 2025-02-07
1571                           monsters_+inc.+2001       2 2025-02-10
1591                                    alien+1979       4 2025-02-07
1615                              the+x+files+1998       2 2025-02-10
############
User 4714 has 7 records in Period 1 and 6 records in Period 2.
Significant drift detected in rating distribution for this user
                                    movie_id  rating       date
2224                    erin+brockovich+2000       2 2025-01-20
2254  the+naked+gun+33+the+final+insult+1994       2 2025-01-23
2334                         phenomenon+1996       1 2025-01-27
2395                         waterworld+1995       1 2025-01-28
2413                        about+a+boy+2002       2 2025-01-31
2477                    muriels+wedding+1994       2 2025-02-02
2481                              ghost+1990       3 2025-02-02
-------
                                movie_id  rating       date
2446                 the+full+monty+1997       5 2025-02-03
2493               kill+bill+vol.+2+2004       5 2025-02-04
2514                          dogma+1999       3 2025-02-06
2521                     highlander+1986       5 2025-02-07
2544                      the+abyss+1989       3 2025-02-05
2643  the+rocky+horror+picture+show+1975       4 2025-02-11
############
User 74050 has 8 records in Period 1 and 6 records in Period 2.
Significant drift detected in rating distribution for this user
                      movie_id  rating       date
5814              sabrina+1995       3 2025-01-02
5823     independence+day+1996       4 2025-01-10
5868       the+substitute+1996       3 2025-01-08
5888         multiplicity+1996       3 2025-01-15
5906   executive+decision+1996       4 2025-01-18
5925        unforgettable+1996       3 2025-01-21
5981  the+nutty+professor+1996       3 2025-01-22
6027       down+periscope+1996       2 2025-01-23
-------
                             movie_id  rating       date
6023  the+truth+about+cats++dogs+1996       2 2025-01-29
6102                   the+quest+1996       1 2025-02-02
6120                    spy+hard+1996       2 2025-02-04
6188                        fled+1996       3 2025-02-06
6241                 the+phantom+1996       2 2025-02-05
6281                   barb+wire+1996       1 2025-02-10
############
User 39484 has 9 records in Period 1 and 8 records in Period 2.
Significant drift detected in rating distribution for this user
                           movie_id  rating       date
6922              broken+arrow+1996       4 2025-01-21
6934                     speed+1994       4 2025-01-23
6954  the+shawshank+redemption+1994       5 2025-01-19
6962              the+birdcage+1996       4 2025-01-20
6986              the+fugitive+1993       5 2025-01-23
7004               judge+dredd+1995       4 2025-01-24
7007              pulp+fiction+1994       5 2025-01-25
7027              crimson+tide+1995       5 2025-01-27
7069                      dave+1993       4 2025-01-26
-------
                                             movie_id  rating       date
7047                       star+trek+generations+1994       4 2025-01-29
7094                       leon+the+professional+1994       3 2025-01-30
7116                            last+action+hero+1993       3 2025-02-02
7126                                  waterworld+1995       3 2025-02-02
7155                       beverly+hills+cop+iii+1994       3 2025-02-01
7201  city+slickers+ii+the+legend+of+curlys+gold+1994       2 2025-02-05
7207                   terminator+2+judgment+day+1991       4 2025-02-06
7278                        beauty+and+the+beast+1991       2 2025-02-08
############
User 14181 has 8 records in Period 1 and 6 records in Period 2.
Significant drift detected in rating distribution for this user
                                           movie_id  rating       date
9557                               city+of+god+2002       5 2025-01-04
9601             the+rocky+horror+picture+show+1975       4 2025-01-14
9620                                pocahontas+1995       1 2025-01-09
9636  harry+potter+and+the+prisoner+of+azkaban+2004       4 2025-01-12
9659                                    grease+1978       4 2025-01-16
9693                                   traffic+2000       5 2025-01-19
9728                  robin+hood+men+in+tights+1993       4 2025-01-17
9759                               about+a+boy+2002       4 2025-01-21
-------
                           movie_id  rating       date
9780                    splash+1984       2 2025-01-23
9816            monsters_+inc.+2001       3 2025-01-26
9855               chasing+amy+1997       3 2025-01-25
9935     the+brady+bunch+movie+1995       1 2025-01-28
9944  honey_+i+shrunk+the+kids+1989       1 2025-01-29
9971        lawrence+of+arabia+1962       4 2025-01-31
############"""