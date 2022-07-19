from datetime import datetime, timedelta
import peewee as pw
import sshtunnel
from sqlalchemy import create_engine
import pandas as pd
import evaluate_data as ed
from pa3_postgresql import *
from dcs_mysql import *


class AresconData:
# TODO вместо функций организации SSH добавить объект класса SSH
    def __init__(self, start_date: str, end_date: str, name_agent=None, post_working=False, ts_name="Приват Сквер"):
        self._COLUMNS_LOG = ['start_date', 'ext_id', 'st_date_stamp', 'st_date_serv',
                             'type_art', 'count_err', 'pcon_min', 'pcon_mean', 'pcon_max']
        self._tszh_name = ts_name
        self._start_date = start_date
        self._end_date = end_date
        self._post_working = post_working
        self._is_sql = True
        self._period_exam = 12
        self._terminal_model = 1
        self._agent_name = name_agent
        # инициация MySQL БД
        self._db_connection = None
        self._db_username = 'processing'
        self._db_password = ''
        self._db_url = '185.148.37.101'
        self._db_port = '63306'
        self._db_name = 'processing'
        # инициация Postgres БД ('private')
        self._ssh_host = ('94.228.246.228', 7525)
        self._ssh_login = 'user'
        self._ssh_psw = 'iu97GHd%g'
        self._server = None
        self._psql_rem_address = ('localhost', 5432)
        self._psql_login = 'postgres'
        self._psql_psw = 'postgres'
        self._psql_url = 'localhost'
        self._psql_name = 'arescon_prod'
        self._engine = None
        # инициация datafarmes
        self._df_counters = pd.DataFrame()
        self._df_terminals = pd.DataFrame()
        self._df_data = pd.DataFrame()
        self._df_log = pd.DataFrame(columns=self._COLUMNS_LOG)
        self._df_result = pd.DataFrame()
        self._default_weight = 0.01    # вес импульса
        self._default_v_consume = 2.4  # скорость потребления воды для 15" в куб/час на 2-ух точках
        # инициация выхдодного формата
        self._format_h_row = 15
        self._format_w_col = 90
        self._format_cell = {'align': 'right', 'num_format': '0.00'}
        self._COLUMNS_RESULT = ['№ кв',	'Услуга', 'Модель',	'№ ПУ',	'Начальная дата', 'Конечная дата',
                                'Начало',	'Конец',	'Потребление',	'Лицевой счет', 'ext_id']
        self._sort_column = '№ кв'
        self._prefix_account = '100000000'

    def __del__(self):
        if self._db_connection is not None:
            self._db_connection.close()

    @property
    def agent_name(self):
        return self._agent_name

    @property
    def db_name(self):
        return self._db_name

    @property
    def lk3_host(self):
        return self._psql_url

    @property
    def lk3_login(self):
        return self._psql_login

    @property
    def lk3_password(self):
        return self._psql_psw

    @property
    def lk3_db_name(self):
        return self._psql_name

    def open_lk3_db(self):
        self.open_ssh()
        lk3_db = pw.PostgresqlDatabase(self._psql_name, host=self._psql_url, port=self._server.local_bind_port,
                                       user=self._psql_login, password=self._psql_psw)
        pa3_database_proxy.initialize(lk3_db)

    @property
    def post_working(self):
        return self._post_working

    @post_working.setter
    def post_working(self, p_working=True):
        self._post_working = p_working

    def set_sql(self, is_sql=True):
        self._is_sql = is_sql

    def set_period_exam(self, period: int = 12):
        self._period_exam = period

    def is_sql(self):
        return self._is_sql

    def get_startdate(self):
        return self._start_date

    def get_enddate(self):
        return self._end_date

    def get_datequery(self):
        start_date = datetime.strptime(self._start_date, '%Y-%m-%d %H:%M') - timedelta(self._period_exam * 30)
        end_date_query = datetime.now()
        return start_date, end_date_query

    def get_weight(self, type_model: str = None):
        if type_model is None:
            return self._default_weight
        else:
            return self._default_weight

    def get_v_consume(self, d_pipe: float = 15.0):
        if d_pipe == 15.0:
            return self._default_v_consume
        else:
            return self._default_v_consume

    def get_term_model(self):
        return self._terminal_model

    def get_result_columns(self) -> list:
        return self._COLUMNS_RESULT

    def get_sort_column(self) -> str:
        return self._sort_column

    def log_append(self, row: list):
        self._df_log = self._df_log.append(pd.Series(row, index=self._COLUMNS_LOG), ignore_index=True)
        print("терминал ->" + row[1] + ", " + row[4])

    def open_ssh(self):
        sshtunnel.SSH_TIMEOUT = 5.0
        sshtunnel.TUNNEL_TIMEOUT = 5.0

        # Create an SSH server
        self._server = sshtunnel.SSHTunnelForwarder(
            self._ssh_host,
            ssh_username=self._ssh_login,
            ssh_password=self._ssh_psw,
            remote_bind_address=self._psql_rem_address
        )
        self._server.start()
        local_port = str(self._server.local_bind_port)
        self._engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
                                self._psql_login, self._psql_psw, self._psql_url,
                                local_port, self._psql_name))
        return self._server

    def close_ssh(self):
        if self._server is not None:
            self._server.close()
            self._server = None

