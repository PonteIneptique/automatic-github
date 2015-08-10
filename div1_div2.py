""" Div1 / Div2 old Perseus data to Div/Div + RefsDecl converter

Authors : Aaron Plasek, Ariane Pinche, Mark Moll, Ana Migowski
Adaptation : Thibault Clérice

Python 3 Script

Description :
    This software will transform old Perseus files into CTS compliant files if their structure is div1/div2 based

    Example of file needing this : 
        https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/598aea1eb719be1709f720839e4428a087e43ad6/data/tlg0612/tlg001/tlg0612.tlg001.perseus-grc1.xml
    Example of output :

Syntax :

    python3 div1_div2.py [Url of the original file on raw.github] [URN] [lang]


Requires :
    - requests
    - lxml
    - MyCapytain

    pip install ...

"""
# Import command line informations
from sys import argv
# Import required library
from lxml import etree
import requests
# Import library for CTS 
import MyCapytain.resources.texts.tei

import common

def transform(url):
    """ Download an xml file and add line numbering and ctsize it

    :param url: A Perseus Github Raw address
    :type url: str
    :param urn: The urn of the text
    :type urn: str
    :param lang: Iso code for lang
    :type lang: str

    """


    lang, urn, target, parsed = common.parse(url)

    if "grc" not in urn and "lat" not in urn:
        type_text = "translation"
    else:
        type_text = "edition"

    # We find divs called div1
    div1_group = parsed.xpath("//div1")
    i = 1
    for div1 in div1_group:
        # We change it's tag
        div1.tag = "div"
        # To deal with different subtype, we get the former attribute value of type and put it to subtype
        div1_subtype = div1.get("type")
        div1.set("subtype", div1_subtype)
        div1.set("type", "textpart")

        if "n" not in dict(div1.attrib):
            div1.set("n", str(i))
        i += 1
                
        
    """
        Change div2 to div, moving their @type to @subtype 
    """    
    # We find divs called div2
    i = 1
    div2_group = parsed.xpath("//div2")
    for div2 in div2_group:
        # We change it's tag
        div2.tag = "div"
        # To deal with different subtype, we get the former attribute value of type and put it to subtype
        div2_subtype = div2.get("type")
        div2.set("subtype", div2_subtype)
        div2.set("type", "textpart")

        if "n" not in dict(div2.attrib):
            div2.set("n", str(i))
        i += 1
        
    """
        Change div3 to div, moving their @type to @subtype 
    """    
    # We find divs called div2
    i = 1
    div3_group = parsed.xpath("//div3")
    for div3 in div3_group:
        # We change it's tag
        div3.tag = "div"
        # To deal with different subtype, we get the former attribute value of type and put it to subtype
        div3_subtype = div3.get("type")
        div3.set("subtype", div3_subtype)
        div3.set("type", "textpart")

        if "n" not in dict(div3.attrib):
            div3.set("n", str(i))
        i += 1

    """
        Add refsDecl information for CTS
    """
    citations = []
    # Used only if div3 > 0
    if len(div3_group) > 0:
        citations.append(
            MyCapytain.resources.texts.tei.Citation(
                name=div3_subtype, 
                refsDecl="/tei:TEI/tei:text/tei:body/div[@type='"+type_text+"']/div[@n='$1']/div[@n='$2']/div[@n='$3']"
            )
        )
    # Used only if div2 > 0
    if len(div2_group) > 0:
        citations.append(
            MyCapytain.resources.texts.tei.Citation(
                name=div2_subtype, 
                refsDecl="/tei:TEI/tei:text/tei:body/div[@type='"+type_text+"']/div[@n='$1']/div[@n='$2']"
            )
        )
    citations.append(
        MyCapytain.resources.texts.tei.Citation(
            name=div1_subtype, 
            refsDecl="/tei:TEI/tei:text/tei:body/div[@type='"+type_text+"']/div[@n='$1']"
        )
    )

    try:
        common.write_and_clean(urn, lang, parsed, citations, target)   
    except Exception as E:
        print(urn + " failed")
        print(E)


if __name__ == '__main__':
    transform(*tuple(argv[1:]))