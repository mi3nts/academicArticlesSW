
import pandas as pd
import glob


def setFogLikelyhood(df):

    df['fogLikelihood'] = (
        (df['humidity'] > 40) & 
        (df['temperature'] > -50) & 
        ((df['temperature'] - df['dewPoint']) < 2.5)
    )
    return df;


def humidityCorrectedPC(dateTime,pc0_1,pc0_3,pc0_5,pc1_0,pc2_5,pc5_0,pc10_0,hum,likeyHood):
    print(dateTime)
    if likeyHood: 
        print('Condition is satisfied')
        data = {'count': [pc0_1, None, pc0_3, pc0_5, pc1_0, pc2_5, pc5_0, pc10_0, None],
                'D_range': [50, 20, 200, 200, 500, 1500, 2500, 5000, None],
                'D_point': [50, 80, 100, 300, 500, 1000, 2500, 5000, 10000]}
        df1 = pd.DataFrame(data)
        df1['N/D'] = df1['count']/df1['D_range']

        df1['height_ini'] = 0
        df1.loc[7, 'height_ini'] = (2*df1.loc[7, 'count'])/5000
        df1.loc[6, 'height_ini'] = (2*df1.loc[6, 'count'])/2500 - df1.loc[7, 'height_ini']
        df1.loc[5, 'height_ini'] = (2*df1.loc[5, 'count'])/1500 - df1.loc[6, 'height_ini']
        df1.loc[4, 'height_ini'] = (2*df1.loc[4, 'count'])/500 - df1.loc[5, 'height_ini']
        df1.loc[3, 'height_ini'] = (2*df1.loc[3, 'count'])/200 - df1.loc[4, 'height_ini']
        df1.loc[2, 'height_ini'] = (2*df1.loc[2, 'count'])/200 - df1.loc[3, 'height_ini']
        df1.loc[0, 'height_ini'] = (2*df1.loc[0, 'count'])/50 - df1.loc[2, 'height_ini']
        df1.loc[1, 'height_ini'] = (20*(df1.loc[0, 'height_ini']-df1.loc[2, 'height_ini'])/50) + df1.loc[2, 'height_ini']
        df1.loc[1, 'count'] = 0.5*(df1.loc[1, 'height_ini']+df1.loc[2, 'height_ini'])*20

        RH = (hum) * 0.7
        RH = 98 if RH >= 99 else RH
        k = 0.62
        df1['D_dry_point'] = df1['D_point']/((1 + k*(RH/(100-RH)))**(1/3))

        df1['D_dry_range'] = df1['D_dry_point'].diff().shift(-1)

        df1['fit_height_ini'] = 0

        df1.loc[7, 'fit_height_ini'] = (2*df1.loc[7, 'count'])/df1.loc[7, 'D_dry_range']
        df1.loc[6, 'fit_height_ini'] = (2*df1.loc[6, 'count'])/df1.loc[6, 'D_dry_range'] - df1.loc[7, 'fit_height_ini']
        df1.loc[5, 'fit_height_ini'] = (2*df1.loc[5, 'count'])/df1.loc[5, 'D_dry_range'] - df1.loc[6, 'fit_height_ini']
        df1.loc[4, 'fit_height_ini'] = (2*df1.loc[4, 'count'])/df1.loc[4, 'D_dry_range'] - df1.loc[5, 'fit_height_ini']
        df1.loc[3, 'fit_height_ini'] = (2*df1.loc[3, 'count'])/df1.loc[3, 'D_dry_range'] - df1.loc[4, 'fit_height_ini']
        df1.loc[2, 'fit_height_ini'] = (2*df1.loc[2, 'count'])/df1.loc[2, 'D_dry_range'] - df1.loc[3, 'fit_height_ini']
        df1.loc[1, 'fit_height_ini'] = (2*df1.loc[1, 'count'])/df1.loc[1, 'D_dry_range'] - df1.loc[2, 'fit_height_ini']

        df1['slope'] = (df1['fit_height_ini'].shift(-1) - df1['fit_height_ini']) / df1['D_dry_range']
        df1['interc'] = df1['fit_height_ini'] - df1['slope'] * df1['D_dry_point']

        df1['cor_height'] = None
        df1['cor_count'] = 0

        if df1.loc[8, 'D_dry_point'] > 5000:
            df1.loc[7, 'cor_height'] = df1.loc[7, 'slope']*5000 + df1.loc[7, 'interc']
            df1.loc[7, 'cor_count'] = 0.5*df1.loc[7, 'cor_height']*(df1.loc[8, 'D_dry_point']-5000)
        else:
            df1.loc[7, 'cor_height'] = 0
            df1.loc[7, 'cor_count'] = 0

        if (2500<df1.loc[7, 'D_dry_point']<=5000)&(df1.loc[8, 'D_dry_point']>5000):
            df1.loc[6, 'cor_height'] = df1.loc[6, 'slope']*2500 + df1.loc[6, 'interc']
            df1.loc[6, 'cor_count'] = (0.5*(df1.loc[7, 'cor_height']+df1.loc[7, 'fit_height_ini'])*(5000-df1.loc[7, 'D_dry_point'])) + (0.5*(df1.loc[6, 'cor_height']+df1.loc[7, 'fit_height_ini'])*(df1.loc[7, 'D_dry_point']-2500))
        elif (2500<df1.loc[7, 'D_dry_point']<5000)&(df1.loc[8, 'D_dry_point']<5000):
            df1.loc[6, 'cor_height'] = df1.loc[6, 'slope']*2500 + df1.loc[6, 'interc']
            df1.loc[6, 'cor_count'] = (0.5*(df1.loc[6, 'cor_height']+df1.loc[7, 'fit_height_ini'])*(df1.loc[7, 'D_dry_point']-2500)) + (0.5*df1.loc[7, 'fit_height_ini']*(df1.loc[8, 'D_dry_point']-df1.loc[7, 'D_dry_point']))
        elif (df1.loc[7, 'D_dry_point']<2500)&(df1.loc[8, 'D_dry_point']<5000):
            df1.loc[6, 'cor_height'] = df1.loc[7, 'slope']*2500 + df1.loc[7, 'interc']
            df1.loc[6, 'cor_count'] = (0.5*df1.loc[6, 'cor_height'])*(df1.loc[8, 'D_dry_point']-2500)
        else:
            df1.loc[6, 'cor_height'] = df1.loc[7, 'slope']*2500 + df1.loc[7, 'interc']
            df1.loc[6, 'cor_count'] = 0.5*(df1.loc[7, 'cor_height']+df1.loc[6, 'cor_height'])*2500

        if (1000<df1.loc[6, 'D_dry_point']<=2500)&(df1.loc[7, 'D_dry_point']>2500):
            df1.loc[5, 'cor_height'] = df1.loc[5, 'slope']*1000 + df1.loc[5, 'interc']
            df1.loc[5, 'cor_count'] = (0.5*(df1.loc[6, 'cor_height']+df1.loc[6, 'fit_height_ini'])*(2500-df1.loc[6, 'D_dry_point'])) + (0.5*(df1.loc[5, 'cor_height']+df1.loc[6, 'fit_height_ini'])*(df1.loc[6, 'D_dry_point']-1000))
        elif (1000<df1.loc[6, 'D_dry_point']<2500)&(df1.loc[7, 'D_dry_point']<2500):
            df1.loc[5, 'cor_height'] = df1.loc[5, 'slope']*1000 + df1.loc[5, 'interc']
            df1.loc[5, 'cor_count'] = (0.5*(df1.loc[5, 'cor_height']+df1.loc[6, 'fit_height_ini'])*(df1.loc[6, 'D_dry_point']-1000)) + (0.5*(df1.loc[6,'fit_height_ini']+df1.loc[7,'fit_height_ini'])*(df1.loc[7,'D_dry_point']-df1.loc[6,'D_dry_point'])) + (0.5*(df1.loc[7,'fit_height_ini']+df1.loc[6,'cor_height'])*(2500-df1.loc[7,'D_dry_point']))
        elif (df1.loc[6,'D_dry_point']<1000)&(df1.loc[7,'D_dry_point']<2500):
            df1.loc[5,'cor_height'] = df1.loc[6,'slope']*1000 + df1.loc[6,'interc']
            df1.loc[5,'cor_count'] = (0.5*(df1.loc[6,'cor_height']+df1.loc[7,'fit_height_ini'])*(2500-df1.loc[7,'D_dry_point'])) + (0.5*(df1.loc[5,'cor_height']+df1.loc[7,'fit_height_ini'])*(df1.loc[7,'D_dry_point']-1000))
        else:
            df1.loc[5,'cor_height'] = df1.loc[6,'slope']*1000 + df1.loc[6,'interc']
            df1.loc[5,'cor_count'] = 0.5*(df1.loc[6,'cor_height']+df1.loc[5,'cor_height'])*1500

        if (500<df1.loc[5,'D_dry_point']<=1000)&(df1.loc[6,'D_dry_point']>1000):
            df1.loc[4,'cor_height'] = df1.loc[4,'slope']*500 + df1.loc[4,'interc']
            df1.loc[4,'cor_count'] = (0.5*(df1.loc[5,'cor_height']+df1.loc[5,'fit_height_ini'])*(1000-df1.loc[5,'D_dry_point'])) + (0.5*(df1.loc[4,'cor_height']+df1.loc[5,'fit_height_ini'])*(df1.loc[5,'D_dry_point']-500))
        elif (500<df1.loc[5,'D_dry_point']<1000)&(df1.loc[6,'D_dry_point']<1000):
            df1.loc[4,'cor_height'] = df1.loc[4,'slope']*500 + df1.loc[4,'interc']
            df1.loc[4,'cor_count'] = (0.5*(df1.loc[4,'cor_height']+df1.loc[5,'fit_height_ini'])*(df1.loc[5,'D_dry_point']-500)) + (0.5*(df1.loc[5,'fit_height_ini']+df1.loc[6,'fit_height_ini'])*(df1.loc[6,'D_dry_point']-df1.loc[5,'D_dry_point'])) + (0.5*(df1.loc[6,'fit_height_ini']+df1.loc[5,'cor_height'])*(1000-df1.loc[6,'D_dry_point']))
        elif (df1.loc[5,'D_dry_point']<500)&(df1.loc[6,'D_dry_point']<1000):
            df1.loc[4,'cor_height'] = df1.loc[5,'slope']*500 + df1.loc[5,'interc']
            df1.loc[4,'cor_count'] = (0.5*(df1.loc[5,'cor_height']+df1.loc[6,'fit_height_ini'])*(1000-df1.loc[6,'D_dry_point'])) + (0.5*(df1.loc[4,'cor_height']+df1.loc[6,'fit_height_ini'])*(df1.loc[6,'D_dry_point']-500))
        else:
            df1.loc[4,'cor_height'] = df1.loc[5,'slope']*500 + df1.loc[5,'interc']
            df1.loc[4,'cor_count'] = 0.5*(df1.loc[5,'cor_height']+df1.loc[4,'cor_height'])*500

        if (300<df1.loc[4,'D_dry_point']<=500)&(df1.loc[5,'D_dry_point']>500):
            df1.loc[3,'cor_height'] = df1.loc[3,'slope']*300 + df1.loc[3,'interc']
            df1.loc[3,'cor_count'] = (0.5*(df1.loc[4,'cor_height']+df1.loc[4,'fit_height_ini'])*(500-df1.loc[4,'D_dry_point'])) + (0.5*(df1.loc[3,'cor_height']+df1.loc[4,'fit_height_ini'])*(df1.loc[4,'D_dry_point']-300))
        elif (300<df1.loc[4,'D_dry_point']<500)&(df1.loc[5,'D_dry_point']<500):
            df1.loc[3,'cor_height'] = df1.loc[3,'slope']*300 + df1.loc[3,'interc']
            df1.loc[3,'cor_count'] = (0.5*(df1.loc[3,'cor_height']+df1.loc[4,'fit_height_ini'])*(df1.loc[4,'D_dry_point']-300)) + (0.5*(df1.loc[4,'fit_height_ini']+df1.loc[5,'fit_height_ini'])*(df1.loc[5,'D_dry_point']-df1.loc[4,'D_dry_point'])) + (0.5*(df1.loc[5,'fit_height_ini']+df1.loc[4,'cor_height'])*(500-df1.loc[5,'D_dry_point']))
        elif (df1.loc[4,'D_dry_point']<300)&(df1.loc[5,'D_dry_point']<500):
            df1.loc[3,'cor_height'] = df1.loc[4,'slope']*300 + df1.loc[4,'interc']
            df1.loc[3,'cor_count'] = (0.5*(df1.loc[4,'cor_height']+df1.loc[5,'fit_height_ini'])*(500-df1.loc[5,'D_dry_point'])) + (0.5*(df1.loc[3,'cor_height']+df1.loc[5,'fit_height_ini'])*(df1.loc[5,'D_dry_point']-300))
        else:
            df1.loc[3,'cor_height'] = df1.loc[4,'slope']*300 + df1.loc[4,'interc']
            df1.loc[3,'cor_count'] = 0.5*(df1.loc[4,'cor_height']+df1.loc[3,'cor_height'])*200

        if (100<df1.loc[3,'D_dry_point']<=300)&(df1.loc[4,'D_dry_point']>300):
            df1.loc[2,'cor_height'] = df1.loc[2,'slope']*100 + df1.loc[2,'interc']
            df1.loc[2,'cor_count'] = (0.5*(df1.loc[3,'cor_height']+df1.loc[3,'fit_height_ini'])*(300-df1.loc[3,'D_dry_point'])) + (0.5*(df1.loc[2,'cor_height']+df1.loc[3,'fit_height_ini'])*(df1.loc[3,'D_dry_point']-100))
        elif (100<df1.loc[3,'D_dry_point']<300)&(df1.loc[4,'D_dry_point']<300):
            df1.loc[2,'cor_height'] = df1.loc[2,'slope']*100 + df1.loc[2,'interc']
            df1.loc[2,'cor_count'] = (0.5*(df1.loc[2,'cor_height']+df1.loc[3,'fit_height_ini'])*(df1.loc[3,'D_dry_point']-100)) + (0.5*(df1.loc[3,'fit_height_ini']+df1.loc[4,'fit_height_ini'])*(df1.loc[4,'D_dry_point']-df1.loc[3,'D_dry_point'])) + (0.5*(df1.loc[4,'fit_height_ini']+df1.loc[3,'cor_height'])*(300-df1.loc[4,'D_dry_point']))
        elif (df1.loc[3,'D_dry_point']<100)&(df1.loc[4,'D_dry_point']<300):
            df1.loc[2,'cor_height'] = df1.loc[3,'slope']*100 + df1.loc[3,'interc']
            df1.loc[2,'cor_count'] = (0.5*(df1.loc[3,'cor_height']+df1.loc[4,'fit_height_ini'])*(300-df1.loc[4,'D_dry_point'])) + (0.5*(df1.loc[2,'cor_height']+df1.loc[4,'fit_height_ini'])*(df1.loc[4,'D_dry_point']-100))
        else:
            df1.loc[2,'cor_height'] = df1.loc[3,'slope']*100 + df1.loc[3,'interc']
            df1.loc[2,'cor_count'] = 0.5*(df1.loc[3,'cor_height']+df1.loc[2,'cor_height'])*200

        if (50<df1.loc[2,'D_dry_point']<=100)&(df1.loc[3,'D_dry_point']>100):
            df1.loc[0,'cor_height'] = df1.loc[1,'slope']*50 + df1.loc[1,'interc']
            df1.loc[0,'cor_count'] = (0.5*(df1.loc[2,'cor_height']+df1.loc[2,'fit_height_ini'])*(100-df1.loc[2,'D_dry_point'])) + (0.5*(df1.loc[0,'cor_height']+df1.loc[2,'fit_height_ini'])*(df1.loc[2,'D_dry_point']-50))
        elif (50<df1.loc[2,'D_dry_point']<100)&(df1.loc[3,'D_dry_point']>100):
            df1.loc[0,'cor_height'] = df1.loc[1,'slope']*50 + df1.loc[1,'interc']
            df1.loc[0,'cor_count'] = (0.5*(df1.loc[0,'cor_height']+df1.loc[2,'fit_height_ini'])*(df1.loc[2,'D_dry_point']-50)) + (0.5*(df1.loc[2,'fit_height_ini']+df1.loc[3,'fit_height_ini'])*(df1.loc[3,'D_dry_point']-df1.loc[2,'D_dry_point'])) + (0.5*(df1.loc[3,'fit_height_ini']+df1.loc[2,'cor_height'])*(100-df1.loc[3,'D_dry_point']))
        elif (df1.loc[2,'D_dry_point']<50)&(df1.loc[3,'D_dry_point']>100):
            df1.loc[0,'cor_height'] = df1.loc[2,'slope']*50 + df1.loc[2,'interc']
            df1.loc[0,'cor_count'] = (0.5*(df1.loc[2,'cor_height']+df1.loc[3,'fit_height_ini'])*(100-df1.loc[3,'D_dry_point'])) + (0.5*(df1.loc[0,'cor_height']+df1.loc[3,'fit_height_ini'])*(df1.loc[3,'D_dry_point']-50))
        else:
            df1.loc[0,'cor_height'] = df1.loc[2,'slope']*50 + df1.loc[2,'interc']
            df1.loc[0,'cor_count'] = 0.5*(df1.loc[2,'cor_height']+df1.loc[0,'cor_height'])*50
            
        # self.pc0_1Cor, self.pc0_3Cor, self.pc0_5Cor, self.pc1_0Cor, self.pc2_5Cor, self.pc5_0Cor, self.pc10_0Cor = \
        return [df1.loc[0,'cor_count'], df1.loc[2,'cor_count'], df1.loc[3,'cor_count'], df1.loc[4,'cor_count'], df1.loc[5,'cor_count'], df1.loc[6,'cor_count'], df1.loc[7,'cor_count']];
    else:
        print('Condition is not satisfied')
        return pc0_1,pc0_3,pc0_5,pc1_0,pc2_5,pc5_0,pc10_0
    

