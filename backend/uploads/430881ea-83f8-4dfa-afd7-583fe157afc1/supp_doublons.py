# src/supp_doublons.py

def supprimer_doublons_consecutifs(input_list):

    if not input_list:
        return []

    result_list = [input_list[0]] 

    # Parcourt la liste à partir du deuxième élément
    for item in input_list[1:]:
        # Compare l'élément actuel avec le DERNIER élément ajouté à result_list
        if item != result_list[-1]:
            result_list.append(item)
            
    return result_list