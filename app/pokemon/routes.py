from flask import Blueprint, redirect, render_template, request, url_for
import requests as r

pokemon = Blueprint('pokemon', __name__, template_folder="pokemon_templates")


@pokemon.route('/pokemon', methods=["POST"])
def myPokemon():
    name = request.form.to_dict()['name']
    data = r.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
    if data.status_code == 200: # status code 200 means success
        my_data = data.json()
        abilities = my_data['abilities']
        my_abilities = []
        for item in abilities:
            my_abilities.append((item['ability']['name']))
        my_img = my_data['sprites']['front_default']
        return render_template('pokemon.html', abilities=my_abilities, img_url=my_img, name=name)
    return redirect(url_for('home'))