def humidityCorrectedPM(df):
    df['pm0_1HC']  =  df['pm0_1']
    df['pm0_3HC']  =  df['pm0_3']
    df['pm0_5HC']  =  df['pm0_5']
    df['pm1_0HC']  =  df['pm1_0']
    df['pm2_5HC']  =  df['pm2_5']
    df['pm5_0HC']  =  df['pm5_0']    
    df['pm10_0HC'] =  df['pm10_0']    

    # Coefficients
    m0_1 = 8.355696123812269e-07
    m0_3 = 2.2560825222215327e-05
    m0_5 = 0.00010446111749483851
    m1_0 = 0.0008397941861044865
    m2_5 = 0.013925696906339288
    m5_0 = 0.12597702778750686
    m10_0 = 1.0472

    # Create a mask for rows where fogLikelihood is True
    mask = df['fogLikelihood'] == True

    # Apply humidity correction only to the rows where fogLikelihood is True
    df.loc[mask, 'pm0_1HC'] = m0_1 * df.loc[mask, 'pc0_1HC']
    df.loc[mask, 'pm0_3HC'] = df.loc[mask, 'pm0_1HC'] + m0_3 * df.loc[mask, 'pc0_3HC']
    df.loc[mask, 'pm0_5HC'] = df.loc[mask, 'pm0_3HC'] + m0_5 * df.loc[mask, 'pc0_5HC']
    df.loc[mask, 'pm1_0HC'] = df.loc[mask, 'pm0_5HC'] + m1_0 * df.loc[mask, 'pc1_0HC']
    df.loc[mask, 'pm2_5HC'] = df.loc[mask, 'pm1_0HC'] + m2_5 * df.loc[mask, 'pc2_5HC']
    df.loc[mask, 'pm5_0HC'] = df.loc[mask, 'pm2_5HC'] + m5_0 * df.loc[mask, 'pc5_0HC']
    df.loc[mask, 'pm10_0HC'] = df.loc[mask, 'pm5_0HC'] + m10_0 * df.loc[mask, 'pc10_0HC']

    return df
