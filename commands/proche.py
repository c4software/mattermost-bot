from commands.libs.decorators import register_as_command
from tools.rest import callrest
import logging, json
from tools.libs import is_telegram, get_username, username_or_channel
from commands.libs.context import mark_for_awaiting_response


def search_arround_me(query):
    type_recherche = ["park", "forest", "castle"]
    type_recherche_translate = {"park": "Parc", "forest": "Forêt", "castle": "Château"}
    retour_string = "Voilà la liste des lieux autours de vous :\n"
    no_result = True

    for rech in type_recherche:
        params = {"accept-language": "fr", "format": "json", "limit": 5, "addressdetails": 1,
                  "q": "[{1}] {0}".format(query, rech)}
        data = callrest(domain="nominatim.openstreetmap.org", ssl=True, params=params, path="/search",
                        type="GET")[2]
        data = json.loads(data)

        retour = []
        for adress in data:
            try:
                # Récupération de la ville / village / code postal
                if "city" in adress["address"]:  # pragma: no cover
                    city = adress["address"]["city"]
                elif "town" in adress["address"]:  # pragma: no cover
                    city = adress["address"]["town"]
                elif "village" in adress["address"]:  # pragma: no cover
                    city = adress["address"]["village"]
                else:  # pragma: no cover
                    city = adress["address"]["postcode"]

                first_element = list(adress["address"].values())[0]
                if rech in adress["address"]:
                    first_element = adress["address"][rech]

                # Récupération du « premier élément » comme Nom
                retour.append("{0}, {1} [Voir](https://www.google.fr/maps/@{2},{3},18z)".format(first_element, city,
                                                                                                adress["lat"],
                                                                                                adress["lon"]))
            except Exception as e:  # pragma: no cover
                raise (e)

        if retour:
            no_result = False
            retour_string = "{0} \n {1} : ".format(retour_string, type_recherche_translate[rech])
            retour_string = retour_string + "\n - " + "\n - ".join(retour) + " \n "

    if not no_result:
        return retour_string
    else:  # pragma: no cover
        return "Désolé, aucun résultat autour de votre position."


@register_as_command("proche", "Recherche les lieux d’interêts autour de votre position", "Geo")
def cmd_do_proche(msg):
    if is_telegram(msg) and msg["telegram"]["update"].message.location:  # pragma: no cover
        user_location = msg["telegram"]["update"].message.location
        return search_arround_me("{0}, {1}".format(user_location.latitude, user_location.longitude))
    elif msg["query"] != "":
        return search_arround_me(msg["query"])
    else:  # pragma: no cover
        mark_for_awaiting_response(username_or_channel(msg), "proche")
        return "Pour utiliser la recherche proche merci de m’indiquer une position GPS. Ex: 48.802,2.025"
