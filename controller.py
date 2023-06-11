from flask import session, url_for, redirect
from passlib.hash import bcrypt
import sqlite3
import os
from werkzeug.utils import secure_filename

class Controller:

    def __init__(self):
        self.secret_key = self.get_session_key()
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def get_is_logged_in(self, app):
        app.secret_key = self.secret_key
        return session.get('loggedIn')

    def get_stored_login(self):
        sql = "SELECT jmeno, heslo from prihlaseni LIMIT 1"
        return self.execute_sql(sql)[0]

    def execute_sql(self, sql, returnLastRow = False):
        with sqlite3.connect("database.sqlite3") as con:
            cur = con.cursor()
            cur.execute(sql)
            resp = cur.fetchall() 

        if(returnLastRow==True):
            return cur.lastrowid
        return resp

    def login_attempt(self, app, name, password):
        stored_login = self.get_stored_login()
        if(name == stored_login[0]):
            if bcrypt.verify(password, stored_login[1]):
                app.secret_key = self.secret_key
                session['loggedIn'] = True

    def save_images(self, files):

        saved_images = []

        if len(files) == 0:
            return saved_images

        #saving images
        for file in files:
            if self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join("static/image", filename)
                file.save(save_path)
                saved_images.append("image/" + filename)

        return saved_images
    
    def tutorial_save_new(self, nadpis, text, uploaded_images):
        
        sql = f"INSERT INTO navody (nadpis, text) \
               VALUES ('{nadpis}', '{text}');"
        row_id = self.execute_sql(sql, True)

        self.insert_images(uploaded_images, row_id)

    def tutorial_edit_save(self, id, nadpis, text, image_urls, uploaded_images):
        
        sql = f"UPDATE navody \
                SET nadpis='{nadpis}', text='{text}' \
                WHERE id='{id}';"
        self.execute_sql(sql)

        sql = f"DELETE from obrazky WHERE id_navod='{id}'"
        self.execute_sql(sql)

        new_image_urls = []
        for url in image_urls:
            new_image_urls.append(url.replace('/static/', ''))

        num_of_inserts = self.insert_images(new_image_urls, id)
        self.insert_images(uploaded_images, id, num_of_inserts) 

    def delete_tutorial(self, id):
        sql = f"DELETE FROM navody WHERE id='{id}';"
        self.execute_sql(sql)

        sql = f"DELETE FROM obrazky WHERE id_navod='{id}'"
        self.execute_sql(sql)

    def insert_images(self, images, id, poradi = 1):

        poradi = poradi
        for image in images:
            sql = f"INSERT INTO obrazky (cesta, poradi, id_navod) \
                   VALUES ('{image}', '{poradi}', '{id}')"
            self.execute_sql(sql)
            poradi += 1

        return poradi

    def get_tutorial(self, id, with_id = False):

        if(with_id):
            sql = "SELECT id, nadpis, text"  
        else: 
            sql = "SELECT nadpis, text"
        
        sql += " FROM navody \
            WHERE id=" + str(id)
        
        tutorial = self.execute_sql(sql)
        images = self.get_tutorial_images(id)

        return tutorial, images

    def get_administration_tutorials(self):
        sql = "SELECT id, nadpis FROM navody"
        return self.execute_sql(sql)

    def get_tutorial_images(self, id, onlyFirst = False):
        sql = "SELECT cesta, poradi \
            FROM obrazky \
            WHERE id_navod=" + str(id) + " \
            ORDER BY poradi ASC"
        if(onlyFirst):
            sql += " LIMIT 1"

        return self.execute_sql(sql)

    def get_session_key(self):
        sql = "SELECT key from sessionKeys LIMIT 1"
        return self.execute_sql(sql)[0][0]

    def get_tutorials_short(self):
        #sql = "SELECT * from navody"
        sql = "SELECT navody.id, navody.nadpis, navody.text, obrazky.cesta as imgCesta, obrazky.poradi as imgPoradi \
            FROM navody \
            LEFT JOIN obrazky \
            ON obrazky.id_navod=navody.id AND obrazky.poradi=1\
            GROUP BY navody.id \
            ORDER BY navody.nadpis"
        tutorials = self.execute_sql(sql)

        max_length = 250
        tutorials = self.shorten_tutorials_text(tutorials, max_length)
        tutorials = self.make_tutorials_img_path(tutorials)

        return tutorials

    def make_tutorials_img_path(self, tutorials):

        new_tutorials = []
        for tutorial in tutorials:

            path = tutorial[3]
            if(path is not None):
                path = url_for('static', filename=path)
                tutorial = tutorial[:3] + (path,) + tutorial[4:]
                
            new_tutorials.append(tutorial)
            
        return new_tutorials


    def shorten_tutorials_text(self, tutorials, max_length):
        shorten_tutorials = []
        for tutorial in tutorials:
            shortened_string = tutorial[2][:max_length]
            tutorial = tutorial[:2] + (shortened_string + "...",) + tutorial[3:]
            shorten_tutorials.append(tutorial)

        return shorten_tutorials