# file_pattern = '/Users/lakitha/mintsData/raw/*/*/*/*/MINTS_001e064a8753_IPS7100_*.csv'

# csv_files = sorted(glob.glob(file_pattern))

# # Read and concatenate all CSV files in alphabetical order into a single DataFrame
# df = pd.concat((pd.read_csv(file) for file in csv_files), ignore_index=True)

# # Display the first few rows of the merged DataFrame
# print(df.head())

# df.to_pickle('IPS7100.pkl')

# file_pattern = '/Users/lakitha/mintsData/raw/*/*/*/*/MINTS_001e064a8753_BME280V2_*.csv'

# csv_files = sorted(glob.glob(file_pattern))

# # Read and concatenate all CSV files in alphabetical order into a single DataFrame
# df = pd.concat((pd.read_csv(file) for file in csv_files), ignore_index=True)

# # Display the first few rows of the merged DataFrame
# print(df.head())

# df.to_pickle('BME280V2.pkl')


# # Load the DataFrame from the pickle file
# dfIPS = pd.read_pickle('IPS7100.pkl')

# # Display the DataFrame to confirm it loaded correctly
# print(dfIPS.head())


# # Load the DataFrame from the pickle file
# dfBME = pd.read_pickle('BME280V2.pkl')

# # Display the DataFrame to confirm it loaded correctly
# print(dfBME.head())

