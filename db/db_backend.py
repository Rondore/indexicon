#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import Callable
from mysql.connector.cursor import MySQLCursor
from sqlite3 import Cursor as SQLiteCursor

import util

class DbBackend(ABC):
    @abstractmethod
    def stand_in_string(self) -> str:
        pass

    @abstractmethod
    def unix_time(self) -> str:
        pass

    @abstractmethod
    def get_cursor(self) -> (MySQLCursor | SQLiteCursor):
        pass

    @abstractmethod
    def execute_and_close(self, query: str, values=()) -> None:
        pass

    @abstractmethod
    def execute_and_return(self, query: str, values=()) -> (MySQLCursor | SQLiteCursor):
        pass

    def update_scrape_stamp(self, id: int) -> None:
        query = 'UPDATE `source` SET `s_last_crawl`=' + self.unix_time() + ' WHERE `s_id`=' + str(id)
        self.execute_and_close(query)

    def save_url(self, id: int, link: str):
        string = self.stand_in_string()
        name = link.split('/')[-1]
        search = name.lower()
        query = 'INSERT INTO `file` (`f_source`, `f_url`, `f_name`, `f_search_text`) VALUES (' + string + ', ' + string + ', ' + string + ', ' + string + ')'
        self.execute_and_close(query, values=(id, link, name, search))

    def purge_source(self, id: int):
        self.execute_and_close('DELETE FROM `file` WHERE `f_source`=' + str(id))

    def get_passovers(self, source_id, base_url: str):
        cursor = self.get_cursor()
        cursor.execute('SELECT p_id, p_directory FROM passover WHERE p_source=' + str(source_id))
        passover_dirs_raw: list = cursor.fetchall()
        passovers: list[str] = []
        for passover_id, dir in passover_dirs_raw:
            passovers.append(util.get_combined_url(base_url, dir))
        cursor.close()
        return passovers

    @abstractmethod
    def commit(self) -> None:
        pass
    
    def for_each_source(self, id: int, function: Callable[[int, str, int, bool], None], only_enabled=True) -> int:
        cursor = self.get_cursor()
        query = 'SELECT `s_id`, `s_url`, ( ' + self.unix_time() + ' - `s_last_crawl` ) AS age, s_enabled FROM `source`'
        where_list = WhereList()
        if only_enabled:
            where_list.add('s_enabled=1')
        if id != -1:
            where_list.add('s_id=' + str(id))
        query += where_list.compile() + ';'
        cursor.execute(query)
        total = 0
        while True:
            rows: list = cursor.fetchmany(20)
            if not rows:
                break
            for id, url, age, enabled in rows:
                total += 1
                id = int(id)
                url = str(url)
                age = int(age)
                enabled = bool(enabled)
                function(id, url, age, enabled)
        cursor.close()
        return total
    
    def for_each_source_with_count(self, id: int, function: Callable[[int, str, int, bool, int], None], only_enabled=True) -> int:
        cursor = self.get_cursor()
        query = 'SELECT `s_id`, `s_url`, ( ' + self.unix_time() + ' - `s_last_crawl` ) AS age, `s_enabled`, `f_count` FROM `source` ' + \
            'LEFT JOIN (SELECT `f_source`, COUNT(*) AS f_count FROM file GROUP BY `f_source`) AS count_table ON source.`s_id`=count_table.f_source'
        where_list = WhereList()
        if only_enabled:
            where_list.add('s_enabled=1')
        if id != -1:
            where_list.add('s_id=' + str(id))
        query += where_list.compile() + ';'
        cursor.execute(query)
        total = 0
        while True:
            rows: list = cursor.fetchmany(20)
            if not rows:
                break
            for id, url, age, enabled, count in rows:
                total += 1
                id = int(id)
                url = str(url)
                age = int(age)
                enabled = bool(enabled)
                clean_count = 0
                if count is not None:
                    clean_count = int(count)
                function(id, url, age, enabled, clean_count)
        cursor.close()
        return total
    
    def for_each_passover(self, id: int, function: Callable[[int, str, str], None], only_enabled=True) -> int:
        cursor = self.get_cursor()
        query = 'SELECT `p_id`, `s_url`, `p_directory` FROM source, passover'
        where_list = WhereList()
        where_list.add('s_id=p_source')
        if id != -1:
            where_list.add('p_id=' + str(id))
        query += where_list.compile() + ';'
        cursor.execute(query)
        count = 0
        while True:
            rows: list = cursor.fetchmany(20)
            if not rows:
                break
            for id, url, directory in rows:
                count += 1
                id = int(id)
                url = str(url)
                directory = str(directory)
                function(id, url, directory)
        cursor.close()
        return count

    def search_db(self, unclean_search, function: Callable[[str, str, str], None]) -> int:
        string = self.stand_in_string()
        words = get_search_array(unclean_search)
        where_list = WhereList()
        where_list.add('`s_enabled`=1')
        where_list.add('`f_source`=`s_id`')
        value_list: list[str] = []
        for term in words:
            if term[0] == '-':
                value_list.append('%' + term[1:] + '%')
                where_list.add("`f_search_text` NOT LIKE " + string)
            else:
                value_list.append('%' + term + '%')
                where_list.add("`f_search_text` LIKE " + string)
        query = 'SELECT `f_name`, `f_url`, `s_url` from source, file' + where_list.compile() + " ORDER BY f_search_text;"
        cursor = self.get_cursor()
        cursor.execute( query, value_list )
        count = 0
        while True:
            rows: list = cursor.fetchmany(20)
            if not rows:
                break
            for name, file, source_url in rows:
                count += 1
                name = str(name)
                file = str(file)
                source_url = str(source_url)
                function(name, file, source_url)
        cursor.close()
        return count
    
    def add_source(self, url: str):
        self.execute_and_close('INSERT INTO source (`s_url`) VALUES (' + self.stand_in_string() + ');', (url,))
        self.commit()

    def delete_source(self, id: int) -> str:
        standin = self.stand_in_string()
        cursor = self.execute_and_return('SELECT `s_url` FROM source WHERE `s_id`=' + standin + ';', (id,))
        row = cursor.fetchone()
        url = ''
        if row:
            url = str(row[0])
        cursor.close()
        self.execute_and_close('DELETE FROM file WHERE `f_source`=' + standin + ';', (id,))
        self.execute_and_close('DELETE FROM source WHERE `s_id`=' + standin + ';', (id,))
        self.execute_and_close('DELETE FROM passover WHERE `p_source`=' + standin + ';', (id,))
        self.commit()
        return url
    
    def add_passover(self, url: str):
        standin = self.stand_in_string()
        cursor = self.execute_and_return('SELECT `s_id`, `s_url` FROM source WHERE ' + standin + ' like `s_url` || "%";', (url,))
        row = cursor.fetchone()
        id = -1
        source_url = ''
        if row:
            id = int(str(row[0]))
            source_url = str(row[1])
        cursor.close()
        if id != -1:
            path = url[len(source_url):]
            self.execute_and_close('INSERT INTO passover (`p_source`, `p_directory`) VALUES (' + standin + ', ' + standin + ');', (id, path))
            self.commit()

    def delete_passover(self, id: int) -> list[str]:
        standin = self.stand_in_string()
        cursor = self.execute_and_return('SELECT `s_url`, `p_directory` FROM passover, source WHERE `p_id`=' + standin + ' AND `s_id`=`p_source`;', (id,))
        row = cursor.fetchone()
        source_url = ''
        directory = ''
        if row:
            source_url = str(row[0])
            directory = str(row[1])
        cursor.close()
        self.execute_and_close('DELETE FROM passover WHERE `p_id`=' + standin + ';', (id,))
        self.commit()
        return [source_url, directory]
    
    def enable_source(self, id: int):
        standin = self.stand_in_string()
        self.execute_and_close('UPDATE source SET `s_enabled`=1 WHERE `s_id`=' + standin + ';', (id,))
        self.commit()
    
    def disable_source(self, id: int):
        standin = self.stand_in_string()
        self.execute_and_close('UPDATE source SET `s_enabled`=0 WHERE `s_id`=' + standin + ';', (id,))
        self.commit()

class WhereList:
    def __init__(self):
        self.list: list[str] = []

    def add(self, clause: str):
        self.list.append(clause)

    def compile(self) -> str:
        output = ''
        if len(self.list) > 0:
            output += ' WHERE ' + ' AND '.join(self.list)
        return output

def get_search_array( search_string ) -> list[str]:
    words = []
    for term in search_string.split():
        term = term.strip().lower()
        if( len( term ) > 0 ):
            words.append(term)
    return words