# загрузить счетчики SQL query
    def get_counters_sql(self):

        self._df_counters = pd.read_sql("SELECT hs.build, acc.flat as flat, mtm.name as mt_name, svc.name as услуга, "
                                        "meters.num as mt_num, meters.terminal_id "
                                        "FROM houses as hs, meters, accounts as acc, meter_models as mtm, "
                                        "meters_accounts as mtac, service_types as svc "
                                        "WHERE hs.id = meters.house_id AND meters.meter_model_id = mtm.id "
                                        "AND acc.id = mtac.account_id AND meters.id = mtac.meter_id "
                                        "AND mtm.meter_type_id = 1 "
                                        "AND meters.service_type_id = svc.id ORDER BY hs.build, acc.flat",
                                        self._engine)
        self._df_counters.terminal_id = self._df_counters.terminal_id.fillna(0).astype('int32')
        return self._df_counters

# загрузить счетчики с последней калибровкой
    def get_counters_lk3(self):
        self.open_lk3_db()
        return (Meters.select(Meters.id, Meters.num, MeterModels.weight, Meters.terminal_id).
                join(MetersAccounts).
                join(Accounts).
                join(Houses).
                join(Tszhs).
                join(MeterModels).
                where(Tszhs.name == self._tszh_name and
                      MeterModels.meter_type == 1))

    def get_check_values(self):
        if self._server is None:
            self.open_ssh()
        self._df_counters = pd.read_sql("SELECT hs.build, acc.flat as flat, mtm.name as mt_name, svc.name as услуга, "
                                        "meters.num as mt_num, meters.terminal_id "
                                        "FROM houses as hs, meters, accounts as acc, meter_models as mtm, "
                                        "meters_accounts as mtac, service_types as svc "
                                        "WHERE hs.id = meters.house_id AND meters.meter_model_id = mtm.id "
                                        "AND acc.id = mtac.account_id AND meters.id = mtac.meter_id "
                                        "AND mtm.meter_type_id = 1 "
                                        "AND meters.service_type_id = svc.id ORDER BY hs.build, acc.flat",
                                        self._engine)

# загрузить терминалы
    def get_terminals(self, include_term: list = None):
        if self._is_sql:
            sql_engine = create_engine(
                'mysql+pymysql://' + self._db_username + ':' + self._db_password + '@' + self._db_url + ':'
                + self._db_port + '/' + self._db_name, pool_recycle=3600)
            self._db_connection = sql_engine.connect()

            sql_query = "SELECT term.id, term.ext_id, term.lastconnect FROM terminals AS term"
            if include_term is None:
                sql_query_term = ", (SELECT term_si.id, term_si.ext_id FROM terminals AS term_si " \
                                 "WHERE " \
                                 "term_si.lastconnect > LAST_DAY(DATE_SUB(NOW(), INTERVAL 2 MONTH)) ) " \
                                 "AS term_si "
                # sql_query_term = " "
                sql_query = sql_query + " " + sql_query_term + \
                            "WHERE term.id_root = term_si.id AND " \
                            "term.id_terminals_model = " + str(self._terminal_model) + " AND " \
                            "term.ext_id REGEXP \"[[:xdigit:]]{16}(01|02){1}$\""
            else:
                sql_query = sql_query + " WHERE "
                for term in include_term:
                    if 'term.ext_id = ' in sql_query:
                        sql_query = sql_query + " OR "
                    sql_query = sql_query + 'term.ext_id = \"' + term + '\"'

            self._df_terminals = pd.read_sql(sql_query, self._db_connection)
        else:
            self._df_terminals = pd.read_excel('input.xlsx', header=0)
            self._df_terminals['ext_id'] = self._df_terminals['ext_id'].astype(str)

        return self._df_terminals

