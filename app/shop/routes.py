from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

#
#
# BASED ON IG ROUTES.PY (everything besides showCart and the admin createProduct routes)
#
#


shop = Blueprint('shop', __name__, template_folder='shop_templates')

from app.models import db, Product, Cart
from .forms import CreateProductForm

@shop.route('/products')
@login_required
def allProducts():
    products = Product.query.all()
    return render_template('shop.html', products=products)

@shop.route('/products/<int:product_id>')
@login_required
def individualProduct(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return redirect(url_for('shop.allProducts'))
    return render_template('individual_product.html', product = product)

# CART FUNCTIONALITY
@shop.route('/cart')
@login_required
def showCart():
    cart = Cart.query.filter_by(user_id=current_user.id)
    count = {}
    for item in cart:
        count[item.product_id] = count.get(item.product_id, 0) + 1 # counting with the .get method
    
    cart_products = []
    for product_id in count:
        product_info = Product.query.filter_by(id=product_id).first().to_dict()
        product_info["quantity"] = count[product_id]
        product_info['subtotal'] = product_info['quantity'] * product_info['price']
        cart_products.append(product_info)

    return render_template('show_cart.html', cart = cart_products)


@shop.route('/cart/add/<int:product_id>')
def addToCart(product_id):
    cart_item = Cart(current_user.id, product_id)
    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('shop.allProducts'))

@shop.route('/cart/add', methods=["POST"])
def addToCart2():
    product_id = request.form.to_dict()['product_id']
    cart_item = Cart(current_user.id, product_id)
    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('shop.individualProduct', product_id=product_id))



# ADMIN CREATE PRODUCT PAGE
@shop.route('/products/create')
@login_required
def createProduct():
    if current_user.is_admin:
        form = CreateProductForm()
        if request.method == "POST":
            if form.validate():
                product_name = form.product_name.data
                img_url = form.img_url.data
                description = form.description.data
                price = form.price.data

                product = Product(product_name, img_url, description, price)

                db.session.add(product)
                db.session.commit()   

                return redirect(url_for('shop.createProduct'))         

        return render_template('create_product.html', form = form)
    else:
        return redirect(url_for('shop.allProducts'))   




# 
#  
# API ROUTES
# 
# 
#  
from app.apiauthhelper import token_required

@shop.route('/api/products')
def apiProducts():
    products = Product.query.all()
    return {
        "status": "ok",
        "total_results": len(products),
        'products': [p.to_dict() for p in products]
    }

@shop.route('/api/products/<int:product_id>')
def apiSingleProduct(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return {
            'status': 'not ok',
            'total_results': 0,
        }
    return {
        'status': 'ok',
        'total_results': 1,
        'product': product.to_dict()
        }


@shop.route('/api/cart/get')
@token_required
def getCartAPI(user):
    cart = Cart.query.filter_by(user_id=user.id)
    myCart = [Product.query.filter_by(id=item.product_id).first().to_dict() for item in cart]
    return {
        'status': 'ok',
        'cart': myCart
    }

@shop.route('/api/cart/add', methods=["POST"])
@token_required
def addToCartAPI(user):
    data = request.json

    product_id = data['product_id']

    newCartItem = Cart(user.id, product_id)
    
    db.session.add(newCartItem)
    db.session.commit()

    return {
        'status': 'ok',
        'message': "Successfully added item to cart!"
    }

@shop.route('/api/cart/remove', methods=["POST"])
@token_required
def removeFromCartAPI(user):
    data = request.json
    
    product_id = data['product_id']

    cartItem = Cart.query.filter_by(user_id=user.id).filter_by(product_id=product_id).first()

    if cartItem:
        db.session.delete(cartItem)
        db.session.commit()
        return {
            'status': 'ok',
            'message': "Successfully removed item from cart."
        }
    return {
        'status': 'not ok',
        'message': 'That item does not exists in your cart.'
    }

import stripe
import os
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@shop.route('/api/stripe/create-checkout-session', methods=["POST"])
def createCheckoutSession():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1JpbJLDTfh3G5wtDtecdGTdJ',
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url='http://localhost:3000/' + '?success=true',
            cancel_url='http://localhost:3000/stripe/shop' + '?canceled=true',
        )

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)