# dfIPS['dateTime'] = pd.to_datetime(dfIPS['dateTime'], errors='coerce')
# dfIPS = dfIPS.dropna(subset=['dateTime'])
# dfIPS.set_index('dateTime', inplace=True)

# # Resample to 5-minute intervals and calculate the mean for each interval
# dfIPS_5min_avg = dfIPS.resample('5T').mean()
# dfIPS_5min_avg.to_pickle('dfIPS5minavg.pkl')
# print(dfIPS_5min_avg.head())


# dfBME['dateTime'] = pd.to_datetime(dfBME['dateTime'], errors='coerce')
# dfBME = dfBME.dropna(subset=['dateTime'])
# dfBME.set_index('dateTime', inplace=True)

# # Resample to 5-minute intervals and calculate the mean for each interval
# dfBME_5min_avg = dfBME.resample('5T').mean()
# dfBME_5min_avg.to_pickle('dfBME5minavg.pkl')
# print(dfBME_5min_avg.head())


# dfIPS_5min_avg = pd.read_pickle('dfIPS5minavg.pkl')
# dfBME_5min_avg = pd.read_pickle('dfBME5minavg.pkl')

# print(dfIPS_5min_avg.head())
# print(dfBME_5min_avg.head())

# mergedIPSBME5Min = pd.merge(dfIPS_5min_avg , dfBME_5min_avg, left_index=True, right_index=True, how='inner')
# mergedIPSBME5Min.to_pickle('mergedIPSBME5Min.pkl')
# print(mergedIPSBME5Min.head())


