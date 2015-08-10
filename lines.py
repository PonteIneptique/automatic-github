# Import command line informations
from sys import argv
import os
# Import required library
from lxml import etree
import requests
# Import library for CTS 
import MyCapytain.resources.texts.tei
import common

def transform_lines(url):
    """ Download an xml file and add line numbering and ctsize it

    :param url: A Perseus Github Raw address
    :type url: str
    :param urn: The urn of the text
    :type urn: str
    :param lang: Iso code for lang
    :type lang: str

    """

    lang, urn, target, parsed = common.parse(url)

    """
        Change div1 to div, moving their @type to @subtype 
    """    

    # We find the lines
    lines = parsed.xpath("//l")
    # We set a counter
    i = 1
    # We loop over lines
    for line in lines: 
        # We set the @n attribute using str(i) because .set(_,_) accepts only string
        line.set("n", str(i))
        # We increment the counter
        i += 1

    # We find divs called div1 or div2. Mind the |// !
    divs = parsed.xpath("//div1|//div2")
    # We loop over them
    for div in divs:
        # We change it's tag
        div.tag = "div"

    citations = list()

    """
        Add refsDecl information for CTS
    """
    citations.append(
        MyCapytain.resources.texts.tei.Citation(
            name="line", 
            refsDecl="/tei:TEI/tei:text/tei:body/div[@type='edition']//tei:l[@n='$1']"
        )
    )

    try:
        common.write_and_clean(urn, lang, parsed, citations, target)
    except:
        print(urn + " failed")


if __name__ == '__main__':
    transform_lines(*tuple(argv[1:]))