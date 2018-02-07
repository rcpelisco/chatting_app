class DatabaseManager:
    
    def login(mysql, username, password):
        cur = mysql.connection.cursor()
        sql_query = '''SELECT user_id, username, first_name, last_name FROM users WHERE 
            username = %s AND password = %s'''
        cur.execute(sql_query, [username, password])
        result = list(cur.fetchall())
        cur.close() 
        return result

    def register(mysql, user):
        cur = mysql.connection.cursor()
        sql_query = '''INSERT INTO users SET username = %s, password = %s, 
            first_name = %s, last_name = %s'''
        cur.execute(sql_query, [user['username'], user['password'], user['first_name'], user['last_name']])
        mysql.connection.commit()
    
    def search(mysql, user_id, user_query):
        cur = mysql.connection.cursor()
        sql_query = '''SELECT username, first_name, last_name FROM users WHERE 
            first_name LIKE %s OR last_name LIKE %s OR username LIKE %s ORDER BY 
            first_name, last_name'''
        cur.execute(sql_query, [user_query + '%', user_query + '%', user_query + '%'])
        results = list(cur.fetchall())
        print(results)
        for result in results:
            result['is_friends'] = False
            if(DatabaseManager.is_friends(mysql, user_id, result['username'])):
                result['is_friends'] = True
        cur.close()
        print(results)
        return results

    def get_user_id(mysql, username):
        cur = mysql.connection.cursor()
        sql_query = 'SELECT user_id FROM users WHERE username = %s'
        cur.execute(sql_query, [username])
        result = list(cur.fetchall())
        return result[0]['user_id']

    def add_contact(mysql, user_id, username):
        cur = mysql.connection.cursor()
        other_contact = DatabaseManager.get_user_id(mysql, username)
        sql_query = 'INSERT INTO friends_list SET user_1 = %s, user_2 = %s'
        cur.execute(sql_query, [user_id, other_contact])
        mysql.connection.commit()

    def is_friends(mysql, user_id, username):
        cur = mysql.connection.cursor()
        other_contact = DatabaseManager.get_user_id(mysql, username)
        sql_query = '''SELECT friend_id FROM friends_list 
            WHERE (user_1 = %s AND user_2 = %s) OR (user_1 = %s AND user_2 = %s)'''
        cur.execute(sql_query, [user_id, other_contact, other_contact, user_id])
        result = list(cur.fetchall())
        return len(result) > 0

    def get_contacts(mysql, user_id):
        cur = mysql.connection.cursor()
        sql_query = '''SELECT username, CONCAT_WS(' ', first_name, last_name) as contact_name FROM users WHERE 
            user_id IN (SELECT user_1 FROM friends_list WHERE user_2 = %s) OR 
            user_id IN(SELECT user_2 FROM friends_list WHERE user_1 = %s)'''
        cur.execute(sql_query, [user_id, user_id])
        user = list(cur.fetchall())
        return user

    def get_user(mysql, username):
        cur = mysql.connection.cursor()
        sql_query = '''SELECT first_name, last_name FROM users WHERE username = %s'''
        cur.execute(sql_query, [username])
        user = list(cur.fetchall())
        return user[0]

    def get_last_message(mysql, user_id, username):
        cur = mysql.connection.cursor()
        sql_query = '''SELECT message FROM messages WHERE'''

    def send_message(mysql, message, sender, recipient):
        cur = mysql.connection.cursor()
        other_contact = DatabaseManager.get_user_id(mysql, recipient)
        user_id = DatabaseManager.get_user_id(mysql, sender)
        sql_query = '''INSERT INTO messages SET message = %s, sender_id = %s, recipient_id = %s'''
        cur.execute(sql_query, [message, user_id, other_contact])
        mysql.connection.commit()

    def get_messages(mysql, user_id, username):
        cur = mysql.connection.cursor()
        other_contact = DatabaseManager.get_user_id(mysql, username)
        sql_query = '''SELECT message, created_on, sender_id,
            (SELECT username FROM users WHERE user_id = sender_id) as sender, 
            (SELECT username FROM users WHERE user_id = recipient_id) as recipient FROM messages 
            WHERE (sender_id = %s AND recipient_id = %s) OR
            (recipient_id = %s AND sender_id = %s) ORDER BY created_on'''
        cur.execute(sql_query, [user_id, other_contact, user_id, other_contact])
        messages = list(cur.fetchall()) 
        return messages

    def save_file(mysql, file_name, sender, recipient):
        cur = mysql.connection.cursor()
        other_contact = DatabaseManager.get_user_id(mysql, recipient)
        sql_query = '''INSERT INTO files (file_name, file_path, sender_id, recipient_id) 
            SELECT %s, concat(%s, '-', MAX(file_id) + 1, '.', %s), %s, %s FROM files'''
        cur.execute(sql_query, ['.'.join([file_name['filename'], file_name['file_ext']]), 
            file_name['filename'], file_name['file_ext'], sender, other_contact])
        mysql.connection.commit()
        sql_query = '''SELECT LAST_INSERT_ID() as id FROM files LIMIT 1'''
        cur.execute(sql_query)
        id = list(cur.fetchall())
        return str(id[0]['id'])

    def get_files(mysql, user_id, username):
        cur = mysql.connection.cursor()
        other_contact = DatabaseManager.get_user_id(mysql, username)
        sql_query = '''SELECT file_id, file_name, created_on, 
            (SELECT username FROM users WHERE user_id = sender_id) as sender, 
            (SELECT username FROM users WHERE user_id = recipient_id) as recipient FROM files 
            WHERE (sender_id = %s AND recipient_id = %s) OR
            (recipient_id = %s AND sender_id = %s) ORDER BY created_on'''
        cur.execute(sql_query, [user_id, other_contact, user_id, other_contact])
        files = list(cur.fetchall())
        return files

    def get_file(mysql, file_id):
        cur = cur = mysql.connection.cursor()
        sql_query = '''SELECT file_name, file_path FROM files WHERE file_id = %s'''
        cur.execute(sql_query, [file_id])
        new_file = list(cur.fetchall())
        print(new_file)
        return new_file[0]
