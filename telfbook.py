# 2022-10-29
import os
import functools as ft
import sqlite3 as sq3
import datetime as dt

# my_keys = ['id', 'name', 'tlf1', 'comment1', 'tlf2', 'comment2', 'tlf3', 'comment3', 'adr', 'job', 
#      'mail', 'site', 'comment', 'cr_dt', 'upd_dt']


def now() -> tuple:
    '''
    Возвращает кортеж с текущими датой и временем в текстовом формате. Нужно для сохранения даты
    создания и изменения карточек
    '''
    k, t = dt.datetime.now(), '{:0>2}'
    return (
        '{:0>4}'.format(k.year), t.format(k.month), t.format(k.day),
        t.format(k.hour), t.format(k.minute), t.format(k.second)
    )


class CardList():
    '''
    Объектом класса является база данных контактов
    obj.dbfile - текущее имя файла базы данных
    obj.new_card(crd: dict) - создание новой карточки контакта
    obj.row_count() -> int - общее количество строк в БД
    obj.avail_id() -> list - список доступных id карточек
    obj.delete_card(card_id: int) - удаление строки по известному id
    obj.get_card(card_id: int) -> dict - вернёт запись по известному id
    obj.update_card(card_id: int, column_to_update: str, new_value: str) - изменить ячейку
    obj.search(pattern: str) -> list - вернет список карточек, в полях которых встречается шаблон pattern
    obj.any_req(db_request: str) -> list - произвольный запрос к базе данных
    '''
    
    def __init__(self, dbfilename: str):
        '''
        В начале, просто проверяем существование файла базы данных, создаём его если не существует
        '''
        # Имя файла базы данных
        self.dbfile = dbfilename

        conn = sq3.connect(self.dbfile)
        curs = conn.cursor()
        
        rownames = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT, ", # ID карточки
            "name TEXT NOT NULL, ", # ФИО
            "tlf1 TEXT DEFAULT 'undefined', ", # Первый телефон
            "comment1 TEXT DEFAULT '', ", # Комментарий к первому телефону
            "tlf2 TEXT DEFAULT '', ", # Второй телефон
            "comment2 TEXT DEFAULT '', ", # Комментарий ко второму телефону
            "tlf3 TEXT DEFAULT '', ", # Третий телефон
            "comment3 TEXT DEFAULT '', ", # Комментарий к третьему телефону
            "adr TEXT DEFAULT '', ", # Адрес
            "job TEXT DEFAULT '', ", # Место работы
            "mail TEXT DEFAULT '', ", # Электронная почта
            "site TEXT DEFAULT '', ", # Сайт
            "comment TEXT DEFAULT 'No comment', ", # Комментарий
            "cr_dt TEXT, ", # Дата создания карточки
            "upd_dt TEXT" # Дата последнего изменения
        ]
        rqtosq3 = "CREATE TABLE IF NOT EXISTS cards ({0});".format(ft.reduce((lambda x, y: x+y), rownames))
        curs.execute(rqtosq3)
        conn.commit()

    def new_card(self, crd: dict):
        '''
        Добавление нового элемента в базу данных. В словаре crd обязательно только поле 'name'. Все
        поля должны быть текстовыми. Поля, которые будут внесены в карточку:
        'name', 'tlf1', 'comment1', 'tlf2', 'comment2', 'tlf3', 'comment3', 'adr', 'job', 
        'mail', 'site', 'comment'
        Остальные ключи - игнорируются
        '''
        res = 0
        if 'name' in crd:

            # Очищаем словарь от лишних полей. Собираем допустимые ключи из crd и их значения в отдельные списки
            my_keys = {'name', 'tlf1', 'comment1', 'tlf2', 'comment2', 'tlf3', 'comment3', 'adr', 'job', 
                'mail', 'site', 'comment', 'cr_dt', 'upd_dt'}
            crdkeys = [i for i in list(crd.keys()) if i in my_keys]
            crditems = [crd[i] for i in crdkeys] + ['{0}-{1}-{2} {3}:{4}:{5}'.format(*now())]*2
            crdkeys.extend(['cr_dt', 'upd_dt'])

            # Формируем запрос к БД
            rq_cols = ", ".join([str(i) for i in crdkeys])
            rq_items = ", ".join(["'"+str(i)+"'" for i in crditems])
            
            conn = sq3.connect(self.dbfile)
            curs = conn.cursor()

            rtins = "INSERT INTO cards ({0}) VALUES ({1});".format(rq_cols, rq_items)
            curs.execute(rtins)
            conn.commit()

        else: 
            return 1
        
    def row_count(self) -> int:
        '''
        Вернёт общее количество записей в БД
        '''
        conn = sq3.connect(self.dbfile)
        curs = conn.cursor()
        rqcnt = "SELECT COUNT(*) FROM cards;"
        curs.execute(rqcnt)
        rsp = curs.fetchall()[0][0]
        conn.commit()
        return rsp     

    def avail_id(self) -> list:
        '''
        Вернет список доступных id
        '''
        conn = sq3.connect(self.dbfile)
        curs = conn.cursor()
        rqavid = "SELECT id FROM cards;"
        curs.execute(rqavid)
        rsp = curs.fetchall()
        conn.commit()
        return [i[0] for i in rsp]

    def delete_card(self, card_id: int):
        '''
        Удалит карточку с указанным id
        '''
        if card_id in self.avail_id():
            conn = sq3.connect(self.dbfile)
            curs = conn.cursor()
            rqdc = "DELETE FROM cards WHERE id={0};".format(card_id)
            curs.execute(rqdc)
            #rsp = curs.fetchall()
            conn.commit()
            return 0
        else:
            return 1

    def get_card(self, card_id: int) -> dict:
        '''
        Вернёт карточку в виде словаря по заданному id. Если такого id нет - вернет пустой словарь.
        '''
        if card_id in self.avail_id():
            conn = sq3.connect(self.dbfile)
            curs = conn.cursor()
            rqgetcrd = "SELECT * FROM cards WHERE id = {0};".format(card_id)
            curs.execute(rqgetcrd)
            rsp = curs.fetchall()
            conn.commit()
            my_keys = ['id', 'name', 'tlf1', 'comment1', 'tlf2', 'comment2', 'tlf3', 'comment3', 'adr', 'job', 
                'mail', 'site', 'comment', 'cr_dt', 'upd_dt']

            return dict(zip(my_keys, rsp[0]))
        else:
            return dict()

    def update_card(self, card_id: int, column_to_update: str, new_value: str) -> int:
        '''
        Изменяет поле column_to_update в карточке с card_id на значение new_value.
        Функция вернет 0 при удачной корректировке поля, и 1 при неудаче
        Допустимые для изменения поля:
        'name', 'tlf1', 'comment1', 'tlf2', 'comment2', 'tlf3', 'comment3', 'adr', 'job', 'mail', 'site', 'comment'
        '''
        if (card_id in self.avail_id()) and (column_to_update in {'name', 'tlf1', 'comment1', 'tlf2', 'comment2', 'tlf3',
            'comment3', 'adr', 'job', 'mail', 'site', 'comment'}):
            conn = sq3.connect(self.dbfile)
            curs = conn.cursor()
            rqupd = "UPDATE cards SET {0}='{1}', upd_dt='{3}' WHERE id={2};".format(column_to_update, new_value, card_id, '{0}-{1}-{2} {3}:{4}:{5}'.format(*now()))
            curs.execute(rqupd)
            conn.commit()
            return 0
        else:
            return 1

    def search(self, pattern: int) -> list:
        '''
        Поиск шаблона pattern в карточках. Регистрозависимый. Вернет список словарей-карточек
        '''
        my_keys = ['name', 'tlf1', 'comment1', 'tlf2', 'comment2', 'tlf3', 'comment3', 'adr', 'job', 
                'mail', 'site', 'comment', 'cr_dt', 'upd_dt']
        conn = sq3.connect(self.dbfile)
        curs = conn.cursor()
        # Формируем запрос к БД
        rq = (" OR ".join(list(map((lambda x: "("+x+" LIKE '%{0}%')"), my_keys)))).format(pattern)
        rqsearch = "SELECT * FROM cards WHERE {0};".format(rq)
        curs.execute(rqsearch)
        rsp = curs.fetchall()
        conn.commit()        
        # Оформляем результат поиска
        return [dict(zip(['id']+my_keys, i)) for i in rsp]

    def any_req(self, db_request: str) -> list:
        '''
        Произвольный sqlite-запрос к базе данных. Имя таблицы - cards
        '''
        conn = sq3.connect(self.dbfile)
        curs = conn.cursor()
        curs.execute(db_request)
        rsp = curs.fetchall()
        conn.commit()
        return rsp


