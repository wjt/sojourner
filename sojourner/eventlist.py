import gtk
import pango
from malvern import (
    MaybeStackableWindow, MaybePannableArea, MagicCheckButton, STAR_ICON,
)

class EventList(MaybeStackableWindow):
    """Shows a list of events; clicking on an event shows details of that
    event."""
    def __init__(self, schedule, title, events):
        MaybeStackableWindow.__init__(self, title)
        self.schedule = schedule
        store = gtk.TreeStore(str, object, bool)

        for event in events:
            store.append(None, [event.summary(), event,
                                event in self.schedule.favourites])

        treeview = gtk.TreeView(store)
        treeview.set_headers_visible(False)
        treeview.connect("row-activated", self.event_activated)

        tvcolumn = gtk.TreeViewColumn('Stuff')
        treeview.append_column(tvcolumn)

        cell = gtk.CellRendererText()
        cell.set_property("ellipsize", pango.ELLIPSIZE_END)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'markup', 0)

        cell = gtk.CellRendererPixbuf()
        cell.set_property("icon-name", STAR_ICON)
        tvcolumn.pack_start(cell, False)
        tvcolumn.add_attribute(cell, 'visible', 2)

        pannable = MaybePannableArea()
        pannable.add(treeview)
        self.add(pannable)

        self.show_all()

    def event_activated(self, treeview, row, column):
        store = treeview.get_property('model')
        iter = store.get_iter(row)
        event, = store.get(iter, 1)

        window = MaybeStackableWindow(event.title)

        vbox = gtk.VBox(spacing=12)

        label = gtk.Label()
        label.set_markup(event.full())
        label.set_properties(wrap=True, justify=gtk.JUSTIFY_FILL)
        vbox.pack_start(label)

        def update_star(state):
            store.set(iter, 2, state)

        toggle = MagicCheckButton("Favourite")
        toggle.set_active(event in self.schedule.favourites)
        toggle.connect('toggled', self.toggle_toggled, event, update_star)
        vbox.pack_start(toggle, False)

        pannable = MaybePannableArea()
        pannable.add_with_viewport(vbox)
        window.add(pannable)

        window.show_all()

    def toggle_toggled(self, toggle, event, update_star):
        if toggle.get_active():
            self.schedule.add_favourite(event)
            update_star(True)
        else:
            self.schedule.remove_favourite(event)
            update_star(False)
