""" Generate PDF bingo cards."""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
import random
import textwrap
from reportlab.lib import utils
import copy
import random

""" TO DO: use better fonts.
from reportlab.pdfbase.ttfonts import TTFont

Then can register TTF with
pdfmetrics.registerFont(TTFont('Vera','Vera.ttf'))
"""


def set_canvas(filename):
    """Take a filename and initiate a canvas object that we can draw to."""
    this_canvas = canvas.Canvas(filename)
    this_canvas.setPageSize(A4)
    # Was setting font here, turns out to be easier to set on draw strings.
    return this_canvas


def get_box_width(n_across=5, page_size=A4, page_margin=1 * inch):
    """For any word, and any page dimensions, figure out how wide your boxes can
    be to accomodate the word and fill the page.
    !!! FIX: If I was clever, I'd set the base font size here, too.
    """
    #page_margin = page_margin * inch
    available_width = page_size[0] - page_margin * 2
    box_width = available_width / n_across
    return box_width


def get_coords(n_across, n_down):
    """
    Take some word and get a list of tuples of x,y coordinates for each letter,
    and two list, one of x values, another of y values, that can be used to draw
    a grid
    """
    box = get_box_width(n_across)
    # Start x so this is centered
    # x is where the first letter gets drawn
    # so the gutter is 0.5 boxes away.
    x_coordinate = 0.5 * box + (A4[0] - box * n_across) / 2
    y_offset = 0.5 * box + (A4[1] - box * n_down) / 2
    y_coordinate = 11 * inch - y_offset
    y_coordinate = 9.75 * inch - y_offset
    x_values = []  # will get one extra value
    y_values = []
    for _unused in range(0, n_across):
        x_values.append(x_coordinate)
        x_coordinate = x_coordinate + box
    for _unused in range(0, n_down):
        y_values.append(y_coordinate)
        # y_coordinate = y_coordinate - box
        y_coordinate = y_coordinate - 0.87*box
    coords = []
    for x in x_values:
        for y in y_values:
            # print x, y
            coords.append((x, y))

    x_list = []
    y_list = []
    # Set the X and Y values for the grid
    for x in x_values:
        x_list.append(int(x - box * 0.5))
    x_list.append(int(x_values[-1] + box * 0.5))
    for y in y_values:
        y_list.append(int(y + box * 0.65))
    # This math is cheating: I just looked at what gets returned
    # to figure out that it was off by 13.
    y_list.append(int(y_values[-1] - box * 0.5 + 13))
    return x_list, y_list, coords


def get_strings():
    """Takes a dictionary produced by set_ranges() and generates a list of
    random numbers for each letter in the range. How many random numbers depends
    on how longthe base word is.
    """
    # Get the word we're working with (probably "bingo")
    with open('c:/v/BofASNP/bofa_hugo/python/bingo.txt') as fin:
        strings = [l.strip() for l in fin.readlines() if l.strip()]
    strings = strings[:29]
    random.shuffle(strings)
    # remove any duplicates
    strings = list( dict.fromkeys(strings) )
    return strings


def get_strings_from_master_list():
    """Takes a dictionary produced by set_ranges() and generates a list of
    random numbers for each letter in the range. How many random numbers depends
    on how longthe base word is.
    """
    L = len(master_list)
    LL = random.randint(int(0.75*L), L)
    strings = copy.copy(master_list)[:LL]
    # add lots of free
    strings.append("FREE")
    strings.append("FREE")
    strings.append("FREE")
    random.shuffle(strings)
    # remove any duplicates
    strings = list( dict.fromkeys(strings) )
    return strings




def draw_grid(this_canvas, coords):
    """ Takes a canvas instance and x and y coordinate lists returned by
    get_coords() and draws a grid (in red) on the canvas."""
    this_canvas.setLineWidth(2.0)
    red50transparent = Color(100, 0, 0, alpha=0.5)
    this_canvas.setStrokeColor(red50transparent)
    # c.setStrokeGrey(0.75)
    x_list = coords[0]
    y_list = coords[1]
    this_canvas.grid(x_list, y_list)


