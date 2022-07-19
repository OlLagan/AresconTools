from peewee import *
from datetime import datetime
import pandas as pd

dcs_database_proxy = DatabaseProxy()

database = MySQLDatabase('processing', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True,
                                          'host': '94.228.246.228', 'port': 63306, 'user': 'processing',
                                          'password': 'JXJuGFVgK7bVXkf9W'})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = dcs_database_proxy


class Person(BaseModel):
    birthday = DateField(null=True)
    contact = TextField(null=True)
    deadday = DateField(null=True)
    fname = CharField(null=True)
    name = CharField(null=True)
    phone = BigIntegerField(index=True, null=True)
    sname = CharField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'person'


class PlacesTypes(BaseModel):
    name = CharField()

    class Meta:
        table_name = 'places_types'


class Places(BaseModel):
    location_id = IntegerField(column_name='LOCATION_ID', null=True)
    id_partner = IntegerField(constraints=[SQL("DEFAULT -1")], index=True, null=True)
    id_places_type = ForeignKeyField(column_name='id_places_type',
                                     constraints=[SQL("DEFAULT 1")], field='id', model=PlacesTypes)
    name = CharField(null=True)
    params = TextField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'places'


class Account(BaseModel):
    user_id = IntegerField(column_name='USER_ID', null=True)
    id_partner = IntegerField(constraints=[SQL("DEFAULT -1")], index=True, null=True)
    id_person = ForeignKeyField(column_name='id_person', field='id', model=Person, null=True)
    id_place = ForeignKeyField(column_name='id_place', field='id', model=Places, null=True)
    settings = TextField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'account'


class CurrencyRates(BaseModel):
    caption = CharField(null=True)
    icon = CharField(null=True)
    id_currency = IntegerField(unique=True)
    rate = FloatField()

    class Meta:
        table_name = 'currency_rates'


class Bills(BaseModel):
    amount = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    bill_type = CharField(constraints=[SQL("DEFAULT ''")])
    comment = TextField(null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    format = IntegerField(constraints=[SQL("DEFAULT 0")])
    host = CharField(constraints=[SQL("DEFAULT ''")])
    id_currency = ForeignKeyField(column_name='id_currency', constraints=[SQL("DEFAULT 643")], field='id_currency',
                                  model=CurrencyRates)
    id_host = IntegerField(null=True)
    id_partner = IntegerField(constraints=[SQL("DEFAULT 0")])
    limit = FloatField(constraints=[SQL("DEFAULT 0.0000")], null=True)
    limit_type = IntegerField(constraints=[SQL("DEFAULT 0")])
    name = CharField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'bills'
        indexes = (
            (('host', 'id_host', 'bill_type', 'format'), False),
        )


class Libs(BaseModel):
    description = TextField(null=True)
    path = TextField()
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])
    type = CharField(null=True)

    class Meta:
        table_name = 'libs'


class PartnersTypes(BaseModel):
    role_id = IntegerField(column_name='ROLE_ID', constraints=[SQL("DEFAULT 0")])
    description = TextField(null=True)
    name = CharField(null=True)

    class Meta:
        table_name = 'partners_types'


class Partners(BaseModel):
    comment = TextField(null=True)
    date_created = DateTimeField(null=True)
    id_partner_type = ForeignKeyField(column_name='id_partner_type', constraints=[SQL("DEFAULT 0")], field='id',
                                      model=PartnersTypes)
    id_root = IntegerField(index=True, null=True)
    info = TextField(null=True)
    name = CharField(constraints=[SQL("DEFAULT ''")])
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'partners'


class Gates(BaseModel):
    id_bill = ForeignKeyField(column_name='id_bill', constraints=[SQL("DEFAULT 0")], field='id', model=Bills)
    id_errorgate = IntegerField(null=True)
    id_lib = ForeignKeyField(column_name='id_lib', constraints=[SQL("DEFAULT 0")], field='id', model=Libs)
    id_nextgate = IntegerField(null=True)
    id_partner = ForeignKeyField(column_name='id_partner', constraints=[SQL("DEFAULT 0")], field='id', model=Partners)
    id_terminal = IntegerField(null=True)
    name = CharField(constraints=[SQL("DEFAULT ''")])
    params = TextField(null=True)
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'gates'


