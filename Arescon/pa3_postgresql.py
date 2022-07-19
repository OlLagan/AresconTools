from datetime import datetime, timedelta
from peewee import *
import pandas as pd

pa3_database_proxy = DatabaseProxy()


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = pa3_database_proxy


class Tszhs(BaseModel):
    address = CharField(null=True)
    bank = CharField(null=True)
    bik = CharField(null=True)
    email = CharField(null=True)
    id = BigAutoField()
    inn = CharField(null=True)
    inserted_at = DateTimeField()
    kpp = CharField(null=True)
    ksch = CharField(null=True)
    name = CharField(null=True)
    phone = CharField(null=True)
    phone_disp = CharField(null=True)
    rsch = CharField(null=True)
    ssd_code = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'tszhs'

class Houses(BaseModel):
    area = CharField(null=True)
    build = CharField(null=True)
    city = CharField(null=True)
    house = CharField(null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    place = CharField(null=True)
    postalcode = CharField(null=True)
    region = CharField(null=True)
    street = CharField(null=True)
    struc = CharField(null=True)
    tszh = ForeignKeyField(column_name='tszh_id', field='id', model=Tszhs, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'houses'

class Users(BaseModel):
    checkword = CharField(null=True)
    checkword_time = DateTimeField(null=True)
    confirm_code = CharField(null=True)
    email = CharField(null=True, unique=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    name = CharField(null=True)
    password_hash = CharField(null=True)
    phone = CharField(null=True)
    type = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'users'

class Accounts(BaseModel):
    area = DoubleField(null=True)
    area_living = DoubleField(null=True)
    flat = IntegerField(null=True)
    flat_type = CharField(null=True)
    house = ForeignKeyField(column_name='house_id', field='id', model=Houses, null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    name = CharField(null=True)
    people = IntegerField(null=True)
    people_registered = IntegerField(null=True)
    tszh = ForeignKeyField(column_name='tszh_id', field='id', model=Tszhs, null=True)
    updated_at = DateTimeField()
    user = ForeignKeyField(column_name='user_id', field='id', model=Users, null=True)

    class Meta:
        table_name = 'accounts'

class MeterTypes(BaseModel):
    code = CharField(null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    name = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'meter_types'

class MeterModels(BaseModel):
    calibration = BooleanField(constraints=[SQL("DEFAULT false")])
    id = BigAutoField()
    inserted_at = DateTimeField()
    measure_name = CharField(null=True)
    measure_weight = DoubleField(constraints=[SQL("DEFAULT 1.0")], null=True)
    meter_type = ForeignKeyField(column_name='meter_type_id', field='id', model=MeterTypes, null=True)
    name = CharField(null=True)
    updated_at = DateTimeField()
    value_round = IntegerField(null=True)
    weight = DoubleField(null=True)

    class Meta:
        table_name = 'meter_models'

class ServiceTypes(BaseModel):
    code = CharField(null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    name = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'service_types'

class Meters(BaseModel):
    id = BigAutoField()
    active = BooleanField(constraints=[SQL("DEFAULT true")])
    date_connect = DateTimeField(null=True)
    date_connect_first = DateTimeField(null=True)
    house = ForeignKeyField(column_name='house_id', field='id', model=Houses, null=True)
    house_meter = BooleanField(constraints=[SQL("DEFAULT false")])
    inserted_at = DateTimeField()
    meter_model = ForeignKeyField(column_name='meter_model_id', field='id', model=MeterModels, null=True, )
    name = CharField(null=True)
    num = CharField(null=True)
    service_type = ForeignKeyField(column_name='service_type_id', field='id', model=ServiceTypes, null=True)
    terminal_id = IntegerField(index=True, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'meters'

    @staticmethod
    def get_all_to_df(service_type: int = 6) -> pd.DataFrame:
        try:
            data_set = Meters.select(Meters.id.alias('meter'), Meters.name, Meters.num, Meters.terminal_id, MetersAccounts.account,
                                     Accounts.tszh,
                                     Accounts.house, Houses.build, Accounts.flat). \
                join(MetersAccounts).join(Accounts).join(Houses). \
                where(Meters.service_type == service_type)
            df_meters = pd.DataFrame(list(data_set.dicts()))
        except Exception as e:
            print(e)
            df_meters = None
        return df_meters

    @staticmethod
    def get_meters() -> pd.DataFrame:
        df_cold_water = Meters.get_all_to_df(service_type=1)
        df_hot_water = Meters.get_all_to_df(service_type=2)
        return pd.concat([df_cold_water, df_hot_water], axis=0)

class AlertTypes(BaseModel):
    code = CharField(null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    name = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'alert_types'


class AlertHistory(BaseModel):
    account = ForeignKeyField(column_name='account_id', field='id', model=Accounts, null=True)
    alert_type = ForeignKeyField(column_name='alert_type_id', field='id', model=AlertTypes, null=True)
    dispatcher = BooleanField(constraints=[SQL("DEFAULT false")])
    house = ForeignKeyField(column_name='house_id', field='id', model=Houses, null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    log_data = TextField(null=True)
    message = CharField(null=True)
    meter = ForeignKeyField(column_name='meter_id', field='id', model=Meters, null=True)
    terminal_id = IntegerField(index=True, null=True)
    tszh = ForeignKeyField(column_name='tszh_id', field='id', model=Tszhs, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'alert_history'

    @staticmethod
    def get_alerts_by_dtime(period: float = 1., is_dispatched:bool= None, is_dataframe=True):
        end_period = datetime.now()
        start_period = end_period - timedelta(hours=period)

        if is_dispatched is None:
            data_set = AlertHistory.select().where(AlertHistory.inserted_at.between(start_period, end_period))
        else:
            data_set = AlertHistory.select().where(AlertHistory.inserted_at.between(start_period,end_period) &
                                                   (AlertHistory.dispatcher == is_dispatched))
        if is_dataframe:
            data_set = pd.DataFrame(list(data_set.dicts()))
        return data_set

    @staticmethod
    def add_alerts(df: pd.DataFrame):
        if df.empty:
            print('there are not alerts that could be add to the history.')
        else:
#TODO добавить обработку dataframe повторяющихся записей.
# Повторяющиеся те, которые фиксируют повтор срабатываний от одного датчика не более чем через 10 минут
            df.sort_values(by=['inserted_at'], ascending=True, inplace=True)
            df['dispatcher'] = False
            df['message'] = "Сработал Датчик протечки №" + df['name'] + " в " + df['inserted_at'].astype(str)
            df['log_data'] = "Lagan's alarm by telegram. Action: name: " + df['name'] + ", terminal_id: " + \
                             df['terminal_id'].astype(str) + " at " + df['inserted_at'].astype(str)
            df['updated_at'] = datetime.now() + timedelta(minutes=1)
            df['alert_type'] = 11
            df['tszh'] = 2

            df = df[['dispatcher', 'message', 'log_data', 'terminal_id', 'meter', 'account', 'tszh', 'house',
                     'alert_type', 'inserted_at', 'updated_at']]
    #удаление дублей
            alert_history = AlertHistory.get_alerts_by_dtime(period=48)
            if not alert_history.empty:
                df = df[~df.message.isin(alert_history['message'])]

            data = df.to_dict('records')
            AlertHistory.insert_many(data,
                                     fields=[AlertHistory.dispatcher, AlertHistory.message, AlertHistory.log_data,
                                             AlertHistory.terminal_id, AlertHistory.meter, AlertHistory.account,
                                             AlertHistory.tszh, AlertHistory.house, AlertHistory.alert_type,
                                             AlertHistory.inserted_at, AlertHistory.updated_at]).execute()
            print(f'{len(df.index)} alarms added to the history.')

class AlertSettings(BaseModel):
    account = ForeignKeyField(column_name='account_id', field='id', model=Accounts, null=True)
    action = CharField(null=True)
    active = BooleanField(constraints=[SQL("DEFAULT false")])
    alert_type = ForeignKeyField(column_name='alert_type_id', field='id', model=AlertTypes, null=True)
    dispatcher = BooleanField(constraints=[SQL("DEFAULT false")])
    house = ForeignKeyField(column_name='house_id', field='id', model=Houses, null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    limit = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    period = CharField(null=True)
    tszh = ForeignKeyField(column_name='tszh_id', field='id', model=Tszhs, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'alert_settings'

class MeterCalibration(BaseModel):
    calibration_date = DateTimeField(null=True)
    calibration_date_end = DateTimeField(null=True)
    data_structure = TextField(null=True)
    delta = DoubleField(null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    meter = ForeignKeyField(column_name='meter_id', field='id', model=Meters, null=True)
    midified_by_owner = BooleanField(constraints=[SQL("DEFAULT false")])
    modified_by = ForeignKeyField(column_name='modified_by', field='id', model=Users, null=True)
    terminal1 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    terminal2 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    terminal3 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    terminal4 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    updated_at = DateTimeField()
    value1 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    value2 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    value3 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    value4 = DoubleField(constraints=[SQL("DEFAULT 0.0")], null=True)
    values = TextField(null=True)
    weight = DoubleField(null=True)

    class Meta:
        table_name = 'meter_calibration'

class MeterModelsServices(BaseModel):
    inserted_at = DateTimeField()
    meter_model = ForeignKeyField(column_name='meter_model_id', field='id', model=MeterModels, null=True)
    service_type = ForeignKeyField(column_name='service_type_id', field='id', model=ServiceTypes, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'meter_models_services'
        indexes = (
            (('meter_model', 'service_type'), False),
        )
        primary_key = False

class MetersAccounts(BaseModel):
    account = ForeignKeyField(column_name='account_id', field='id', model=Accounts, null=True)
    inserted_at = DateTimeField()
    meter = ForeignKeyField(column_name='meter_id', field='id', model=Meters, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'meters_accounts'
        indexes = (
            (('meter', 'account'), False),
        )
        primary_key = False

class Posts(BaseModel):
    accounts_users = ForeignKeyField(column_name='accounts_users_id', field='id', model=Users, null=True)
    body = TextField(null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    title = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'posts'

class Roles(BaseModel):
    r = BooleanField(column_name='R', null=True)
    w = BooleanField(column_name='W', null=True)
    entity_id = IntegerField(null=True)
    entity_type = CharField(null=True)
    id = BigAutoField()
    inserted_at = DateTimeField()
    name = CharField(null=True)
    r = BooleanField(null=True)
    updated_at = DateTimeField()
    w = BooleanField(null=True)

    class Meta:
        table_name = 'roles'

class SchemaMigrations(BaseModel):
    inserted_at = DateTimeField(null=True)
    version = BigAutoField()

    class Meta:
        table_name = 'schema_migrations'

class UserRole(BaseModel):
    inserted_at = DateTimeField()
    role = ForeignKeyField(column_name='role_id', field='id', model=Roles, null=True)
    updated_at = DateTimeField()
    user = ForeignKeyField(column_name='user_id', field='id', model=Users, null=True)

    class Meta:
        table_name = 'user_role'
        indexes = (
            (('user', 'role'), False),
        )
        primary_key = False
