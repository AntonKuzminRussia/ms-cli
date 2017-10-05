# -*- coding: utf-8 -*-
"""
This is part of MailSnoopy software
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Api for work with DB
"""
import time
import pprint
import mysql.connector

class Database(object):
    """ Api for work with DB """

    _db = None
    _restart_by_deadlock_limit = 5
    _sleep_by_deadlock_restart = 3
    _host = None
    _user = None
    _password = None
    _basename = None

    def __init__(self, host, user, password, basename):
        self._host = host
        self._user = user
        self._password = password
        self._basename = basename

        self.connect()

    def clone(self):
        return Database(self._host, self._user, self._password, self._basename)

    def connect(self):
        self._db = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            database=self._basename,
            #raise_on_warnings=True,
        )
        self._db.autocommit = True

    def q(self, sql, return_curs=False):
        """ Usual query, return cursor """
#        pprint.pprint("START " + sql[0:100])
        for i in range(1, self._restart_by_deadlock_limit + 1):
            try:
                curs = self._db.cursor(buffered=True)
                curs.execute(sql)
            except mysql.connector.errors.ProgrammingError as ex:
                raise Exception("SQLERR:" + sql)
            except mysql.connector.errors.OperationalError as ex:
                if "MySQL Connection not available" in str(ex):
                    self.connect()
                    return self.q(sql, return_curs)
                else:
                    raise ex
            except mysql.connector.errors.DatabaseError as e:
                if str(e).count("Lock wait timeout exceeded") or str(e).count("Deadlock found when trying to get lock"):
                    if i == self._restart_by_deadlock_limit:
                        curs = self._db.cursor()
                        curs.execute(sql)
                    else:
                        time.sleep(self._sleep_by_deadlock_restart)
                        continue
                else:
                    raise e
            except mysql.connector.errors.InterfaceError:
                pprint.pprint("Database interface error (MySQL)")
                time.sleep(3)
                self.connect()
                return self.q(sql, return_curs)
            except IndexError:
                pprint.pprint("Database data transfer error (MySQL)")
                time.sleep(3)
                self.connect()
                return self.q(sql, return_curs)
            except BaseException:
                raise Exception("SQLERR:" + sql)
            break
        if return_curs:
            return curs
        else:
            curs.close()

#        pprint.pprint("DONE " + sql[0:100])

    def fetch_all(self, sql):
        """ Fetch result of sql query as assoc dict """
        result = []

        curs = self.q(sql, True)
        cols = curs.column_names
        for row in curs:
            row_result = {}
            for field in cols:
                k = cols.index(field)
                row_result[cols[k]] = row[k]
                #print cols[k], row[k]
            result.append(row_result)
        curs.close()
        return result

    def fetch_row(self, sql):
        """ Fetch result of sql query as one row """
        curs = self.q(sql, True)
        cols = curs.column_names
        row = curs.fetchone()
        if curs._have_unread_result():
            curs.fetchall()
        curs.close()
        if row:
            result = {}
            for field in cols:
                k = cols.index(field)
                result[cols[k]] = row[k]
            return result
        else:
            return None

    def fetch_one(self, sql):
        """ Fetch first value of sql query from first row """
        curs = self.q(sql, True)
        row = curs.fetchone()
        if curs._have_unread_result():
            curs.fetchall()
        curs.close()
        if row:
            return row[0]
        else:
            return None


    def fetch_col(self, sql):
        """ Fetch first column of sql query as list """
        result = []

        curs = self.q(sql, True)
        for row in curs:
            result.append(row[0])
        curs.close()
        return result

    def fetch_pairs(self, sql):
        """ Fetch result of sql query as dict {first_col: second_col} """
        result = {}

        curs = self.q(sql, True)
        for row in curs:
            result[row[0]] = row[1]
        curs.close()
        return result

    def escape(self, _str):
        """ Escape special chars from str """
        return mysql.connector.conversion.MySQLConverter().escape(_str)

    def quote(self, _str):
        """ Escape special chars from str and put it into quotes """
        return "NULL" if _str is None else "'" + self.escape(str(_str)) + "'"

    def close(self):
        """ Close db connection """
        self._db.close()

    def insert(self, table_name, data, ignore=False):
        """
        Insert data into table
        :param table_name: target table
        :param data: dict with data {col_name: value}
        :param ignore: Its INSERT IGNORE request or no?
        :return:
        """
        fields = map((lambda s: "`" + str(s) + "`"), data.keys())
        values = map(self.quote, data.values())
        curs = self.q(
            "INSERT " + ("IGNORE" if ignore else "") + " INTO `{0}` ({1}) VALUES({2})".format(
                table_name, ", ".join(fields),
                ", ".join(values)
            ),
            True)
        last_row_id = curs.lastrowid
        curs.close()
        return last_row_id

    def insert_mass(self, table_name, data, ignore=False):
        """
        Insert data into table with many VALUES sections
        :param table_name: target table
        :param data: list of dicts with data {col_name: value}
        :param ignore: Its INSERT IGNORE request or no?
        :return:
        """
        fields = []
        to_insert = []
        for row in data:
            if fields == []:
                fields = map((lambda s: "`" + str(s) + "`"), row.keys())
            values = map(self.quote, row.values())
            to_insert.append("({0})".format(", ".join(values)))

            if len(to_insert)%50 == 0:
                self.q(
                    "INSERT " + ("IGNORE" if ignore else "") + " INTO `{0}` ({1}) VALUES {2}"
                    .format(table_name, ", ".join(fields), ", ".join(to_insert))
                )
                to_insert = []

        if len(to_insert):
            self.q(
                "INSERT " + ("IGNORE" if ignore else "") + " INTO `{0}` ({1}) VALUES {2}"
                .format(table_name, ", ".join(fields), ", ".join(to_insert))
            )

    def update_mass(self, table_name, field, data):
        """
        Mass update data in table (UPDATE ... CASE)
        :param table_name: Target table
        :param field: Field what will be change
        :param data: Dict with update data in format {case: value}
        :param where: Where condition (example: "id = 3")
        :return:
        """
        sqlTplStart = "UPDATE `{0}` SET `{1}` = CASE \n".format(table_name, field)
        sqlTplEnd = "ELSE `{0}` \n END".format(field)

        sqls = []
        for case in data:
            sqls.append("WHEN {0} THEN {1} \n".format(case, self.quote(data[case])))

            if len(sqls)%50 == 0:
                self.q(sqlTplStart + "".join(sqls) + sqlTplEnd)
                sqls = []

        if len(sqls):
            self.q(sqlTplStart + "".join(sqls) + sqlTplEnd)

    def replace(self, table_name, data):
        """
        Replace data in table
        :param table_name: target table
        :param data: dict with data {col_name: value}
        :param ignore: Its INSERT IGNORE request or no?
        :return:
        """
        fields = map((lambda s: "`" + str(s) + "`"), data.keys())
        values = map(self.quote, data.values())
        curs = self.q("REPLACE INTO `{0}` ({1}) VALUES({2})".format(table_name, ", ".join(fields), ", ".join(values)))
        last_row_id = curs.lastrowid
        curs.close()
        return last_row_id

    def update(self, table_name, data, where):
        """
        Update data in table
        :param table_name: Target table
        :param data: Dict with update data in format {col: value}
        :param where: Where condition (example: "id = 3")
        :return:
        """
        fields = []
        for fname in data:
            fields.append("`{0}` = '{1}'".format(fname, self.escape(data[fname])))

        self.q("UPDATE `{0}` SET {1} WHERE {2}".format(table_name, ", ".join(fields), where))