# загрузить данные
    def get_data(self, ext_id: str = '', index: int = None):
        start_date, end_date_query = self.get_datequery()
        if index is None:
            sql_query = "SELECT tdata.id, term.ext_id, tdata.value, tdata.stamp, tdata.date_server, tdata.date_terminal\
                                    FROM terminals AS term, terminals_data AS tdata \
                                    WHERE ((tdata.date_server BETWEEN \"" + start_date.strftime('%Y-%m-%d') + "\"\
                                    AND \"" + end_date_query.strftime('%Y-%m-%d') + "\") \
                                    OR (tdata.stamp BETWEEN \"" + start_date.strftime('%Y-%m-%d') + "\"\
                                    AND \"" + end_date_query.strftime('%Y-%m-%d') + "\")) \
                                    AND tdata.id_terminal = term.id AND term.ext_id = \"" + ext_id + "\" ORDER BY tdata.id"
        else:
            sql_query = "SELECT tdata.id, term.ext_id, tdata.value, tdata.stamp, tdata.date_server, tdata.date_terminal\
                                    FROM terminals AS term, terminals_data AS tdata \
                                    WHERE ((tdata.date_server BETWEEN \"" + start_date.strftime('%Y-%m-%d') + "\"\
                                    AND \"" + end_date_query.strftime('%Y-%m-%d') + "\") \
                                    OR (tdata.stamp BETWEEN \"" + start_date.strftime('%Y-%m-%d') + "\"\
                                    AND \"" + end_date_query.strftime('%Y-%m-%d') + "\")) \
                                    AND tdata.id_terminal = term.id AND term.id = \"" + str(index) + "\" ORDER BY tdata.id"
            self._df_data.drop(self._df_data.index, inplace=True)
# попытки выполнить запрос
        is_connection_false = True
        while is_connection_false:
            try:
                self._df_data = pd.read_sql(sql_query, self._db_connection)
                is_connection_false = False
            except Exception as e:
                print(e)
                continue
        return self._df_data

# загрузить все терминалы с данными по датам данных
    def get_alarms(self):
        return TerminalsData.get_by_dates(self._start_date, self._end_date, 3)

# обновление исходного набора данных в подмножество согласно условию выборки
    def update_df_data(self, criteria: pd.DataFrame):
        self._df_data = self._df_data[criteria]
        return self._df_data

# согласование адреса набора данных в объекте и вне объекта
    def set_df_data(self, df: pd.DataFrame):
        self._df_data = df
        return self._df_data

    def result_append(self):
        self._df_result = self._df_result.append(self._df_data)

# выгрузка данных в файл
    def upload_data(self):
        if self._df_result.empty:
           print("нет данных для записи в файл")
        else:
            self._df_result.drop(['value', 'id', 'err'], axis=1, inplace=True)
            name_file = ed.create_name_file(self._start_date, self._agent_name)
            ed.write_data(name_file, self._df_result, sheet='calc', is_header=True, str_row=-1)
            ed.write_data(name_file, self._df_log, sheet='log', is_header=True, str_row=-1)

    def merge(self):
        name_file = ed.create_name_file(self._start_date, self._agent_name)
        df = ed.open_data(name_file, 'load')
        df_calc = df[0]
        df_load = df[1]
        # df_calc['res_cons'] = df_calc.apply(lambda x: x*0.1 if (x['Модель'] == 'Minomes') else x)

        # создание df merge
        df_merge = df_load.merge(df_calc['cons'], on='ext_id', how='left')

        # создать df для страницы c результатами - скопировать с merge
        df_result = df_merge.copy()
        df_result.reset_index(inplace=True)

# данные из столбца "Конец" переписать в столбец "Начало", в столбец "Конец" записать сумму "Начало" и res_cons
        df_result['Начало'] = df_result['Конец']
        df_result['Конец'] = df_result['Начало'] + df_result['cons']
        df_result['Потребление'] = df_result['cons']
        df_result.round({"Начало": 2, "Конец": 2, "Потребление": 2})

# в "Начальная дата" и "Конечная дата" записать начальную и конечную даты выборки
        df_result['Начальная дата'] = self._start_date
        df_result['Конечная дата'] = self._end_date
# формсирование Лицевых счетов
        df_result['Лицевой счет'] = df_result['№ кв'].str.extract(r'(\s\d+\s*$)')
        df_result['Префикс'] = self._prefix_account
        criteria = ~df_result['№ кв'].isna() & (df_result['№ кв'].str.len() == 2)
        df_result.loc[criteria, 'Префикс'] = self._prefix_account[:len(self._prefix_account)-1]
        criteria = ~df_result['№ кв'].isna() & (df_result['№ кв'].str.len() == 3)
        df_result.loc[criteria, 'Префикс'] = self._prefix_account[:len(self._prefix_account)-2]
        criteria = df_result['Лицевой счет'].isna() & ~df_result['№ кв'].isna()
        df_result.loc[criteria, 'Лицевой счет'] = df_result.loc[criteria, 'Префикс'] + df_result.loc[criteria, '№ кв']
        df_result['Лицевой счет'].str.strip()