class AccountCards(BaseModel):
    caption = CharField()
    id_account = ForeignKeyField(column_name='id_account', field='id', model=Account)
    id_gate = ForeignKeyField(column_name='id_gate', field='id', model=Gates)
    number = BigIntegerField(index=True)
    params = TextField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")], null=True)
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'account_cards'


class AccountCheckout(BaseModel):
    amount = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    caption = CharField(null=True)
    id_account = ForeignKeyField(column_name='id_account', field='id', model=Account)
    params = TextField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")], null=True)
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'account_checkout'


class Cores(BaseModel):
    core_type = CharField(column_name='CoreType', constraints=[SQL("DEFAULT 'CyberCore'")])
    description = TextField(column_name='Description', null=True)
    display_name = CharField(column_name='DisplayName')
    public = IntegerField(column_name='Public', constraints=[SQL("DEFAULT 0")])
    service_name = CharField(column_name='ServiceName', unique=True)
    version = CharField(column_name='Version', null=True)
    database = TextField(null=True)
    ident = CharField(unique=True)
    logs = TextField(null=True)
    options = TextField(null=True)
    pid = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'cores'


class Actions(BaseModel):
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_host = IntegerField(index=True, null=True)
    id_lib = ForeignKeyField(column_name='id_lib', field='id', model=Libs)
    id_partner = ForeignKeyField(column_name='id_partner', constraints=[SQL("DEFAULT 0")], field='id', model=Partners)
    maxsteps = IntegerField(constraints=[SQL("DEFAULT 0")])
    maxthreadcount = IntegerField(constraints=[SQL("DEFAULT 0")])
    name = CharField(null=True)
    params = TextField()
    runline = TextField()
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT -1")])
    timeout = IntegerField(constraints=[SQL("DEFAULT 120")])
    type = CharField(constraints=[SQL("DEFAULT 'shell'")])
    workflow = CharField(constraints=[SQL("DEFAULT 'accept'")], index=True, null=True)

    class Meta:
        table_name = 'actions'


class ActionsEvents(BaseModel):
    d = IntegerField(constraints=[SQL("DEFAULT 1")])
    h = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_action = ForeignKeyField(column_name='id_action', field='id', model=Actions)
    id_next = IntegerField(null=True)
    id_onerror = IntegerField(null=True)
    last = DateTimeField(null=True)
    m = IntegerField(constraints=[SQL("DEFAULT 0")])
    n = IntegerField(constraints=[SQL("DEFAULT 0")])
    s = IntegerField(constraints=[SQL("DEFAULT 0")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])
    w = IntegerField(constraints=[SQL("DEFAULT 0")])
    y = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'actions_events'
        indexes = (
            (('id_action', 'state'), False),
        )


class ActionsArchive(BaseModel):
    comment = TextField(null=True)
    data = TextField(null=True)
    error = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_action = ForeignKeyField(column_name='id_action', field='id', model=Actions)
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_event = ForeignKeyField(column_name='id_event', field='id', model=ActionsEvents)
    iteration = IntegerField(constraints=[SQL("DEFAULT 0")])
    last = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    maxsteps = IntegerField(constraints=[SQL("DEFAULT 0")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])
    workflow = CharField(null=True)

    class Meta:
        table_name = 'actions_archive'
        indexes = (
            (('id_core', 'state'), False),
        )


class ActionsLogs(BaseModel):
    comment = TextField(null=True)
    id_action_archive = ForeignKeyField(column_name='id_action_archive', field='id', model=ActionsArchive)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    workflow = CharField(null=True)

    class Meta:
        table_name = 'actions_logs'


