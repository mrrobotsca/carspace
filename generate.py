import pandas as pd
import numpy as np
import os

data = {'lat': ['45.535726','45.535873','45.535706','45.535605'],
        'lon': ['-73.661380','-73.661560','-73.661112','-73.661437'],
        'nomCapteur': ['Capteur1', 'Capteur2', 'Capteur4', 'Capteur4'],
        'etat': [True, False, False, True],
        'moyenne': ['2:30','1:50','0:10','5:30']
        }

df = pd.DataFrame(data, columns= ['lat', 'lon','nomCapteur','etat','moyenne'])

df.to_csv('data.csv')