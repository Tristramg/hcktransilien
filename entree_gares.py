#!/usr/bin/env python
from xml.etree.ElementTree import ElementTree, fromstring
from pyproj import Proj, transform
from urllib.request import urlopen

def get_sa(x,y):
    request = "http://ms.api.transilien.com/?action=proximitylist&x={0}&y={1}distance=1000&type=stoparea".format(x,y)
    response = urlopen(request).read()
    tree = fromstring(response)
    sa = tree.find('ProximityList/Proximity/StopArea')
    if sa == None :
        return "Unknown"
    else:
        return sa.attrib["StopAreaExternalCode"]


request = "http://api.openstreetmap.fr/xapi/xapi?node[bbox=2,48.5,3,49.5][railway=subway_entrance]"
response = urlopen(request).read()
tree = fromstring(response)

es = []

lambert2e = Proj(init='epsg:27572')
wgs84 = Proj(init='epsg:4326')
ignored = 0
for node in tree.iter("node") :
    cur = {}
    cur["lon"] = float(node.attrib["lon"])
    cur["lat"] = float(node.attrib["lat"])
    cur["ufr"] = "unknown"
    cur["name"] = ""
    cur["ref"] = ""
    cur["x"], cur["y"] = transform(wgs84, lambert2e, cur["lon"], cur["lat"])
    cur["saec"] = get_sa(int(cur["x"]), int(cur["y"]))
    for tag in node.iter("tag") :
        k = tag.attrib["k"]
        v = tag.attrib["v"]
        if k == "name" :
            cur["name"] = v
        if k == "ref" :
            cur["ref"] = v
        if k == "wheelchair" :
            cur["ufr"] = v
    if cur["saec"] != "Unknown" :
        es.append(cur)
    else:
        ignored += 1

print("Nombre d'entrées-sorties trouvées : ", len(es))
print("Nombre d'entrées-sorties ignorées : ", ignored)
for entree in es:
    print("Code gare {saec}, nom : {name}, accessibilité : {ufr}, code : {ref}".format(**entree))


