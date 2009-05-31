"""
Image processing utilities
"""

import os

import burst
if burst.running_on_nao():
    base='/opt/naoqi/'
else:
    base=os.environ['AL_DIR']
TABLE = os.path.join(base, 'modules/etc/table.mtb')
WHICH = os.path.join(base, 'modules/etc/whichtable.txt')
which = 'undefined'
if not os.path.exists(WHICH):
    with open(WHICH) as fd:
        which=fd.read().strip()

if (('webots' in which and burst.connecting_to_nao()) or
    ('webots' not in which and burst.connecting_to_webots())):
    print "WARNING: you are using the incorrect color table:"
    print "which = %s" % which

def get_nao_mtb():
    with open(TABLE) as fd:
        table = fd.read()
    return table

def return_index_to_rgb():
    """ For use with imops.write_index_to_rgb
    for usage with the debug imops.thresholded_to_rgb
    """
    colors = [
        ("GREY",          (127, 127, 127)),
        ("WHITE",         (0, 0, 0)),
        ("GREEN",         (0, 0, 0)),
        ("BLUE",          (0, 0, 0)),
        ("YELLOW",        (0, 0, 0)),
        ("ORANGE",        (0, 0, 0)),
        ("YELLOWWHITE",   (0, 0, 0)),
        ("BLUEGREEN",     (0, 0, 0)),
        ("ORANGERED",     (0, 0, 0)),
        ("ORANGEYELLOW",  (0, 0, 0)),
        ("RED",           (0, 0, 0)),
        ("NAVY",          (0, 0, 0)),
        ("BLACK",         (0, 0, 0)),
        ("PINK",          (0, 0, 0)),
        ("SHADOW",        (0, 0, 0)),
        ("CYAN",          (0, 0, 0)),
        ("DARK_TURQUOISE", (0, 0, 0)),
        ("LAWN_GREEN",    (0, 0, 0)),
        ("PALE_GREEN",    (0, 0, 0)),
        ("BROWN",         (0, 0, 0)),
        ("SEA_GREEN",     (0, 0, 0)),
        ("ROYAL_BLUE",    (0, 0, 0)),
        ("POWDER_BLUE",   (0, 0, 0)),
        ("MEDIUM_PURPLE", (0, 0, 0)),
        ("MAROON",        (0, 0, 0)),
        ("LIGHT_SKY_BLUE", (0, 0, 0)),
        ("MAGENTA",       (0, 0, 0)),
        ("PURPLE",        (0, 0, 0)),
    ]

