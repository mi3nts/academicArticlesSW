
import pandas as pd





def getDataFrame(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)
    df = df.drop(index=range(8))

    # print(df.head())

    df.columns = [ 'date', 'time', 'internalTemperature', 'pm2_5BAM']

    df = df[df['date'] != 'Date']

    # Ensure 'date' is datetime and 'time' is a string before concatenating
    df['date'] = pd.to_datetime(df['date'])
    df['time'] = df['time'].astype(str)

    # Combine 'date' and 'time' into a single datetime column
    df['dateTime'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])

    # Set DateTime as the index
    df.set_index('dateTime', inplace=True)

    # Drop the original Date and Time columns
    df.drop(columns=['date', 'time'], inplace=True)

    return df


def getDataFrameV2(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)
    df = df.drop(index=range(5))

    df[['date', 'time', 'internalTemperature', 'pm2_5BAM']] = df['Five-Minute Data'].str.split(',', expand=True)
    
    # Drop the original column if no longer needed
    df.drop(columns=['Five-Minute Data'], inplace=True)

    df = df[df['date'] != 'Date']

    # Ensure 'date' is datetime and 'time' is a string before concatenating
    df['date'] = pd.to_datetime(df['date'])
    df['time'] = df['time'].astype(str)

    # Combine 'date' and 'time' into a single datetime column
    df['dateTime'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])

    # Set DateTime as the index
    df.set_index('dateTime', inplace=True)

    # Drop the original Date and Time columns
    df.drop(columns=['date', 'time'], inplace=True)


    df.to_csv('df.csv')

    return df



# Specify the file path
df1 = getDataFrame('C-310 PM 2.5 April 09 to August 02 2024.xlsx')
print(df1.head())

df4 = getDataFrame('C-310 PM 2.5 January 27 to April 09.xlsx')
print(df4.head())

df2 = getDataFrameV2('C-310 PM 2.5 December 23.xlsx')
print(df2.head())

df3 = getDataFrameV2('C-310 PM 2.5 January 24.xlsx')
print(df3.head())

df5 = getDataFrameV2('C-310 PM 2.5 November 23.xlsx')
print(df5.head())

bam = pd.concat([df1, df2, df3, df4, df5])

bam = bam.sort_values(by='dateTime')

bam['pm2_5BAM'] = bam['pm2_5BAM'].replace(r'[^0-9.-]', '', regex=True)
bam['pm2_5BAM'] = pd.to_numeric(bam['pm2_5BAM'], errors='coerce')
bam = bam[bam['pm2_5BAM'] >= 0]
bam = bam[bam['pm2_5BAM'] <= 2000]

bam['internalTemperature'] = pd.to_numeric(bam['internalTemperature'], errors='coerce')


print(bam.head())
bam.to_csv('bam.csv')
bam.to_pickle('bam.pkl') 

