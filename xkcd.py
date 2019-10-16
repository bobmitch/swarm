import pyglet
import urllib
import tempfile
import re
import random

win = pyglet.window.Window()
pyglet.gl.glClearColor(1, 1, 1, 1)

class XKCD(object):
    def __init__(self):
        self.fetch_image()

    index = None
    max_index = None
    def fetch_image(self):
        if self.index:
            url = 'http://xkcd.com/%s/'%self.index
        else:
            url = 'http://xkcd.com/'
        page = urllib.urlopen(url).read()
        m = re.search('(http://imgs.xkcd.com/comics/[^"]+)" title="([^"]+)"', page)
        url = m.group(1)
        title = m.group(2)
        t = tempfile.NamedTemporaryFile()
        t.write(urllib.urlopen(url).read())
        t.flush()

        index = re.search('this comic: http://xkcd.com/([^/]+)', page).group(1)
        self.index = int(index)
        if self.max_index is None:
            self.max_index = self.index

        # load image and create alt-text display
        self.image = pyglet.image.load(t.name)
        self.text = pyglet.text.Label(title, width=self.image.width,
            multiline=True, color=(0, 0, 0, 255),
            halign='center', anchor_x='center', anchor_y='bottom', x=self.image.width//2)
        win.set_size(self.image.width, self.image.height +
            self.text.content_height)

    def on_text(self, text):
        if text == 'r':
            self.index = random.randint(1, self.max_index)
            self.fetch_image()
            return True
        return False

    def on_text_motion(self, motion):
        if motion == pyglet.window.key.MOTION_LEFT:
            if self.index == 1: return False
            self.index = self.index - 1
        elif motion == pyglet.window.key.MOTION_RIGHT:
            if self.index == self.max_index: return False
            self.index = self.index + 1
        else:
            return False
        self.fetch_image()
        return True

    def on_draw(self):
        win.clear()
        if self.image is None:
            self.fetch_image()
        self.image.blit(0, self.text.content_height)
        self.text.draw()

xkcd = XKCD()
win.push_handlers(xkcd)

pyglet.app.run()