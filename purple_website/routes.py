import secrets
import os
from PIL import Image
from purple_website import app,db,bcrypt,mail
from flask import render_template,flash,redirect,url_for,request,abort
from purple_website.form import RegisterForm,LoginForm,RequestResetForm,ProductForm,ResetPasswordForm,SellerRegistrationForm,AddCartForm
from purple_website.models import userstable,productstable,adminstable,sellertable
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
from flask import session,jsonify
from flask_wtf.csrf import generate_csrf


@app.route("/")
def home():
    if 'cart' not in session:
        session['cart'] = []
    return render_template("index.html")



@app.route("/categories", methods=["GET", "POST"])
def categories():
    products = productstable.query.all()
    form = AddCartForm()    
    if form.validate_on_submit():
        product_id = form.product_id.data
        product_data= productstable.query.get(product_id) 
        flash(f"{session['cart']}","success")
    return render_template("categories.html", products=products, form=form)



@app.route("/addtocart/<int:product_id>",methods=['GET','POST'])
def addtocart(product_id):
    product_data= productstable.query.get(product_id) 
    product_dict= {"product_id":product_data.id,"productname":product_data.name,"price":product_data.price,}
    session['cart'].append(product_dict)
    flash(f"{session['cart']}","success")
    return redirect(url_for('categories'))

@app.route("/removecart/<int:product_id>",methods=['GET','POST'])
def removecart(product_id):
    # Check if the cart exists in the session
    if 'cart' in session:
        # Find the product in the cart and remove it
        session['cart'] = [item for item in session['cart'] if item['productname'] != productstable.query.get(product_id).name]
        
        # Flash a success message
        flash(f"Product with ID {product_id} has been removed from your cart.", "success")
    else:
        flash("Your cart is empty.", "warning")
    
    return redirect(url_for('categories')) 
 
@app.route("/clearcart")
def clearcart():
    # Check if the cart exists in the session
    if 'cart' in session:
        session.pop('cart', None)  # Clear the cart from the session
        flash("Your cart has been cleared.", "success")
    else:
        flash("Your cart is already empty.", "warning")
    
    return redirect(url_for('categories')) 


@app.route("/getcart")
def get_cart():
    # Check if the cart exists in the session
    cart = session.get('cart', [])
    return jsonify(cart)

@app.route("/single")
def single():
    return render_template("single.html")

@app.route("/text-book")
def textbook():
    return render_template("text-book.html")
@app.route("/contact")
def contact():
    return render_template("contact.html")
@app.route("/book")
def book():
    return render_template("book.html")


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/product_images', picture_fn)

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/add_product', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)  # Assume this function saves the image and returns the filename

            # Get the current user's seller_id
            seller = sellertable.query.filter_by(user_id=current_user.id).first()
            if seller:
                new_product = productstable(
                    name=form.name.data,
                    price=form.price.data,
                    quantity=form.quantity.data,
                    image_file=picture_file,
                    seller_id=seller.id  # Use the seller's ID
                )

                # Add to the database
                db.session.add(new_product)
                db.session.commit()

                flash('Product added successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('No seller found for this user.', 'error')
        else:
            flash('No image file selected!', 'error')

    return render_template('add_product.html', form=form)

@app.route('/dashboard')
@login_required  # Ensure the user is logged in
def dashboard():
    # Get the seller associated with the current user
    seller = sellertable.query.filter_by(user_id=current_user.id).first()
    
    # Fetch products associated with this seller, or an empty list if no seller is found
    if seller:
        products = productstable.query.filter_by(seller_id=seller.id).all()
    else:
        products = []  # No products if there's no associated seller

    return render_template("dashboard.html", products=products)


@app.route('/register_seller', methods=['GET', 'POST'])
def register_seller():
    form = SellerRegistrationForm()  # Create an instance of your form
    if form.validate_on_submit():  # Validate the form
        # Create a new seller record
        new_seller = sellertable(
            user_id=current_user.id,  # Assuming the user is logged in
            storename=form.store_name.data,
            storedescription=form.store_description.data
        )
        db.session.add(new_seller)  # Add to the session
        
        # Update the user status in usertable
        user = userstable.query.get(current_user.id)  # Get the current user
        if user:
            user.designation = 'seller'  # Update the designation or status
            db.session.commit()  # Commit the changes to usertable
        
        db.session.commit()  # Commit the session to save the new seller
        flash('Your seller account has been created!', 'success')  # Success message
        return redirect(url_for('dashboard'))  # Redirect to a desired page after registration

    return render_template('makeseller.html', form=form)  # Render the template with the form

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


    

@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        print("Form validation successful!")  # Add a print statement to check if form validation is successful
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        userdata = userstable(username=form.username.data.lower(), email=form.email.data.lower(), password=hashed)
        db.session.add(userdata)
        db.session.commit()
        flash("Your account is created and you can login now!", 'success')
        return redirect(url_for('login'))  
    else:
        print("Form validation failed!") 
    return render_template("register.html", title="Register", form=form)



@app.route("/login",methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
            userdata=userstable.query.filter_by(email=form.email.data.lower()).first()
            if(userdata and bcrypt.check_password_hash(userdata.password,form.password.data)):
                 login_user(userdata,remember=form.remember.data)
                 next_page=request.args.get('next')
                 return redirect(next_page) if next_page else  redirect(url_for("home"))
            elif(userdata):
                flash("check your password","danger")
            else:     
                flash('Wrong Email Entered',"danger")
    return render_template("login.html",title="Login",form=form)


    

def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',sender="saboorabdul627@gmail.com",recipients=[user.email])
    msg.body=f''' to Rese your password visit the following link :
http://127.0.0.1:5000/{url_for('reset_token',token=token,external=True)}   
if you did not request reset then ignore this email'''
    mail.send(msg)


@app.route("/reset_password",methods=['POST','GET'])
def reset_request():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user_data=userstable.query.filter_by(email=form.email.data).first()
        send_reset_email(user_data)
        flash("check your email to reset password !","info")
        return redirect(url_for('login'))
    return render_template('resetrequest.html',form=form)

@app.route("/reset_password/<token>",methods=['POST','GET'])
def reset_token(token):
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    user_data=userstable.verify_reset_token(token)
    if user_data is None:
        flash("That is an Inavalid token the link is Expired ",'warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        print("Form validation successful!")  # Add a print statement to check if form validation is successful
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user_data.password=hashed
        db.session.commit()
        flash("Your Password is reset !", 'success')
        return redirect(url_for('login')) 
    return render_template('resetpassword.html',form=form)