class ActionsThreads(BaseModel):
    comment = TextField(null=True)
    data = TextField(null=True)
    error = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_action = ForeignKeyField(column_name='id_action', field='id', model=Actions)
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_event = ForeignKeyField(column_name='id_event', field='id', model=ActionsEvents)
    iteration = IntegerField(constraints=[SQL("DEFAULT 0")])
    last = DateTimeField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00'")])
    maxsteps = IntegerField(constraints=[SQL("DEFAULT 0")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    workflow = CharField(null=True)

    class Meta:
        table_name = 'actions_threads'
        indexes = (
            (('id_core', 'state'), False),
        )


class GateInits(BaseModel):
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_gate = ForeignKeyField(column_name='id_gate', field='id', model=Gates)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'gate_inits'
        indexes = (
            (('id_gate', 'id_core'), True),
        )


class Providers(BaseModel):
    comment = CharField(null=True)
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_gate = ForeignKeyField(column_name='id_gate', field='id', model=Gates)
    ident = CharField(constraints=[SQL("DEFAULT ''")])
    maxvalue = FloatField(constraints=[SQL("DEFAULT 30000.00")])
    minvalue = FloatField(constraints=[SQL("DEFAULT 0.00")])
    name = CharField(constraints=[SQL("DEFAULT ''")])
    settings = TextField(null=True)
    state = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'providers'
        indexes = (
            (('id_core', 'ident'), False),
        )


class GatesOnProviders(BaseModel):
    id_gate = ForeignKeyField(column_name='id_gate', field='id', model=Gates)
    id_partner = IntegerField(index=True, null=True)
    id_provider = ForeignKeyField(column_name='id_provider', field='id', model=Providers)

    class Meta:
        table_name = 'gates_on_providers'


class LibHandles(BaseModel):
    handle = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_lib = ForeignKeyField(column_name='id_lib', field='id', model=Libs)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'lib_handles'
        indexes = (
            (('id_lib', 'id_core'), True),
        )


class PartnersAccounts(BaseModel):
    comment = CharField(null=True)
    ext_id = IntegerField(index=True)
    id_connected = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)
    id_host = ForeignKeyField(column_name='id_host', constraints=[SQL("DEFAULT 1")], field='id', model=Partners)
    id_partner = ForeignKeyField(backref='partners_id_partner_set', column_name='id_partner',
                                 constraints=[SQL("DEFAULT 1")], field='id', model=Partners)
    info = TextField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])

    class Meta:
        table_name = 'partners_accounts'


class RewardsTarifs(BaseModel):
    description = TextField(null=True)
    name = CharField()

    class Meta:
        table_name = 'rewards_tarifs'


class PartnersAccountsRules(BaseModel):
    enduse = DateTimeField(null=True)
    id_partners_account = ForeignKeyField(column_name='id_partners_account', field='id', model=PartnersAccounts)
    id_places_group = IntegerField(null=True)
    id_rewards_tarif = ForeignKeyField(column_name='id_rewards_tarif', field='id', model=RewardsTarifs)
    id_terminals_group = IntegerField(null=True)
    name = CharField(null=True)
    startuse = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'partners_accounts_rules'


class TerminalsModels(BaseModel):
    channelnum = IntegerField(constraints=[SQL("DEFAULT 1")])
    datastruct = TextField(null=True)
    ident = CharField(constraints=[SQL("DEFAULT ''")], null=True)
    name = CharField()
    portnum = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'terminals_models'


class TerminalsTypes(BaseModel):
    title = CharField()
    transit = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'terminals_types'


class Terminals(BaseModel):
    id = PrimaryKeyField()
    capacity = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    created = DateTimeField()
    ext_id = CharField()
    id_bill = ForeignKeyField(column_name='id_bill', field='id', model=Bills)
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_partner = ForeignKeyField(column_name='id_partner', constraints=[SQL("DEFAULT 0")], field='id', model=Partners)
    id_place = ForeignKeyField(column_name='id_place', field='id', model=Places)
    id_root = IntegerField(null=True)
    id_terminals_model = ForeignKeyField(column_name='id_terminals_model', constraints=[SQL("DEFAULT 1")], field='id',
                                         model=TerminalsModels)
    id_terminals_type = ForeignKeyField(column_name='id_terminals_type', constraints=[SQL("DEFAULT 1")], field='id',
                                        model=TerminalsTypes)
    lastconnect = DateTimeField(null=True)
    lastdata = DateTimeField(null=True)
    name = CharField()
    port = IntegerField(null=True)
    rssi = IntegerField(constraints=[SQL("DEFAULT -999")], null=True)
    security = TextField(null=True)
    serial = IntegerField(null=True)
    settings = TextField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'terminals'
        indexes = (
            (('id_core', 'ext_id'), True),
        )


