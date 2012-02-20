import functools
import itertools

import MySQLdb
import MySQLdb.cursors

import core.easydict

CHATTY = 0

def index(idcol):
    def indexed_dec(f):
        @functools.wraps(f)
        def indexed_func(self, *args):
            return self.provider.Indexed(idcol, f(self, *args))
        return indexed_func
    return indexed_dec

def set_col(rowfunc):
    def set_col_dec(f):
        @functools.wraps(f)
        def set_col_func(self, *args):
            result = f(self, *args)
            for row in result:
                key, value = rowfunc(row)
                row[key] = value
            return result
        return set_col_func
    return set_col_dec

def short_url(idcol, urlformat):
    return set_col(lambda row: ('ShortURL', urlformat % row[idcol]))

def long_url(namecol, urlformat):
    return set_col(lambda row: ('LongURL', urlformat % row[namecol].replace(' ','_')))

def first(f):
    def getFirstDec(self, *args):
        return f(self, *args)[0]
    return getFirstDec

def group_by(colname):
    def group_by_dec(f):
        @functools.wraps(f)
        def group_by_func(self, *args):
            result = f(self, *args)
            return [ (key, list(group))
                     for (key, group)
                     in itertools.groupby(result, lambda row: row[colname]) ]
        return group_by_func
    return group_by_dec

def open_query(f):
    @functools.wraps(f)
    def open_query_func(self, *args):
        sql, params = f(self, *args)
        return self.provider.Open(sql, *params)
    return open_query_func

def open_query_one_row(f):
    @functools.wraps(f)
    def open_query_one_row_func(self, *args):
        sql, params = f(self, *args)
        return self.provider.Open(sql, *params)[0]
    return open_query_one_row_func

def open_query_one_value(f):
    @functools.wraps(f)
    def open_query_one_value_func(self, *args):
        sql, params = f(self, *args)
        return self.provider.Open(sql, *params)[0].values()[0]
    return open_query_one_value_func

def exec_query(f):
    @functools.wraps(f)
    def exec_query_func(self, *args):
        sql, params = f(self, *args)
        return self.provider.Execute(sql, *params)
    return exec_query_func

class Provider(object):
    def Indexed(self, idcol, table):
        return dict((row[idcol], row) for row in table)

class MySQLProvider(Provider):
    def __init__(self):
        self.db = MySQLdb.connect(
            host=core.ini.db.hostname,
            user=core.ini.db.username,
            passwd=core.ini.db.password,
            db=core.ini.db.database,
            use_unicode=True,
            charset='utf8')

    def Open(self, sql, *args):
        if CHATTY:
            print sql
            print args
        c = self.db.cursor(MySQLdb.cursors.DictCursor)
        c.execute(sql, args)
        result = c.fetchall()
        c.close()
        return map(core.easydict.EasyDict, result)

    def Execute(self, sql, *args):
        if CHATTY:
            print sql
            print args
        c = self.db.cursor()
        c.execute(sql, args)
        result = c.rowcount, c.lastrowid
        c.connection.commit()
        c.close()
        return result

class Model(object):
    def __init__(self, provider=MySQLProvider):
        if isinstance(provider, type):
            self.provider = provider()
        else:
            self.provider = provider
