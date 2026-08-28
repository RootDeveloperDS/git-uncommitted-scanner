import asyncio
import time
from textual.app import App
from textual.widgets import DataTable

class BenchApp(App):
    def compose(self):
        yield DataTable()

    async def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("A", "B", "C")
        t0 = time.time()
        with self.batch_update():
            for i in range(100):
                table.add_row(str(i), "b", "c", key=str(i))
        print("Done:", time.time() - t0)
        self.exit()

if __name__ == "__main__":
    app = BenchApp()
    app.run()