class Payments(BaseModel):
    account = CharField(null=True)
    addinfo = TextField(null=True)
    amount = FloatField(constraints=[SQL("DEFAULT 0.00")])
    amount_all = FloatField(constraints=[SQL("DEFAULT 0.00")])
    authcode = CharField(null=True)
    comment = CharField(index=True, null=True)
    date_done = DateTimeField(null=True)
    date_init = DateTimeField()
    date_provider = DateTimeField(null=True)
    date_terminal = DateTimeField(null=True)
    errmsg = CharField(null=True)
    error = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_gate = ForeignKeyField(column_name='id_gate', constraints=[SQL("DEFAULT 0")], field='id', model=Gates)
    id_place = ForeignKeyField(column_name='id_place', constraints=[SQL("DEFAULT 0")], field='id', model=Places)
    id_provider = ForeignKeyField(column_name='id_provider', constraints=[SQL("DEFAULT 0")], field='id',
                                  model=Providers)
    id_root = IntegerField(index=True, null=True)
    id_root_terminal = ForeignKeyField(column_name='id_root_terminal', constraints=[SQL("DEFAULT 0")], field='id',
                                       model=Terminals)
    id_terminal = ForeignKeyField(backref='terminals_id_terminal_set', column_name='id_terminal',
                                  constraints=[SQL("DEFAULT 0")], field='id', model=Terminals)
    id_transaction = IntegerField(null=True)
    number = CharField(constraints=[SQL("DEFAULT ''")])
    other = TextField(null=True)
    result = IntegerField(constraints=[SQL("DEFAULT 0")])
    session = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    transid = CharField(constraints=[SQL("DEFAULT ''")], index=True)

    class Meta:
        table_name = 'payments'
        indexes = (
            (('id_gate', 'account', 'result', 'date_done'), False),
            (('id_gate', 'date_done', 'result'), False),
            (('id_provider', 'transid'), True),
            (('id_terminal', 'session'), True),
        )


class PaymentsErrors(BaseModel):
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_error = IntegerField()
    title = CharField(null=True)

    class Meta:
        table_name = 'payments_errors'
        indexes = (
            (('id_error', 'id_core'), True),
        )


