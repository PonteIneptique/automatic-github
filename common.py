"""
    Useful functions for Github/TEI interactions
"""
import os 

import requests
from lxml import etree

import cts

with open("utils/p4p5.xslt") as xsl:
    xslt_file = etree.parse(xsl)

P4P5 = etree.XSLT(xslt_file)

def parse(url):
    """ Parse the url and retrieve necessary informations

    :returns: lang, urn, target, parsed
    """
    s_url = url.split("/")
    ns = [e for e in s_url if "canonical-" in e][0].split("-")[-1]
    f = ".".join(s_url[-1].split(".")[:-1])

    textgroup, work, donotcate = tuple(f.split("."))
    lang = f.split("-")[-1][0:3]
    urn = "urn:cts:{0}:{1}".format(ns, f)

    target = "output/canonical-{namespace}/data/{group}/{work}/{file}".format(namespace=ns, group=textgroup, work=work, file=s_url[-1])

    """
        Downloading the resource 
    """
    # Download the resource
    response = requests.get(url)
    # Ensure there was no errors
    response.raise_for_status()

    # Get the file name by splitting the url
    filename = url.split("/")[-1]

    """ 
        Caching the resource 
    """

    os.makedirs("cache", exist_ok=True)
    # Save the original response
    with open("cache/original-"+filename, 'w') as f:
        # Don't forget to write the reponse.text and not response itself
        read_data = f.write(response.text)

    # Open it and parse it
    with open("cache/original-"+filename) as f:
        # We use the etree.parse property
        parsed = etree.parse(f)

    return lang, urn, target, parsed


def write_and_clean(urn, lang, parsed, citations,target):
    """ Write and clean a TEI-P4 file

    :param parsed: lxml object representing the file
    :type parsed:
    :param citations: List of Node representing cRefPattern
    :param target:
    :type target: basestring

    """

    os.makedirs("cache", exist_ok=True)

    """
        Change TEI.2 tag to TEI 
    """
    # We change the main tag
    TEI = parsed.getroot()
    # We change the root tag to TEI
    TEI.tag = "TEI"
    # We change the main tag
    TEI = parsed.getroot()

    """
        Moving every children of //body into a new div with a @n attribute
    """
    body = parsed.xpath("//body")[0]
    # Get its children
    child_body = body.getchildren()

    # For each child of body, remove it from body
    for child in child_body:
        body.remove(child)

    # Create a new div with the informations
    div = etree.Element(
        "div",
        attrib = { 
            "type":"edition",
            "n": urn,
            "{http://www.w3.org/XML/1998/namespace}lang" : lang
        }
    )

    # Add the full list of children of body to the newly created div
    div.extend(child_body)
    # Add this new div in body
    body.append(div)

    # Add them to the current encodingDesc
    refsDecl = """<tei:refsDecl n="CTS" xmlns:tei="http://www.tei-c.org/ns/1.0">\n""" + "\n".join([str(citation) for citation in citations]) + """\n</tei:refsDecl>"""
    # Parse it
    refsDecl = etree.fromstring(refsDecl)
    # Find encodingDesc
    encodingDesc = parsed.xpath("//encodingDesc")[0]
    encodingDesc.append(refsDecl)

    """
        Search for old //encodingDesc/refsDecl and refsDecl/state and correct them
    """
    refsDecls = parsed.xpath("//encodingDesc/refsDecl[@doctype]")
    for refsDecl in refsDecls:
        refsDecl.set("n", refsDecl.get("doctype"))
        del refsDecl.attrib["doctype"]

    states = parsed.xpath("//encodingDesc/refsDecl/state")
    for state in states:
        state.tag = "refState"

    """
        Change language@id to ident
    """
    languages = parsed.xpath("//langUsage/language[@id]") + parsed.xpath("//langUsage/lang[@id]")
    for lang in languages:
        lang.set("ident", lang.attrib["id"])
        del lang.attrib["id"]

    """
        Change pb@id to pb@n
    """
    pbs = parsed.xpath("//pb[@id]")
    for pb in pbs:
        pb.set("n", pb.attrib["id"])
        del pb.attrib["id"]

    """
        Clean keyboarding/p
    """
    ps = parsed.xpath("//sourceDesc/p")
    for p in ps:
        p.getparent().remove(p)

    """
        Clear attributes of text and body
    """
    body_text = parsed.xpath("//body") + parsed.xpath("//text")
    for tag in body_text:
        for key in tag.attrib:
            del tag.attrib[key]


    """
        Clear refsDecl/step
    """
    refsdecls_step = parsed.xpath("//refsDecl/step/parent::refsDecl")
    for step_parent in refsdecls_step:
        step_parent.getparent().remove(step_parent)

    """
        Clear refsDecl/step
    """
    refsdecls_step = parsed.xpath("//refsDecl/step/parent::refsDecl")
    for step_parent in refsdecls_step:
        step_parent.getparent().remove(step_parent)

    """
        Fix anchored
    """
    anchoreds = parsed.xpath("//*[@anchored='yes']")
    for anchored in anchoreds:
        anchored.set("anchored", "true")

    # Convert to xml
    """ 
        Create a new document so we can have tei namespace 
    """
    # And now some other CTS Magic
    New_Root = etree.Element(
        "{http://www.tei-c.org/ns/1.0}TEI",
        nsmap = { None : "http://www.tei-c.org/ns/1.0" } # Creating a new element allows us to use a default namespace
    )
    New_Root.text = "\n"
    # Add children of old root to New_Root
    New_Root.extend(TEI.getchildren())

    # We create a new document
    New_Doc = etree.ElementTree(New_Root)
    # And now some other CTS Magic
    
    New_Doc = P4P5(New_Doc)

    # save xml
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open (target, "w") as xmlfile:
        xmlfile.write("""<?xml version="1.0" encoding="UTF-8"?>\n"""+etree.tostring(New_Doc, encoding=str))

    # And now we write cts informations
    cts.cts_metadata(urn)

