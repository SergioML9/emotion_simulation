def init():

    global rooms_json
    #Example Map
    #Store the rooms
    rooms_json = [

    {'name':'Hall.1', 'entrance':'', 'type':'hall', 'conectedTo': {'U':'Hall.2', 'D':'outBuilding'}, 'measures': {'dx':3, 'dy':2}},
    {'name':'Hall.2', 'type':'hall', 'conectedTo': {'U':'Hall.3', 'R':'Lab1.1'}, 'measures': {'dx':3, 'dy':2.5}},
    {'name':'Hall.3', 'entrance':'', 'type':'hall', 'conectedTo': {'U':'Hall.4', 'R':'Lab2.1'}, 'measures': {'dx':3, 'dy':1}},
    {'name':'Hall.4', 'entrance':'', 'type':'hall', 'conectedTo': {'D':'Hall.3'}, 'measures': {'dx':3, 'dy':1}},

    {'name':'Lab1.1', 'type' : 'lab', 'measures': {'dx':1.85, 'dy':3.7}, 'conectedTo': {'L':'Hall.2', 'R':'Lab1.2'}},
    {'name':'Lab1.2', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab1.1', 'R':'Lab1.3', 'D':'Lab1.5'}},
    {'name':'Lab1.3', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab1.2', 'R':'Lab1.4'}},
    {'name':'Lab1.4', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab1.3'}},
    {'name':'Lab1.5', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'U':'Lab1.2', 'L':'Lab1.6', 'R':'Lab1.7'}},
    {'name':'Lab1.6', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'R':'Lab1.5'}},
    {'name':'Lab1.7', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab1.5', 'R':'Lab1.8'}},
    {'name':'Lab1.8', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab1.7'}},

    {'name':'Lab2.1', 'type' : 'lab', 'measures': {'dx':1.85, 'dy':3.7}, 'conectedTo': {'L':'Hall.3', 'R':'Lab2.2'}},
    {'name':'Lab2.2', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab2.1', 'R':'Lab2.3', 'U':'Lab2.5'}},
    {'name':'Lab2.3', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab2.2', 'R':'Lab2.4'}},
    {'name':'Lab2.4', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab2.3'}},
    {'name':'Lab2.5', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'U':'Lab2.2', 'L':'Lab2.6', 'R':'Lab2.7'}},
    {'name':'Lab2.6', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'R':'Lab2.5'}},
    {'name':'Lab2.7', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab2.5', 'R':'Lab2.8'}},
    {'name':'Lab2.8', 'type' : 'lab', 'measures': {'dx':1, 'dy':3.7}, 'conectedTo': {'L':'Lab2.7'}},


    {'name':'outBuilding', 'type' : 'out'}

    ]