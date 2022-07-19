import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
import os.path
import arescon_objects as agd

OUTPUT_PATH = '\\Data\\'


def create_name_file(st_date: datetime, name_client: str, type_file='_output_'):
    return name_client + type_file + st_date.strftime("%Y-%m-%d") + '.xlsx'


def open_data(name_file: str, func='clear', rel_path=OUTPUT_PATH):
    df_data = [pd.DataFrame(), pd.DataFrame()]
    subdir = os.getcwd() + rel_path
    data_path = subdir + name_file

    if func == 'clear':
        df_data[0] = pd.read_excel(data_path, sheet_name='calc', header=0)
        df_data[0]['ext_id'] = df_data[0]['ext_id'].astype(str)
    elif func == 'mount':
        df_data[0] = pd.read_excel(data_path, sheet_name='Монтаж', header=0)
        df_data[1] = pd.read_excel(data_path, sheet_name='Наряды', header=0)
    else:
        df_data[0] = pd.read_excel(data_path, sheet_name='calc', header=0)
        df_data[1] = pd.read_excel(data_path, sheet_name='load', header=0)
# переименовать столбец №СИ в ext_id
        if '№ СИ' in df_data[1].columns:
            df_data[1] = df_data[1].rename(columns={'№ СИ': 'ext_id'})
        if 'Л/С' in df_data[1].columns:
            df_data[1] = df_data[1].rename(columns={'Л/С': '№ кв'})

        df_data[0]['ext_id'] = df_data[0]['ext_id'].astype(str)
        df_data[1]['ext_id'] = df_data[1]['ext_id'].astype(str)
        df_data[1]['№ кв'] = df_data[1]['№ кв'].astype(str)
        df_data[0] = df_data[0].set_index('ext_id')
        df_data[1] = df_data[1].set_index('ext_id')

    return df_data


def write_data(name_file: str, df: pd.DataFrame, sheet: str, is_header=True, str_row=0, rel_path=OUTPUT_PATH):
    subdir = os.getcwd()
    data_path = subdir + rel_path + name_file

    isfl = os.path.isfile(data_path)
    xlmode = 'w'
    if isfl:
        book = load_workbook(data_path)
        xlmode = 'a'

    with pd.ExcelWriter(data_path, mode=xlmode) as writer:
        if isfl:
            writer.book = book
            writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
        df.to_excel(writer, sheet_name=sheet, index=True, header=is_header, startrow=str_row+1)
        writer.save()
    print("write sheet " + sheet + " in " + name_file)

def clear_data(df: pd.DataFrame):
    df.sort_values(by='real_time', inplace=True)
    df.drop_duplicates(subset='value', keep='first', inplace=True)
    df['cons'] = df['real_data'].diff()
    df.drop_duplicates(subset='ext_id', keep='last', inplace=True)

    return df

def clear_data_fabric(func):
    for st_date in agd.START_DATE:
        name_file = create_name_file(st_date, agd.CLIENT_NAME)
        df_data = open_data(name_file)[0]
        df = clear_data(df_data)

        write_data(name_file, df, func, str,str_row=-1)

def split_data(func):
    for st_date in agd.START_DATE:
        name_file = create_name_file(st_date, agd.CLIENT_NAME)
        df = open_data(name_file, 'load')
        df_split = pd.merge(df[0], df[1], on='ext_id', how='outer', left_on=True, indicator=True)
        write_data(name_file, df_split, 'split')


def set_actual_mounting(func):
    COLUMNS_RESULTS = ['Дата наряда','Дата операции','Дом','Cекция','Этаж','Квартира',
                       'ПУ','Показание','Терминал']
    COLUMNS_ORDERS_CWS = ['Дата создания','дата','Дом','Секция','Этаж','Квартира','Новый пу хвс',
                          'показания новый хвс','номер нового си']
    COLUMNS_ORDERS_HWS = ['Дата создания','дата','Дом','Секция','Этаж','Квартира','Новый пу хвс',
                          'показания новый гвс','номер нового си']
    df_results = pd.DataFrame(columns=COLUMNS_RESULTS)

    name_file = create_name_file(agd.START_DATE[0], agd.CLIENT_NAME, '_mounting_')
    df = open_data(name_file, 'mount')
    df_mounts = df[0]
    df_results[COLUMNS_RESULTS] = df[1].loc[~df[1]['Новый пу хвс'].isna()][COLUMNS_ORDERS_CWS].copy()
    df_results['Услуга'] = 'ХВС'

    df_results[COLUMNS_RESULTS].append(df[1].loc[~df[1]['Новый пу гвс'].isna()][COLUMNS_ORDERS_HWS])
    print(df_results)
        # .drop_duplicates(subset=['id', 'ext_id'], keep='last', inplace=True)
    df_actual = df_results[[df_mounts]]


def switch_func(arg='clear'):
    switcher = {
        'clear': clear_data_fabric,
        'split': split_data,
        'mount': set_actual_mounting
    }
    switcher.get(arg)(arg)