class PaymentsHistory(BaseModel):
    date = DateTimeField()
    error = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_payment = ForeignKeyField(column_name='id_payment', field='id', model=Payments)
    ip = CharField(null=True)
    logfile = CharField()
    ptype = CharField()
    result = IntegerField(constraints=[SQL("DEFAULT 0")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'payments_history'


class PaymentsTemp(BaseModel):
    account = CharField(null=True)
    addinfo = TextField(null=True)
    amount = FloatField(constraints=[SQL("DEFAULT 0.00")])
    amount_all = FloatField(constraints=[SQL("DEFAULT 0.00")])
    authcode = CharField(null=True)
    comment = CharField(index=True, null=True)
    date_done = DateTimeField(null=True)
    date_init = DateTimeField()
    date_provider = DateTimeField(null=True)
    date_terminal = DateTimeField(null=True)
    errmsg = CharField(null=True)
    error = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_gate = ForeignKeyField(column_name='id_gate', constraints=[SQL("DEFAULT 0")], field='id', model=Gates)
    id_place = ForeignKeyField(column_name='id_place', constraints=[SQL("DEFAULT 0")], field='id', model=Places)
    id_provider = ForeignKeyField(column_name='id_provider', constraints=[SQL("DEFAULT 0")], field='id',
                                  model=Providers)
    id_root = IntegerField(index=True, null=True)
    id_root_terminal = ForeignKeyField(column_name='id_root_terminal', constraints=[SQL("DEFAULT 0")], field='id',
                                       model=Terminals)
    id_terminal = ForeignKeyField(backref='terminals_id_terminal_set', column_name='id_terminal',
                                  constraints=[SQL("DEFAULT 0")], field='id', model=Terminals)
    id_transaction = IntegerField(null=True)
    number = CharField(constraints=[SQL("DEFAULT ''")])
    other = TextField(null=True)
    result = IntegerField(constraints=[SQL("DEFAULT 0")])
    session = CharField(constraints=[SQL("DEFAULT ''")], index=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    transid = CharField(constraints=[SQL("DEFAULT ''")], index=True)

    class Meta:
        table_name = 'payments_temp'
        indexes = (
            (('id_provider', 'transid'), True),
            (('id_terminal', 'session'), True),
        )


class PaymentsHistoryTemp(BaseModel):
    date = DateTimeField()
    error = IntegerField(constraints=[SQL("DEFAULT 0")])
    id_payment = ForeignKeyField(column_name='id_payment', field='id', model=PaymentsTemp)
    ip = CharField(null=True)
    logfile = CharField()
    ptype = CharField()
    result = IntegerField(constraints=[SQL("DEFAULT 0")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'payments_history_temp'


class PaymentsResults(BaseModel):
    id_result = IntegerField(index=True)
    title = CharField()

    class Meta:
        table_name = 'payments_results'


class PaymentsStates(BaseModel):
    id_state = IntegerField(index=True)
    title = CharField()

    class Meta:
        table_name = 'payments_states'


class PlacesGroups(BaseModel):
    id_partner = ForeignKeyField(column_name='id_partner', field='id', model=Partners)
    name = CharField(null=True)

    class Meta:
        table_name = 'places_groups'


class PlacesOnGroups(BaseModel):
    id_place = ForeignKeyField(column_name='id_place', field='id', model=Places)
    id_places_group = ForeignKeyField(column_name='id_places_group', field='id', model=PlacesGroups)

    class Meta:
        table_name = 'places_on_groups'


class RewardsGatesRules(BaseModel):
    down = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    fix = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    id_gate = ForeignKeyField(column_name='id_gate', field='id', model=Gates)
    id_rewards_tarif = ForeignKeyField(column_name='id_rewards_tarif', field='id', model=RewardsTarifs)
    max = FloatField(constraints=[SQL("DEFAULT 30000.0000")])
    min = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])
    up = FloatField(constraints=[SQL("DEFAULT 0.0000")])

    class Meta:
        table_name = 'rewards_gates_rules'
        indexes = (
            (('id_rewards_tarif', 'id_gate'), True),
        )


class SchemaMigrations(BaseModel):
    inserted_at = DateTimeField(null=True)
    version = BigAutoField()

    class Meta:
        table_name = 'schema_migrations'


class SmsProviders(BaseModel):
    id_partner = ForeignKeyField(column_name='id_partner', constraints=[SQL("DEFAULT 0")], field='id', model=Partners)
    settings = TextField(null=True)
    state = IntegerField(constraints=[SQL("DEFAULT 1")])
    timeout = IntegerField(constraints=[SQL("DEFAULT 120")])

    class Meta:
        table_name = 'sms_providers'


class Sms(BaseModel):
    created = DateTimeField(null=True)
    id_lc = IntegerField(column_name='id_LC', null=True)
    id_sms_provider = ForeignKeyField(column_name='id_sms_provider', field='id', model=SmsProviders)
    iteration = IntegerField(constraints=[SQL("DEFAULT 0")])
    mes_id = CharField(null=True)
    phone = CharField()
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    text = TextField(null=True)

    class Meta:
        table_name = 'sms'


class SmsTemp(BaseModel):
    created = DateTimeField(null=True)
    id_lc = IntegerField(column_name='id_LC', null=True)
    id_sms_provider = ForeignKeyField(column_name='id_sms_provider', field='id', model=SmsProviders)
    iteration = IntegerField(constraints=[SQL("DEFAULT 0")])
    mes_id = CharField(null=True)
    phone = CharField()
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    text = TextField(null=True)

    class Meta:
        table_name = 'sms_temp'


class TerminalsData(BaseModel):
    channel = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    counter = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    date_server = DateTimeField(index=True)
    date_terminal = DateTimeField(index=True)
    id_gate = ForeignKeyField(column_name='id_gate', field='id', model=Gates)
    id_place = ForeignKeyField(column_name='id_place', field='id', model=Places)
    id_provider = ForeignKeyField(column_name='id_provider', field='id', model=Providers)
    id_terminal = ForeignKeyField(column_name='id_terminal', field='id', model=Terminals)
    info = TextField(null=True)
    rowdata = TextField(null=True)
    rssi = IntegerField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])
    value = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    weight = FloatField(constraints=[SQL("DEFAULT 0.0000")])

    class Meta:
        table_name = 'terminals_data'

    @staticmethod
    def get_by_dates_port(start_date: datetime, end_date: datetime, port: int = 1) -> pd.DataFrame:
        try:
            data_set = TerminalsData.\
                select(TerminalsData.id, TerminalsData.id_terminal, TerminalsData.stamp,
                       TerminalsData.date_server, TerminalsData.date_terminal).\
                where(TerminalsData.stamp.between(start_date, end_date) & (TerminalsData.value == 1)).\
                order_by(TerminalsData.stamp.desc()).limit(1000)
            df_term = pd.DataFrame(list(data_set.dicts()))
        except Exception as e:
            df_term = None
        return df_term

class TerminalsGroups(BaseModel):
    id_partner = ForeignKeyField(column_name='id_partner', field='id', model=Partners)
    name = CharField(null=True)

    class Meta:
        table_name = 'terminals_groups'


class TerminalsLogs(BaseModel):
    id_place = ForeignKeyField(column_name='id_place', field='id', model=Places)
    id_terminal = ForeignKeyField(column_name='id_terminal', field='id', model=Terminals)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT -1")], null=True)

    class Meta:
        table_name = 'terminals_logs'


class TerminalsMonitoring(BaseModel):
    dt = DateTimeField(null=True)
    id_terminal = IntegerField(null=True)
    info = TextField(null=True)
    ip = CharField(null=True)
    mac = CharField(null=True)
    rssi = IntegerField(null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'terminals_monitoring'


class TerminalsOnGroups(BaseModel):
    id_terminal = ForeignKeyField(column_name='id_terminal', field='id', model=Terminals)
    id_terminals_group = ForeignKeyField(column_name='id_terminals_group', field='id', model=TerminalsGroups)

    class Meta:
        table_name = 'terminals_on_groups'


class TerminalsRequests(BaseModel):
    body = TextField(null=True)
    command = CharField(null=True)
    comment = CharField(null=True)
    id_core = ForeignKeyField(column_name='id_core', field='id', model=Cores)
    id_gate = IntegerField(index=True, null=True)
    id_terminal = IntegerField(index=True, null=True)
    mask = CharField(constraints=[SQL("DEFAULT '0000-00-00 00:00:00.000'")], null=True)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")])
    when = DateTimeField(null=True)

    class Meta:
        table_name = 'terminals_requests'


class TransactionsTypes(BaseModel):
    caption = CharField(null=True)
    description = TextField(null=True)
    params = TextField(null=True)

    class Meta:
        table_name = 'transactions_types'


class Transactions(BaseModel):
    comment = CharField(null=True)
    date_cancel = DateTimeField(null=True)
    date_fin = DateTimeField(null=True)
    date_init = DateTimeField(null=True)
    ext_id = BigIntegerField(index=True, null=True)
    id_transactions_type = ForeignKeyField(column_name='id_transactions_type', field='id', model=TransactionsTypes)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'transactions'


class TransactionsTemp(BaseModel):
    comment = CharField(null=True)
    date_cancel = DateTimeField(null=True)
    date_fin = DateTimeField(null=True)
    date_init = DateTimeField(null=True)
    ext_id = BigIntegerField(index=True, null=True)
    id_transactions_type = ForeignKeyField(column_name='id_transactions_type', field='id', model=TransactionsTypes)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'transactions_temp'


class TransactionsTransfers(BaseModel):
    amount = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    id_bill = ForeignKeyField(column_name='id_bill', field='id', model=Bills)
    id_transaction = ForeignKeyField(column_name='id_transaction', field='id', model=Transactions)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'transactions_transfers'


class TransactionsTransfersTemp(BaseModel):
    amount = FloatField(constraints=[SQL("DEFAULT 0.0000")])
    id_bill = ForeignKeyField(column_name='id_bill', field='id', model=Bills)
    id_transaction = ForeignKeyField(column_name='id_transaction', field='id', model=TransactionsTemp)
    stamp = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    state = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'transactions_transfers_temp'