# итоговая стока
#         last_row = {'№ кв':'Итого', 'Начало': df_result['Начало'].sum(), 'Конец':
#                    df_result['Конец'].sum(), 'Потребление': df_result['Потребление'].sum()}
#         df_result = df_result.append(last_row, ignore_index=True)
        drop_columns = list(set(df_result.columns).difference(self._COLUMNS_RESULT))
        df_result.drop(columns=drop_columns, inplace=True)
        df_result.sort_values(by=self._sort_column, inplace=True)
        df_result = df_result[self._COLUMNS_RESULT]

# записать страницы merge и результатов в отдельные файлы
        name_file = ed.create_name_file(self._start_date, self._agent_name, ' Выгрузка!')
        ed.write_data(name_file, df_result, 'результаты', str_row=-1)
        ed.write_data(name_file, df_merge, 'merge', str_row=-1)


class GetDataPrivate(AresconData):

    def __init__(self, start_date: str, end_date: str):
        super().__init__(start_date, end_date, 'private')
        self._db_password = 'JXJuGFVgK7bVXkf9W'
        self._db_url = '94.228.246.228'
        self._COLUMNS_RESULT = ['Корпус', '№ кв',	'Услуга', 'Модель',	'№ ПУ',	'Начальная дата', 'Конечная дата',
                                'Начало',	'Конец',	'Потребление',	'Лицевой счет', 'ext_id']
        self._server = self.open_ssh()
        self._psql_db = pw.PostgresqlDatabase(self.lk3_db_name, host=self.lk3_host, port=self._server.local_bind_port,
                                              user=self.lk3_login, password=self.lk3_password)


class GetDataKvart23(AresconData):

    def __init__(self, start_date: str, end_date: str):
        super().__init__(start_date, end_date, 'kvart23')
        self._tszh_name = "Кварт-23"
        self._ssh_psw = 'gh7HJ5rt'
        self._db_password = '3iPAasaeeMN9zJoYr'
        self._db_url = '46.39.252.67'
        # инициация Postgres БД ('private')
        self._ssh_host = ('46.39.252.67', 4357)
        self._ssh_login = 'root'
        self._ssh_psw = 'gh7HJ5rt'
        self._psql_rem_address = ('localhost', 5432)
        self._psql_login = 'postgres'
        self._psql_psw = '3iPAasaeeMN9zJoYr'
        self._psql_url = 'localhost'
        self._psql_name = 'arescon_prod'
        # инициация выхдодного формата
        self._format_row_heght = 15


class GetDataKvart126(AresconData):
    def __init__(self, start_date: str, end_date: str):
        super().__init__(start_date, end_date, 'kvart126')
        self._tszh_name = "Кварт-126"
        self._db_username = 'stm01'
        self._db_password = 'bcgjl_dsgjldthnd123'
        self._db_url = '185.148.37.101'
        self._db_name = 'processing_kvart'
    # инициация Postgres БД ('private')
        self._ssh_host = ('185.148.37.96', 22)
        self._ssh_login = 'user'
        self._ssh_psw = 'ythKL67'
        self._psql_rem_address = ('localhost', 5432)
        self._psql_login = 'postgres'
        self._psql_psw = 'postgres'
        self._psql_url = 'localhost'
        self._psql_name = 'arescon_prod'

        self._server = self.open_ssh()
        self._psql_db = pw.PostgresqlDatabase(self.lk3_db_name, host=self.lk3_host, port=self._server.local_bind_port,
                                              user=self.lk3_login, password=self.lk3_password)


class GetDataArbat(AresconData):
    def __init__(self, start_date: str, end_date: str):
        super().__init__(start_date, end_date, 'arbat')
        self._db_password = '3iPAasaeeMN9zJoYr'
        self._db_url = '185.148.37.101'


def get_agent(start_date, end_date, name_agent: str):
    if name_agent == 'private':
        obj = GetDataPrivate(start_date, end_date)
    elif name_agent == 'kvart23':
        obj = GetDataKvart23(start_date, end_date)
    elif name_agent == 'kvart126':
        obj = GetDataKvart126(start_date, end_date)
    elif name_agent == 'arbat':
        obj = GetDataArbat(start_date, end_date)
    else:
        print("Ошибка в имени объекта сбора данных")
        obj = None
        exit(-10)

    return obj