def draw_strings(this_canvas, coords, strings):
    """ Takes a canvas, a list of tuples, a list of strings/ integers and draws
    each string on the canvas according to the coordinates. Assumes that
    "strings" includes letters as column headers and integers for the grid
    itself.
    !!! FIX: If the boxes are too small, the font should get reduced.
    """
#    for i in range(0, len(strings)):
    box = get_box_width(3)
    for i in range(0, len(coords)):
        # Print the "Free" cell in a smaller font.
        if (strings[i] == "FREE"):
            fontSize = 28
            fontName = 'Helvetica-BoldOblique'
        else:
            fontSize = 20
            fontName = 'Helvetica-Bold'
        this_canvas.setFont(fontName, fontSize)

        x = coords[i][0]
        y = coords[i][1] + 0.5*fontSize

        printable_string = str(strings[i])
        printable_strings = textwrap.wrap(printable_string, 12)
      #  print(stringWidth(printable_string, fontName, fontSize), box, 0.9*box)
        if len(printable_strings)==1:
            this_canvas.drawCentredString(x, y, printable_string)
        elif len(printable_strings)==2:
            y_up = y + 0.75*fontSize
            y_down = y - 0.75*fontSize
            this_canvas.drawCentredString(x, y_up, printable_strings[0])
            this_canvas.drawCentredString(x, y_down, printable_strings[1])
        elif len(printable_strings)==3:
            y_up = y + 1.5*fontSize
            y_down = y - 1.5*fontSize
            this_canvas.drawCentredString(x, y_up, printable_strings[0])
            this_canvas.drawCentredString(x, y, printable_strings[1])
            this_canvas.drawCentredString(x, y_down, printable_strings[2])
        else:
            print(printable_strings)


def draw_img(this_canvas, path):
    from PIL import Image

    page_width, page_height = this_canvas._pagesize

    image = Image.open(path)
    image_width, image_height = image.size

    this_canvas.drawImage(path, 0, 0, width=page_width, height=page_height,
                     preserveAspectRatio=False)


def draw_card_number(this_canvas, number):
    fontSize = 10
    fontName = 'Helvetica-Bold'
    this_canvas.setFont(fontName, fontSize)
    this_canvas.drawString(35, 35, "card "+str(number))

def when(card_strings, master_list, list_len):
    call = max([master_list.index(card_strings[i]) for i in range(list_len)])
    for i in range(list_len):
        print(card, i, card_strings[i], master_list.index(card_strings[i]))
    print(card, call)
    return call
    print('====')


def make_master_list():
    master_list = get_strings()
    master_list = ['FREE'] + master_list
    with open('cards/master_list.txt', 'w') as fout:
        for n, item in enumerate(master_list):
            print(n, item, file=fout)
            print(n, item)
    return master_list


def draw_card(path, filename, card, n_across, n_down):
    """Take a path, a filename, some integer (i), some word. Draw i bingo
    cards at path/filename.
    """
    os.chdir(path)
    os.chdir('c:/v/BofASNP/bofa_hugo/python/cards')
    # The canvas, ranges and coordinates only need to be set once.
    # this coords is x_list, y_list, tuples
    # x_list, y_list  x and y for each of box corners
    # tuples a list of (x,y) pairs of centres of boxes
    this_coordinates = get_coords(n_across, n_down)
    this_coord_tuples = this_coordinates[2]

    # Generate new random strings for each card.
    # for _unused in range(0, i):
    this_canvas = set_canvas(f'{filename}_{card}.pdf')

    draw_img(this_canvas, 'c:/v/BofASNP/bofa_hugo/python/SNP BINGO.png')
    card_strings = get_strings_from_master_list()
    call = when(card_strings, master_list, len(this_coord_tuples))
    draw_strings(this_canvas, this_coord_tuples, card_strings)
    draw_grid(this_canvas, this_coordinates)
    draw_card_number(this_canvas, card)
    this_canvas.save()
    return call

if __name__ =="__main__":

    with open('cards/when.txt', 'w') as card_info:
        max_call = 100
        master_list = make_master_list()

        for card in range(1, 500):
            call = draw_card("./", "bingo", card, 3, 4)
            print(card, call, file=card_info)
            max_call = min(call, max_call)
    print('max call', max_call)
