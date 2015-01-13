from threading import Lock

from gi.repository import Gtk
from gi.repository import GdkPixbuf

PINCH_THRESHOLD = 0.1


class Slideshow(Gtk.Box):

    def __init__(self):
        super(Slideshow, self).__init__()
        self.image = Gtk.Image()
        self.image_path = None
        self.pack_start(self.image, True, True, 0)
        self.w = None
        self.h = None
        self.mutex = Lock()
        self.selection = None

    def render_selection(self, selection=None, reload=True, force=False,
                         scale=1):
        self.mutex.acquire()

        if selection is not None:
            new_image = selection.current()
        else:
            new_image = None

        if force or new_image:
            # TODO: image path is bad criteria for redrawing if we re-develop
            if (new_image and
                    self.image_path != new_image.image_path) or force:
                if reload:
                    pbuf = new_image.load_pixbuf(selection.library_path)
                    self.image_path = new_image.image_path
                else:
                    pbuf = self.image.get_pixbuf()
                # Set the initial size
                if self.w is None and self.h is None:
                    self.w = pbuf.get_width()
                    self.h = pbuf.get_height()
                if self.selection is None:
                    self.selection = selection
                if scale != 1:
                    self.image.set_from_pixbuf(
                        pbuf.scale_simple(
                            self.w * scale,
                            self.h * scale,
                            GdkPixbuf.InterpType.BILINEAR
                        )
                    )
                else:
                    self.image.set_from_pixbuf(pbuf)
                self.last_scale = 1

        self.mutex.release()

    def on_pinch(self, gesture, scale):
        if self.image and abs(scale - self.last_scale) > PINCH_THRESHOLD:
            pbuf = self.image.get_pixbuf()
            w = pbuf.get_width()
            h = pbuf.get_height()

            # Don't scale up past original size for now, or down below 100px.
            if (scale > 1 and w < self.w and
                    h < self.h) or (scale < 1 and w > 100 and h > 100):
                self.render_selection(reload=False, force=True, scale=scale)
                self.last_scale = scale
            elif (scale > 1 and w > self.w or h > self.h):
                self.render_selection(selection=self.selection, reload=True,
                                      force=True)