# Собственно, программа для консоли. Файл можно использовать как модуль, подключив его к GUI
if __name__=='__main__':

    # Имя файла основной базы данных
    dbname = 'tlfbook.tdb'
    count = 0

    def inp_val(name_val: str, card_key: str, old_card: dict):
        '''
        Ввод новых значений полей карты во время редактирования
        Возвращает новое отредактированное значение, или **, если необходимо прервать редактирование карты
        '''
        result = ''
        print('\n{0}:'.format(name_val), old_card[card_key])
        new_val = input('New {0}: '.format(name_val.lower()))
        if new_val=='':
            result = old_card[card_key]
        elif new_val=='0':
            result = '**'
        else:
            result = new_val
        return result


    class DataBase(CardList):
        '''
        Адаптация класса базы данных справочника для работы с консолью
        '''
        def change_dbname(self, new_dbname: str):
            # Тут должна быть проверка на существование базы данных с новым именем
            pass

        def show_card(self, crd: dict):
            '''
            Просто выводит карточку в консоль
            '''
            print('\n')
            print('='*50)
            print('id: {0},  NAME: {1}'.format(crd['id'], crd['name']))
            print('-'*50)
            if crd['tlf1']!='':
                print('Telephone 1:  {0}{1}'.format(crd['tlf1'], ((', '+crd['comment1']) if crd['comment1']!='' else '')))
            if crd['tlf2']!='':
                print('Telephone 2:  {0}{1}'.format(crd['tlf2'], ((', '+crd['comment2']) if crd['comment2']!='' else '')))
            if crd['tlf3']!='':
                print('Telephone 3:  {0}{1}'.format(crd['tlf3'], ((', '+crd['comment3']) if crd['comment3']!='' else '')))
            print()
            if crd['adr']!='':
                print('ADDRESS:', crd['adr'])
            if crd['job']!='':
                print('ORGANIZATION:', crd['job'])
            if crd['mail']!='':
                print('E-MAIL:', crd['mail'])
            if crd['site']!='':
                print('PERSONAL SITE:', crd['site'])
            print()
            print('COMMENT:', crd['comment'])
            print()
            print('Created: {0},  last update: {1}'.format(crd['cr_dt'], crd['upd_dt']))
            print('='*50)
            print()

        def view_and_update_card(self, v_id: int):
            '''
            Выводит в консоль карточку из БД и позволяет ее редактировать
            Возвращает True после удаления карточки, что позволяет сделать новую выборку
            '''
            res = False
            crd_to_show = self.get_card(v_id)
            self.show_card(crd_to_show)
            while True:
                print('0. Back to search')
                print('1. Edit')
                print('2. Delete')
                ch3 = input('Enter you choice: ')
                if ch3=='0':
                    break
                elif ch3=='2':
                    print('\nDelete card id={0} and name="{1}"?'.format(crd_to_show['id'], crd_to_show['name']))
                    ch4 = input('Input y/n: ')
                    if ch4=='y':
                        tmp_id = crd_to_show['id']
                        self.delete_card(v_id)
                        print('\nCard id={0} deleted!\n'.format(tmp_id))
                        res = True
                        break
                elif ch3=='1':
                    print('Edit card. Input new values. Press "Enter" to skip or "0" to stop.')
                    while True:
                        edited_card = {}
                        print('\nid:', crd_to_show['id'])

                        nvc = inp_val('Name', 'name', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'name', nvc)

                        nvc = inp_val('Telephone 1', 'tlf1', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'tlf1', nvc)

                        nvc = inp_val('Comment 1', 'comment1', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'comment1', nvc)

                        nvc = inp_val('Telephone 2', 'tlf2', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'tlf2', nvc)
                        
                        nvc = inp_val('Comment 2', 'comment2', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'comment2', nvc)

                        nvc = inp_val('Telephone 3', 'tlf3', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'tlf3', nvc)
                        
                        nvc = inp_val('Comment 3', 'comment3', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'comment3', nvc)                          

                        nvc = inp_val('Address', 'adr', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'adr', nvc)                        

                        nvc = inp_val('Organization', 'job', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'job', nvc)

                        nvc = inp_val('E-mail', 'mail', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'mail', nvc)

                        nvc = inp_val('Personal site', 'site', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'site', nvc)

                        nvc = inp_val('Comment', 'comment', crd_to_show)
                        if nvc=='**':
                            break
                        else:
                            self.update_card(crd_to_show['id'], 'comment', nvc)                       

                        self.show_card(self.get_card(crd_to_show['id']))

                        break
                else:
                    print('Error')
            return res    

        def search_partial(self, patt: str) -> list:
            '''
            Выборка из БД по шаблону, возвращает удобные для отображения в консоли строки
            '''
            # Добавляем строку заголовков
            rsp = [{'id': 'id', 'name': 'name', 'tlf1': 'telephone', 'comment': 'comment'}] + self.search(ptt)
            # Собираем длины всех элементов в двумерный список, транспонируем его
            len_lst = list(zip(*[[len(str(i['id'])), len(i['name']), len(i['tlf1']), len(i['comment'])] for i in rsp]))
            # Результирующий список с подогнанными длинами строк
            res_lst = [
                '  '.join(['{0: >{1}}'.format(i['id'], max(len_lst[0])),
                ('{0: <{1}}'.format(i['name'], max(len_lst[1])))[:30],
                ('{0: <{1}}'.format(i['tlf1'], max(len_lst[2])))[:20], 
                ('{0: <{1}}'.format(i['comment'], max(len_lst[3])))[:20] ])
            for i in (rsp)]
            # Список доступных id в текущей выборке
            local_id_avail = [i['id'] for i in rsp[1:]]
            return (res_lst, local_id_avail)
        

    db = DataBase(dbname)

    print('Now: {0}-{1}-{2}  {3}:{4}:{5}'.format(*now()))
    
    mainloop = True
    while mainloop:

        print('\n1. Database filename: "{0}", cards in db: {1}'.format(db.dbfile, db.row_count()))
        print('2. Search, view and update cards\n3. New card\n0. End')
        ch = input('Enter you choice: ')

        if ch=='0':
            mainloop = False

        # Выбор или создание файла базы данных
        elif ch=='1':
            q = False
            while True:
                # Переменная q обеспечит выход из цикла при оздании нового файла БД
                if q:
                    break
                print('\nCurrent database filename: "{0}"\n'.format(db.dbfile))
                # Список доступных файлов БД в текущей папке:
                db_list = ['Back'] + [i for i in os.listdir('.') if ((i!=db.dbfile) and (i.endswith('.tdb')))] + ['Create a new DB file']
                index_list = [i for i in range(len(db_list))]
                sel_db = dict(zip(index_list, db_list))

                print('Choose available DB file or create a new file:')
                for i in index_list:
                    print('{0}. {1}'.format(i, db_list[i]))
                
                ch5 = input('\nEnter you choice: ')
                if ch5=='0':
                    break
                elif ch5.isdigit():
                    if int(ch5) in index_list:
                        if int(ch5)==index_list[-1]:
                            print('СОЗДАНИЕ НОВОГО ФАЙЛА БД!')
                            while True:
                                ch6 = input('\nNew database filename without ".tdb": ')
                                new_database = (ch6.replace('.', '') + '.tdb')
                                db = DataBase(new_database)
                                q = True
                                break
                        else:
                            db.dbfile = sel_db[int(ch5)]
                            dbname = db.dbfile
                            break
                    
                    else:
                        print('"{0}" - error!'.format(ch5))
                    
                else:
                    print('"{0}" - error!'.format(ch5))

        # Поиск, просмотр и редактирование записей
        elif ch=='2':
            while True:
                print('\nInput ID of required card, pattern to search, or 0 to stop.')
                print('Use "*" request to view full DB, or "*some_pattern" to find some_pattern in cards')
                ch1 = input('Enter you choice: ')
                if (ch1=='0' or ch1==''):
                    break
                elif ch1.isdigit():
                    if int(ch1) in db.avail_id():
                        # Если запрос - число, входящее в список доступных id, то выводим соответствующую
                        #    карточку для просмотра и редактирования
                        db.view_and_update_card(ch1)
                    else:
                        print("\nId {0} not found! Available ids: {1}".format(int(ch1), (', '.join(list(map(str, db.avail_id()))))[:200]  ))
                else: 
                    # Остальные варианты запроса считаем шаблонами. Убираем звёздочку в начале шаблона
                    if ch1[0]=='*':
                        ptt = ch1[1:]
                    else:
                        ptt = ch1
                    srch, av_ids = db.search_partial(ptt)
                    if len(av_ids)>0:
                        print('\nHave a {0} matches:'.format(len(av_ids)))
                        while True:
                            print('\n')
                            # Добавляем пустую строку для отделения заголовков от самой таблицы
                            if srch[1]!='':
                                srch.insert(1, '')
                            print(*srch, sep='\n')
                            print('\nSelect id card to update or 0 to perform another search.')
                            ch2 = input('Enter you choice: ')
                            if ch2=='0':
                                break
                            elif ch2.isdigit():
                                if int(ch2) in av_ids:
                                    # Показываем полную карточку
                                    mk_break = db.view_and_update_card(int(ch2))
                                    if mk_break:
                                        break
                                else:
                                    print('\nId {0} not found in this search!'.format(ch2))
                            else:
                                print('\n"{0}" is not id!'.format(ch2))
                        
                    else:
                        print("\nNo matches for pattern '{0}' in database!".format(ptt))
                    
        # Ввод новой карточки с контактом и запись ее в базу данных
        elif ch=='3':
            new_card = dict()
            while True:
                print('\nNew card creation. Type 0 to cancel (any field) or 00 to skip (except name).')
                
                # Ввод имени
                new_name = input('Enter name (skip not available): ')
                if new_name=='0':
                    break
                else:
                    new_card['name'] = new_name if new_name!='' else 'Undefined name'

                # Ввод телефонов и комментариев к ним. Переменная skip позволит пропустить все
                #    остальные номера телефонов и комментарии
                skip = False
                new_tlf1 = input('Enter telephone number: ')
                if new_tlf1=='0':
                    break
                elif new_tlf1=='00':
                    skip = True
                else:
                    new_card['tlf1'] = new_tlf1
                if not skip:
                    new_comment1 = input('Enter comment to telephone number: ')
                    if new_comment1=='0':
                        break
                    elif new_comment1=='00':
                        # Пропускаем комментарий без skip = True, чтобы дать возможность ввести
                        # второй номер телефона без комментария
                        pass
                    else:
                        new_card['comment1'] = new_comment1
                if not skip:
                    new_tlf2 = input('Enter second telephon number: ')
                    if new_tlf2=='0':
                        break
                    elif new_tlf2=='00':
                        skip = True
                    else:
                        new_card['tlf2'] = new_tlf2
                if not skip:
                    new_comment2 = input('Enter comment to second telephone number: ')
                    if new_comment2=='0':
                        break
                    elif new_comment2=='00':
                        pass
                    else:
                        new_card['comment2'] = new_comment2
                if not skip:
                    new_tlf3 = input('Enter third telephon number: ')
                    if new_tlf3=='0':
                        break
                    elif new_tlf3=='00':
                        skip = True
                    else:
                        new_card['tlf3'] = new_tlf3
                if not skip:
                    new_comment3 = input('Enter comment to third telephone number: ')
                    if new_comment3=='0':
                        break
                    elif new_comment3=='00':
                        pass
                    else:
                        new_card['comment3'] = new_comment3
                
                # Ввод адреса контакта
                new_adr = input('Enter address: ')
                if new_adr=='0':
                    break
                elif new_adr=='00':
                    pass
                else:
                    new_card['adr'] = new_adr

                # Ввод места работы контакта
                new_job = input('Enter job: ')
                if new_job=='0':
                    break
                elif new_job=='00':
                    pass
                else:
                    new_card['job'] = new_job

                # Ввод электронной почты
                new_mail = input('Enter email: ')
                if new_mail=='0':
                    break
                elif new_mail=='00':
                    pass
                else:
                    new_card['mail'] = new_mail

                # Ввод сайта
                new_site = input('Enter URL: ')
                if new_site=='0':
                    break
                elif new_site=='00':
                    pass
                else:
                    new_card['site'] = new_site

                # Ввод комментария к карточке
                new_comment = input('Notes: ')
                if new_comment=='0':
                    break
                elif new_comment=='00':
                    pass
                else:
                    new_card['comment'] = new_comment

                # Сохраняем новую карточку в БД
                try:
                    db.new_card(new_card)
                    print('New card is created!')
                except:
                    print('New card is NOT created! Have a some problems')
                break

        else:
            pass
