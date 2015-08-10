# Import command line informations
from sys import argv
import os
# Import required library
from lxml import etree
import requests

import MyCapytain.common.reference
import MyCapytain.common.utils


def cts_metadata(urn):
    """ Retrieve metadata from URN using catalog atom feed """
    urn = MyCapytain.common.reference.URN(urn)

    group_file = "output/canonical-{namespace}/data/{group}/__cts__.xml".format(namespace=urn[2], group=urn[3])
    work_file = "output/canonical-{namespace}/data/{group}/{work}/__cts__.xml".format(namespace=urn[2], group=urn[3], work=urn[4])
    
    # Make sure dir exists
    os.makedirs(os.path.dirname(work_file), exist_ok=True)

    url = "http://data.perseus.org/catalog/{urn}/atom".format(urn=str(urn))
    atom = requests.get(url)
    atom.raise_for_status()

    with open("cache/"+urn[3]+"."+urn[4]+"."+urn[5]+".atom", "w") as atom_write:
        atom_write.write(atom.text)

    with open("cache/"+urn[3]+"."+urn[4]+"."+urn[5]+".atom") as atom:
        xml = MyCapytain.common.utils.xmlparser(atom)

    ns = { "cts" : "http://chs.harvard.edu/xmlns/cts/ti", "ti": "http://chs.harvard.edu/xmlns/cts" }

    etree.register_namespace('ti', 'http://chs.harvard.edu/xmlns/cts')

    textgroup = xml.xpath("//cts:textgroup[@urn='"+urn["textgroup"]+"']", namespaces=ns)[0]
    # Change namespaces
    textgroup.tag = "{http://chs.harvard.edu/xmlns/cts}textgroup"
    for node in textgroup.xpath(".//*"):
        node.tag = "{http://chs.harvard.edu/xmlns/cts}"+node.tag.split("}")[-1]


    work = textgroup.xpath("./ti:work", namespaces=ns)[0]
    textgroup.remove(work)

    work.set("groupUrn", urn["textgroup"])

    ed_tr = work.xpath(".//ti:edition|ti:translation", namespaces=ns)[0]
    ed_tr.set("workUrn", urn["work"])

    with open(group_file, "w") as g:
        g.write(etree.tostring(textgroup, encoding=str))

    with open(work_file, "w") as w:
        w.write(etree.tostring(work, encoding=str))

if __name__ == '__main__':
    cts_metadata(argv[1])