# withLikelyHoodIPSBME5Min = setFogLikelyhood(mergedIPSBME5Min)
# withLikelyHoodIPSBME5Min.to_pickle('withLikelyHoodIPSBME5Min.pkl')
# withLikelyHoodIPSBME5Min.to_csv('withLikelyHoodIPSBME5Min.csv')



#####

withLikelyHoodIPSBME5Min = pd.read_pickle('withLikelyHoodIPSBME5Min.pkl')
# print(withLikelyHoodIPSBME5Min.head())

withLikelyHoodIPSBME5MinWithHCPC = withLikelyHoodIPSBME5Min 

# hcValuesOnly =  withLikelyHoodIPSBME5Min.apply(
#                 lambda row: humidityCorrectedPC(
#                     row.name,
#                     row['pc0_1'],
#                     row['pc0_3'],
#                     row['pc0_5'],
#                     row['pc1_0'],
#                     row['pc2_5'],
#                     row['pc5_0'],
#                     row['pc10_0'],
#                     row['humidity'],
#                     row['fogLikelihood']
#                 ),
#                 axis=1
# )

# hcValuesOnly.to_pickle('hcValuesOnly.pkl')
# print(hcValuesOnly.head())


# hcValuesOnly = pd.read_pickle('hcValuesOnly.pkl')
# hcSeries = pd.Series(hcValuesOnly)

