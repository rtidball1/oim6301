# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of project, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    I would use this event profit planner for my networking event company, Corporates Connect (Cc). It would help me decide how to price tickets, how many ticket pricing tiers to offer, and how much I can spend on an event in order to hit my profit goal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    My first step will be to enter my estimated event expenses, estimated ticket prices for three tiers, and estimated number of tickets per tier.

    I will enter different combinations of ticket prices and the number of tickets sold for the tool to compare.

    With the assistance of an AI agent, I will get my event planner tool to calculate the projected revenue, expenses, and profit for the event based on my inputs.

    For each combination, I will ask my tool to multiply the number of tickets in each tier by the respective price and add those amounts to calculate total revenue. It will then subtract total expenses to calculate the projected profit for the event.

    I will also ask my tool to produce a table of combinations that meet or exceed my profit goal. It will identify the option that meets my goal with the fewest tickets sold and explain the result in a sentence. If none of the combinations meet my goal, I will get it to tell me to change an input.

    - *What does your loop carry from one step to the next, the way a running total carries its sum?*

    My loop will carry a list of combinations that meet my profit goal. It will also remember the combination with the fewest tickets sold and update that result if it is beat.

    - *Which check will you use in section 6, and which two numbers should agree?*

    To check that the numbers are calculated correctly, I will calculate profit manually for a ticket combination and compare it with the profit calculated by the tool (using the same ticket prices per tier and expenses). My manual calculation must match the tools output.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your project from the Mini Project 1 page. If you chose your own project, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    # Your inputs.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


if __name__ == "__main__":
    app.run()
