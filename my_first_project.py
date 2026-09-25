import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    print("Notebook is running")
    return


if __name__ == "__main__":
    app.run()
