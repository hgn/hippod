#!/usr/bin/python3
# coding: utf-8

import os
import sys
import ldap
import pprint
import json
import addict

from hippod.error_object import *


class LDAP:

    def __init__(self, server_addr, server_port, user, password, bind):
        self.server_addr = server_addr
        self.server_port = server_port
        self.user = user
        self.password = password
        self.bind = bind


    def sanitize_result(self, r):
        d = addict.Dict()
        d_sub = addict.Dict()
        keys = (("fullname", "displayNamePrintable"),
                ("email", "mail"),
                ("department", "department"),
                ("telephone", "telephoneNumber"))

        # convert from LDAP structure into Hippod specific one
        for i in keys:
            try:
                tmp = r[0][1][i[1]]
                d_sub[i[0]] = tmp[0].decode('utf-8')
            except:
                d_sub[i[0]] = "unknown"
        # emails should always stored in lower case
        d_sub["email"] = d_sub["email"].lower()
        return d_sub


    def query(self, name):
        try:
            con = ldap.initialize("{}:{}".format(self.server_addr,
                                  self.server_port), bytes_mode=False)
            con.simple_bind_s(self.user, self.password)
            query_filter = "(cn={})".format(name)
            r = con.search_s(self.bind, ldap.SCOPE_SUBTREE, query_filter)
            if not r:
                return False, "No Data from LDAP server"
            return True, self.sanitize_result(r)
        except Exception as e:
            return False, str(e)
        


class UserDB:

    def __init__(self, conf, user_db_path, ldap_db_path):
        self.user_db_path = user_db_path
        self.ldap_db_path = ldap_db_path
        self._init_user_db()
        self._init_ldap_db()
        if conf.userdb.method == "ldap":
            self.ldap_method = True
            self.conf_ldap = conf
            self.server_addr = conf.userdb.ldap_credentials['server']
            self.server_port = conf.userdb.ldap_credentials['port']
            self.username = conf.userdb.ldap_credentials['username']
            self.password = conf.userdb.ldap_credentials['password']
            self.bind = conf.userdb.ldap_credentials['bind']
        elif conf.userdb.method == "file":
            self.ldap_method = False
        else:
            msg = "configuration methdod {} unknown. Only 'ldap' or " \
                  "'file' methods are valid"
            msg = msg.format(conf.userdb.method)
            raise ApiError(msg)


    def _init_user_db(self):
        if  os.path.isfile(self.user_db_path):
            return
        print("initialize new enpty user database in {}".format(self.user_db_path))
        entry = dict()
        entry_sub = dict()
        entry["john_doe"] = entry_sub
        entry_sub['fullname']   = "John Doe"
        entry_sub['email']      = "john@example.coa"
        entry_sub['department'] = "Death Star"
        entry_sub['telephone']  = "00000000"
        #entry['color']    = '#{:02X}'.format(random.randint(0, 0xFFFFFF))
        d_jsonfied =  json.dumps(entry, sort_keys=True,indent=4, separators=(',', ': '))
        with open(self.user_db_path,"w+") as f:
            f.write(d_jsonfied)

    def _init_ldap_db(self):
        if  os.path.isfile(self.ldap_db_path):
            return
        print("initialize new enpty LDAP database in {}".format(self.ldap_db_path))
        entry = dict()
        entry_sub = dict()
        entry["john_doe"] = entry_sub
        entry_sub['fullname']   = "John Doe"
        entry_sub['email']      = "john@example.coa"
        entry_sub['department'] = "Death Star"
        entry_sub['telephone']  = "00000000"
        #entry['color']    = '#{:02X}'.format(random.randint(0, 0xFFFFFF))
        d_jsonfied =  json.dumps(entry, sort_keys=True,indent=4, separators=(',', ': '))
        with open(self.ldap_db_path,"w+") as f:
            f.write(d_jsonfied)


    def _check_file(self):
        assert(os.path.isfile(self.user_db_path))


    def _local_ldap_db_add_entry(self, new_entry, username):
        with open(self.ldap_db_path, 'r') as f:
            db = json.load(f)
        db[username] = new_entry
        db_json = json.dumps(db, sort_keys=True,indent=4, separators=(',', ': '))
        with open(self.ldap_db_path, 'w') as f:
            f.write(db_json)


    def _local_db_query_entry(self, username):
        try:
            with open(self.user_db_path) as db_file:
                db = json.load(db_file)
                if not username in db:
                    return None
                return db[username]
        except ValueError:
            # here use also logger
            return


    def _local_ldap_db_query_entry(self, username):
        try:
            with open(self.ldap_db_path) as db_file:
                db = json.load(db_file)
                if not username in db:
                    return None
                return db[username]
        except ValueError:
            # here use also logger
            return


    def query_user(self, username):
        data_local_db = self._local_db_query_entry(username)
        if not data_local_db and self.ldap_method:
            data_local_ldap = self._local_ldap_db_query_entry(username)
            if not data_local_ldap:
                ldap = LDAP(self.server_addr, self.server_port, self.username,
                            self.password, self.bind)
                ok, data = ldap.query(username)
                if not ok:
                    msg = "user {} not known in user database or LDAP server" \
                          " down or credentials wrong. More info: {}"
                    msg = msg.format(username, data)
                    raise ApiError(msg)
                self._local_ldap_db_add_entry(data, username)
                data_local_ldap = data
            return data_local_ldap
        if not data_local_db and not self.ldap_method:
            msg = "user {} not known in local user database. Please add" \
                  " manually entry for this user in local user.db"
            msg = msg.format(username)
            raise ApiError(msg)
        return data_local_db