# hcPCValuesOnlyDF = pd.DataFrame(hcSeries.tolist(), index=hcSeries.index, columns=['pc0_1HC', 'pc0_3HC', 'pc0_5HC', 'pc1_0HC', 'pc2_5HC', 'pc5_0HC', 'pc10_0HC'])
# hcPCValuesOnlyDF.to_pickle('hcPCValuesOnlyDF.pkl')

# # # Ensure that the index matches the original DataFrame
# withLikelyHoodIPSBME5MinWithHCPC = withLikelyHoodIPSBME5MinWithHCPC.join(hcPCValuesOnlyDF)

# # Print the resulting DataFrame
# print(withLikelyHoodIPSBME5MinWithHCPC.head())
# withLikelyHoodIPSBME5MinWithHCPC.to_pickle('withLikelyHoodIPSBME5MinWithHCPC.pkl') 


withLikelyHoodIPSBME5MinWithHCPC   = pd.read_pickle('withLikelyHoodIPSBME5MinWithHCPC.pkl')

withLikelyHoodIPSBME5MinWithHCPCPM = humidityCorrectedPM(withLikelyHoodIPSBME5MinWithHCPC)

# Print the resulting DataFrame
print(withLikelyHoodIPSBME5MinWithHCPCPM.head())
withLikelyHoodIPSBME5MinWithHCPCPM.to_pickle('withLikelyHoodIPSBME5MinWithHCPCPM.pkl') 

withLikelyHoodIPSBME5MinWithHCPCPM.to_csv('withLikelyHoodIPSBME5MinWithHCPCPM.csv')



