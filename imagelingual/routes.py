from flask import render_template, send_from_directory, url_for, flash, redirect, request, jsonify
from imagelingual import app, db, bcrypt
from imagelingual.forms import RegistrationForm, LoginForm, SearchForm, DisplayForm
from imagelingual.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from imagelingual import constantpaths
from werkzeug.utils import secure_filename
import os
from imagelingual.abdominal_ultrasound_classification import extract_features, extract_features_pca, train_knn_model
from imagelingual.xray_classification import predict_class, CLASSNAMES,knn_model,VGG_model
import joblib
from imagelingual.kmeans import kmeans_segmentation
import numpy as np
import matplotlib.pyplot as plt
from imagelingual.translate import get_language_code, translate_image_text
UPLOAD_FOLDER = "imagelingual/static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SEGMENTED_IMAGES_FOLDER = 'imagelingual/static/segmented_images'
os.makedirs(SEGMENTED_IMAGES_FOLDER, exist_ok=True)  # Handle missing directory
app.config['SEGMENTED_IMAGES_FOLDER'] = SEGMENTED_IMAGES_FOLDER

# Function to save uploaded file
def save_uploaded_file(file,name):
    filename = secure_filename(file.filename)
    new_filename = name  # Specify your new file name here
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
    return "uploads/"+new_filename

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', bla=constantpaths.paths["GastroenterologyMRI"])

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, preferred_lang=form.preferred_lang.data, country=form.country.data)
        
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, row="row", col="col-mb-10")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route("/map", methods=['GET', 'POST'])
def map():
    return render_template('map-new.html', title='Explore')    

@app.route("/search", methods=['GET', 'POST'])
def search():
    return redirect("/explore")
    
@app.route("/about")
def about():
    return render_template("about.html", title="About")
    
@app.route("/gallery")
def gallery():
    limt = list(constantpaths.paths.values())
    likt = " ".join(limt)
    return render_template("gallery.html", title="Gallery", bla=likt)

@app.route("/explore", methods=['GET', 'POST'])
def explore():
    form = DisplayForm()
    if form.validate_on_submit():
        if form.field.data and form.modality.data:
            path = form.field.data + form.modality.data

            # Check if the folder exists
            return render_template('expolore.html', title='Results', form=form, bla=constantpaths.paths[path])
        else:
            # Handle case where both fields are not selected
            flash('Please select both Domain and Modality', 'danger')
    return render_template('expolore.html', form=form)

@app.route("/predict_abdominal_ultrasound", methods=['GET', 'POST'])
def predict_abdominal_ultrasound():
    if request.method == 'POST':
        # message = ""
        if 'file' not in request.files:
            return render_template('classification.html', message='No file part')
        
        file = request.files['file']

        if file.filename == '':
            return render_template('classification.html', message='No selected file')
        
        if file:
            try:
                # Save uploaded file
                new_filename = save_uploaded_file(file,"ultrasound.jpg")
                nn_model = "densenet121"
                model = joblib.load("imagelingual/abdominal_ultrasound_classification/densenet121")

                extract_features(nn_model, model)
                extract_features_pca(nn_model)

                predictions = train_knn_model(nn_model)
                # print("Predicted classes:", predictions)
                # for key,val in predictions.items():
                #     print(key, " == ", val, "\n")                
                return render_template('classification.html', message='Prediction result: {}'.format(predictions["temp"]),filename=new_filename)
            except Exception as e:
                return render_template('classification.html', message='Error occurred: {}'.format(e))
    return render_template('classification.html', message=" ")


@app.route('/predict_scan')
def upload_file():
    return render_template('upload.html')

@app.route('/clustering')
def clustering():
    return render_template('kmeanspage.html')

@app.route("/predict_cluster", methods=['POST'])
def predict_cluster():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('kmeanspage.html', message='No file part')

        file = request.files['file']

        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            return render_template('kmeanspage.html', message="No file selected")

        if file:
            # filename = secure_filename(file.filename)
            filename="clusterinput.jpg"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            original_image_url = '/uploads/' + filename

            # Perform image segmentation
            try:
                segmented_image = kmeans_segmentation(file_path)
            except Exception as e:
                return render_template('kmeanspage.html', message=f"Error processing file: {str(e)}")

            # Save the segmented image
            segmented_image_filename = secure_filename("segmented_" + filename)
            segmented_image_path = os.path.join(app.config['SEGMENTED_IMAGES_FOLDER'], segmented_image_filename)
            plt.imsave(segmented_image_path, segmented_image.astype(np.uint8))

            # Get the URL for segmented image
            segmented_image_url = "/segmented_images/" + segmented_image_filename

            # Render the result template with image URLs
            return render_template('kmeanspage.html', segmented_image=segmented_image_url, filename=original_image_url)

    # Handle other cases by redirecting to the upload page
    return render_template('kmeanspage.html', message='Error processing file', filename="")

@app.route('/segmented_images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['SEGMENTED_IMAGES_FOLDER'], filename)

@app.route('/predict_scan_result', methods=['POST'])
def predict_scan_result():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('upload.html', message='No file part')
        file = request.files['file']
        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            return render_template('upload.html', message="Image uploaded successfully",image_url = "/uploads/" + filename)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = "/uploads/" + filename 
            predicted_class = predict_class(file_path, knn_model, VGG_model)
            predicted_class=CLASSNAMES[int(str(predicted_class)[1])]
            # predicted_class="spleen"
            return render_template('upload.html', message=predicted_class, filename = image_url)
    return render_template('upload.html', message=" ")




@app.route("/describe_image", methods=['GET', 'POST'])
def describe_image():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('classification.html', message='No file part')
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return render_template('classification.html', message='No selected file')
        # If file is provided
        if file:
            try:
                # Save uploaded file
                new_filename = save_uploaded_file(file)
                nn_model = "densenet121"
                model = joblib.load("imagelingual/abdominal_ultrasound_classification/densenet121")

                extract_features(nn_model, model)
                extract_features_pca(nn_model)

                predictions = train_knn_model(nn_model)
                # print("Predicted classes:", predictions)
                # for key,val in predictions.items():
                #     print(key, " == ", val, "\n")                
                return render_template('classification.html', message='Prediction result: {}'.format(predictions["temp"]),filename=new_filename)
            except Exception as e:
                return render_template('classification.html', message='Error occurred: {}'.format(e))
    return render_template('classification.html', message='Upload an image')

@app.route('/translate_report')
def translate_report():
    return render_template('translate-upload.html')

@app.route('/translate_result', methods=['POST'])
def translate_result():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify(message="No file part")
        
        file = request.files['file']
        if file.filename == '':
            return jsonify(message="No selected file")

        language_name = request.form['language']
        language_code = get_language_code(language_name)
        if not language_code:
            return jsonify(message="Invalid language")

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    
        filename = "translateinput.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = UPLOAD_FOLDER + "/" + filename

        original_text, translated_text = translate_image_text(image_path, language_code)
        # original_text = "hello"
        # translated_text = "vanako"
        if not original_text:
            return jsonify(message="No text found in the image. Please try another image.")
        return render_template('translate_result.html', original_text=original_text, translated_text=translated_text)