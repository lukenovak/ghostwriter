import json
import sqlite3

# the dataset we chose to use is in an sqlite db, so we want to convert it to a json
dbconn = sqlite3.connect("./db/billboard-200.db")
cur = dbconn.cursor()
master_json = []

cur.execute("SELECT artist, album_id, song FROM acoustic_features;")

# build a simple json object with the parameters we want
for row in cur:
    row_json = {}
    if row[0] == "Soundtrack" or row[0] == "Various Artists" or row[0] == "Original Cast":
        continue
    row_json["artist"] = row[0]
    row_json["album_id"] = row[1]
    row_json["song"] = row[2]

    master_json.append(row_json)

raw_json = json.dumps(master_json)

# write the raw json to a json file
json_file = open("./db/songs.json", "+w")
json_file.write(raw_json)
json_file.close()

print("completed conversion from db to json!")