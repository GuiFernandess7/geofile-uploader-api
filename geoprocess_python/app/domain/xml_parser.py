import xml.sax

class KMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.current_tag = ""
        self.current_attr = ""
        self.current_text = ""
        self.current_placemark = {"dados": {}}
        self.placemarks = []

    def startElement(self, tag, attributes):
        self.current_tag = tag
        self.current_text = ""
        if tag == "Placemark":
            self.current_placemark = {}
        elif tag == "SimpleData":
            self.current_attr = attributes.get("name", "")

    def characters(self, content):
        if self.current_tag in ["name", "SimpleData"]:
            self.current_text += content.strip()

    def endElement(self, tag):
        if tag == "name":
            self.current_placemark["Nome"] = self.current_text
        elif tag == "SimpleData" and self.current_attr:
            self.current_placemark[self.current_attr] = self.current_text
        #elif tag == "coordinates":
        #    self.current_placemark["coordenadas"] = self.current_text
        elif tag == "Placemark":
            self.placemarks.append(self.current_placemark)
        self.current_tag = ""
