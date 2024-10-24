import json

#Simple IO for parsing jsons with data, obviously there is a lot more that will need to be done but
#this will serve as a baseline to seeing how we will want to go about creating and editing our data
#throughout the project

with open('test.json', 'r') as file:    #Opens the test.son file to read
    data = json.load(file)  #Creates temorary storage for the json file into data object
print(f"Agent ID: {data['Agent']['ID']}")   #Reads from the json and gives us the agent ID

data['Agent']['Generation'] = "5"   #Replaces generation 2 with 5
data['Agent']['location']['x'] = "45.2" #Replaces x data with 45.2
data['Agent']['location']['y'] = "50.1" #Replaces y data with 50.1


del data['Agent']['fitness'][0]['Test deletion']  #Deleting data from json, must be a number if from a list
data['Agent']['fitness'][0]['Fitness2'] = "A predetermined fitness score"  #Importing data to the front of the list

with open('newData.json', 'w') as new_json: #writes the contents to a new json file from the old/edited
    json.dump(data, new_json, indent=4) #Indent 4 allows for better standardization of the code format
