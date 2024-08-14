import urwid

class FileEditor:
    def __init__(self):
        self.file_path = None
        self.edit = urwid.Edit(multiline=True)
        self.load_button = urwid.Button("Load File", on_press=self.load_file)
        self.save_button = urwid.Button("Save File", on_press=self.save_file)
        self.file_name_edit = urwid.Edit("File Path: ")

        self.main_layout = urwid.Pile([
            urwid.Text("Simple Urwid File Editor"),
            self.file_name_edit,
            self.load_button,
            self.save_button,
            urwid.Divider(),
            urwid.BoxAdapter(urwid.Filler(self.edit), height=20)
        ])

        self.main_loop = urwid.MainLoop(
            urwid.Filler(self.main_layout),
            unhandled_input=self.handle_input
        )

    def load_file(self, button):
        self.file_path = self.file_name_edit.get_edit_text()
        try:
            with open(self.file_path, 'r') as f:
                content = f.read()
            self.edit.set_edit_text(content)
        except FileNotFoundError:
            self.edit.set_edit_text("File not found.")

    def save_file(self, button):
        if not self.file_path:
            self.file_path = self.file_name_edit.get_edit_text()
        with open(self.file_path, 'w') as f:
            f.write(self.edit.get_edit_text())
        self.edit.set_edit_text("File saved.")

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def run(self):
        self.main_loop.run()

if __name__ == "__main__":
    editor = FileEditor()
    editor.run()
