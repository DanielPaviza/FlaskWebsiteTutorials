
from flask import Flask, render_template, url_for, request, redirect
from controller import Controller
app = Flask(__name__)
c = Controller()

@app.route('/')
def show_home():
   tutorials = c.get_tutorials_short()
   
   return render_template('home.html', tutorials = tutorials)

@app.route('/tutorial/<int:postID>')
def show_tutorial(postID):
    tutorial, images = c.get_tutorial(postID)
    
    if(tutorial == []):
        return redirect(url_for('show_home'))
   
    return render_template('tutorial.html', tutorial = tutorial, images = images)

@app.route('/admin')
def show_administration():
    loggedIn = c.get_is_logged_in(app)
    print(f"loggedIn {loggedIn}")
    if(loggedIn is not True):
        return render_template('login.html')

    tutorials = c.get_administration_tutorials()
    return render_template('administrace.html', tutorials=tutorials)

@app.route('/new_password', methods=['POST', 'GET'])
def show_new_password():
    loggedIn = c.get_is_logged_in(app)
    if(loggedIn is not True):
        return redirect(url_for('show_administration'))

    if request.method == 'GET':
        return render_template('new_password.html')
    if request.method == "POST":
        password = request.form.get('password')
        c.update_password(password)

    return redirect(url_for('show_administration'))

@app.route('/new', methods=['POST', 'GET'])
def show_new():
    loggedIn = c.get_is_logged_in(app)
    if(loggedIn is not True):
        return redirect(url_for('show_administration'))

    if request.method == 'GET':
        return render_template('edit.html', new_form=True, images=[], tutorial=[])
    if request.method == "POST":
        nadpis = request.form.get('nadpis')
        text = request.form.get('text')
        uploaded_images = c.save_images(request.files.getlist('uploaded_images[]'))
        c.tutorial_save_new(nadpis, text, uploaded_images)

        return redirect(url_for('show_administration'))

@app.route('/edit/<int:postID>', methods=['POST', 'GET'])
def show_edit(postID):
    loggedIn = c.get_is_logged_in(app)
    if(loggedIn is not True):
        return redirect(url_for('show_administration'))
    
    if request.method == 'GET':
        tutorial, images = c.get_tutorial(postID, True)
        if(tutorial == []):
            return redirect(url_for('show_administration'))
        return render_template('edit.html', tutorial=tutorial, images=images, new_form=False)
    if request.method == "POST":
        nadpis = request.form.get('nadpis')
        text = request.form.get('text')
        image_urls = request.form.getlist('image_urls[]')
        uploaded_images = c.save_images(request.files.getlist('uploaded_images[]'))
        c.tutorial_edit_save(postID, nadpis, text, image_urls, uploaded_images)

        return redirect(url_for('show_administration'))
    
@app.route('/delete/<int:postID>')
def delete_tutorial(postID):
    loggedIn = c.get_is_logged_in(app)
    if(loggedIn is not True):
        return redirect(url_for('show_administration'))
    
    c.delete_tutorial(postID)

    return redirect(url_for('show_administration'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        c.login_attempt(app, name, password)

    return redirect(url_for('show_administration'))

if __name__ == '__main__':
   app.run()