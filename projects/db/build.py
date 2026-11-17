import marimo

# marimo stamps the version of itself that generated this file — this is
# how marimo (not us) tracks which file format/feature set to expect. It
# isn't something we edit by hand.
__generated_with = "0.24.2"
# Creates the notebook "app" that every @app.cell function below registers
# itself with. width="medium" only controls how wide the notebook renders
# in the browser — it has no effect on the database logic.
app = marimo.App(width="medium")


# ============================================================================
# CELL: imports
# ----------------------------------------------------------------------------
# Every marimo cell is an ordinary Python function wrapped in @app.cell.
# marimo looks at each function's parameters to know which other cells'
# outputs it depends on, and at its `return (...)` tuple to know which
# names it hands to later cells — so the variable names in every cell
# below matter: this edit only adds comments, it never renames anything
# marimo relies on to wire the cells together.
# ============================================================================
@app.cell
def _():
    # The standard-library CSV reader — used below to read people.csv row
    # by row (people has to be loaded one row at a time; see the comment
    # near that INSERT).
    import csv
    # Standard-library OS interface — used to delete the old
    # database.duckdb file before every rebuild.
    import os

    # DuckDB: the embedded SQL database this whole project builds and
    # queries. duckdb.connect(...) is how every cell talks to the .duckdb
    # file on disk.
    import duckdb
    # marimo's own API, imported under the short alias `mo` by convention —
    # used here for mo.md(...) (renders a markdown cell) and
    # mo.notebook_dir() (finds this notebook's own folder on disk, so
    # paths work no matter where marimo was launched from).
    import marimo as mo
    # Polars: a fast dataframe library. ask() below converts every SQL
    # result to a polars DataFrame with .pl() so query results render as
    # tables in the notebook.
    import polars as pl
    # Matplotlib's plotting interface — used once, in "A Look at the
    # Data", to chart tasks created by day of week.
    import matplotlib.pyplot as plt

    # Hands every one of these names to any later cell that asks for it by
    # listing it as a parameter (e.g. `def _(duckdb, mo):` a few cells
    # down).
    return csv, duckdb, mo, os, pl, plt


# ============================================================================
# CELL: title / intro markdown
# ----------------------------------------------------------------------------
# Takes `mo` from the imports cell and renders a heading + one-line
# description — purely cosmetic, so it defines nothing later cells need,
# which is why its return is empty.
# ============================================================================
@app.cell
def _(mo):
    # Markdown-only cell: no computation, just a heading shown at the top
    # of the notebook.
    mo.md(r"""
    # BabsonAI Labs — Database Build

    Builds `database.duckdb` from nothing every time this notebook runs,
    using the CSV files `make_data.py` writes into `data/`.
    """)
    return


# ============================================================================
# CELL: paths and the read-only ask() helper
# ----------------------------------------------------------------------------
# Defines the three names every later cell in this notebook relies on:
# `database` (where the .duckdb file lives), `data_dir` (where the CSVs
# live), and `ask()` (the one approved way to query the database once it's
# built).
# ============================================================================
@app.cell
def _(duckdb, mo):
    # mo.notebook_dir() returns the folder this notebook file sits in
    # (projects/db/), regardless of what directory marimo was started
    # from — so `database` always points at projects/db/database.duckdb.
    database = mo.notebook_dir() / "database.duckdb"
    # Same idea, for the folder make_data.py writes its CSVs into.
    data_dir = mo.notebook_dir() / "data"

    def ask(sql):
        # Opens the database read_only=True, inside a `with` block, so the
        # connection — and the file lock that comes with it — closes the
        # instant this function returns. That's what lets other programs
        # (or a rebuild in this very notebook) open the same file again
        # right after.
        with duckdb.connect(database, read_only=True) as _con:
            # Runs the SQL and immediately converts the result to a polars
            # DataFrame (.pl()) before the connection closes, so it's the
            # data itself — not a live cursor tied to a now-closed
            # connection — that gets returned.
            return _con.sql(sql).pl()

    # Hands ask, data_dir and database to every later cell that lists them
    # as a parameter.
    return ask, data_dir, database


# ============================================================================
# CELL: "The Tables" markdown
# ----------------------------------------------------------------------------
# Markdown-only: describes, in prose, the five tables the next cell
# actually creates, and names which rule can't be held by a CHECK.
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    # The Tables

    Five tables: `people`, `projects`, `assignments` (who works on which
    project, with a role/hours/date for each pairing), `tasks` and
    `expenses`. `people.manager_id` is a foreign key back into `people`
    itself, nullable for the two founders. `assignments` has a composite
    primary key of `(person_id, project_id)`. Every rule the scenario
    states as a single-row fact is a `CHECK`; the one rule that spans
    tables -- a task's assignee must work on its project, and not before
    their start date -- can't be a `CHECK`, so it's checked with a query
    instead (business question 7).
    """)
    return


# ============================================================================
# CELL: build the database from nothing
# ----------------------------------------------------------------------------
# This is the one cell that actually creates projects/db/database.duckdb.
# It takes csv, data_dir, database, duckdb and os from earlier cells, and
# returns nothing, because nothing it defines needs to be visible to a
# later cell — later cells talk to the database only through the
# read-only ask() helper, never through this cell's own connection.
# ============================================================================
@app.cell
def _(csv, data_dir, database, duckdb, os):
    # Deletes any database left over from a previous run, so the build
    # below always starts from nothing and database.duckdb never drifts
    # out of sync with these CREATE TABLE statements or the CSVs in
    # data/.
    if database.exists():
        os.remove(database)

    # Opens one read/write connection for the whole build, inside a
    # `with` block, so the file closes (and its lock releases) the
    # moment this block ends — that's what lets ask(), or any other
    # program, open database.duckdb again right after this cell
    # finishes.
    with duckdb.connect(database) as _con:
        # ---- people ---------------------------------------------------
        _con.execute(
            """
            CREATE TABLE people (
                person_id   INTEGER PRIMARY KEY,                     -- one row per employee; referenced by assignments, tasks, and by manager_id below, which points back into this very table
                first_name  VARCHAR NOT NULL,                        -- can't be blank
                last_name   VARCHAR NOT NULL,                        -- can't be blank
                work_email  VARCHAR NOT NULL UNIQUE,                 -- no two people can share an email; make_data.py guarantees this when it generates rows
                title       VARCHAR NOT NULL,                        -- current job title; changes (along with the email) whenever someone is promoted
                start_date  DATE NOT NULL,                           -- the day this person started at BabsonAI Labs
                manager_id  INTEGER REFERENCES people(person_id)     -- FK back into people itself; NULL only for the two founders, who report to nobody
            )
            """
        )
        # ---- projects ---------------------------------------------------
        _con.execute(
            """
            CREATE TABLE projects (
                project_id  INTEGER PRIMARY KEY,                             -- one row per project; referenced by assignments, tasks and expenses
                name        VARCHAR NOT NULL,
                client_name VARCHAR,                                         -- nullable on purpose: internal projects (category = 'internal tool') have no client
                category    VARCHAR NOT NULL
                            CHECK (category IN ('LLM app', 'data pipeline', 'internal tool')),  -- restricts this column to exactly these three values
                budget      DECIMAL(12, 2) NOT NULL CHECK (budget > 0),      -- the scenario's rule "a budget is more than zero," enforced at the database level
                start_date  DATE NOT NULL,
                status      VARCHAR NOT NULL DEFAULT 'planned'
                            CHECK (status IN ('planned', 'active', 'paused', 'done'))  -- the only four statuses the scenario allows; defaults to 'planned' if a row doesn't say otherwise
            )
            """
        )
        # ---- assignments (who works on which project) -------------------
        _con.execute(
            """
            CREATE TABLE assignments (
                person_id      INTEGER NOT NULL REFERENCES people(person_id),      -- FK half of the composite key
                project_id     INTEGER NOT NULL REFERENCES projects(project_id),   -- FK half of the composite key
                role           VARCHAR NOT NULL,                                  -- this person's role on this specific project
                hours_per_week INTEGER NOT NULL CHECK (hours_per_week BETWEEN 1 AND 40),  -- "every commitment is at least one hour" and "nobody commits more than 40 hours/week to a single project"
                date_joined    DATE NOT NULL,                                     -- the day this person joined this project
                PRIMARY KEY (person_id, project_id)                              -- composite key: a person can be paired with a given project only once, but can appear in many such pairings, and so can a project
            )
            """
        )
        # ---- tasks ---------------------------------------------------------
        _con.execute(
            """
            CREATE TABLE tasks (
                task_id        INTEGER PRIMARY KEY,
                project_id     INTEGER NOT NULL REFERENCES projects(project_id),   -- every task belongs to exactly one project
                description    VARCHAR NOT NULL,
                created_date   DATE NOT NULL,
                assigned_to    INTEGER REFERENCES people(person_id),               -- nullable: a new task may be unassigned
                due_date       DATE NOT NULL,
                completed_date DATE,                                              -- nullable: stays empty until the task is actually completed
                CHECK (completed_date IS NULL OR completed_date >= created_date)  -- "it cannot be completed before it was created" -- a single-row rule, so a CHECK can hold it
            )
            """
        )
        # ---- expenses -----------------------------------------------------
        _con.execute(
            """
            CREATE TABLE expenses (
                expense_id   INTEGER PRIMARY KEY,
                project_id   INTEGER NOT NULL REFERENCES projects(project_id),   -- every expense belongs to exactly one project
                expense_date DATE NOT NULL,
                amount       DECIMAL(12, 2) NOT NULL CHECK (amount > 0),         -- "so is every expense" -- must be more than zero
                category     VARCHAR NOT NULL
                             CHECK (category IN ('GPU cloud', 'data labeling', 'software', 'travel')),  -- the only four expense categories the scenario allows
                note         VARCHAR
            )
            """
        )

        # people: one INSERT per row, managers before the people who report to
        # them. make_data.py always gives a manager a lower person_id than
        # their reports, so sorting by person_id puts every manager first.
        # Loading this table in one bulk statement fails instead: manager_id
        # is a foreign key into people itself, and DuckDB checks every row of
        # a statement against the table as it stood *before* that statement
        # ran, so the first report it reaches would have no manager to find
        # yet, no matter what order the CSV's rows come in.
        with open(data_dir / "people.csv", newline="") as _f:
            # csv.DictReader turns each CSV row into a dict keyed by the
            # header row's column names; sorted(..., key=...) re-orders
            # those dicts by person_id — as an int, not a string, so "10"
            # correctly sorts after "9", not between "1" and "2".
            _people_rows = sorted(csv.DictReader(_f), key=lambda _r: int(_r["person_id"]))
        for _r in _people_rows:
            # One INSERT per person, in manager-before-report order, so
            # every manager_id foreign key finds its target already in the
            # table by the time its report's own row is inserted.
            _con.execute(
                "INSERT INTO people VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    int(_r["person_id"]),
                    _r["first_name"],
                    _r["last_name"],
                    _r["work_email"],
                    _r["title"],
                    _r["start_date"],
                    # CSV cells are always strings; an empty string means
                    # "no manager" (the two founders), which has to become
                    # an actual Python None here to land as SQL NULL
                    # rather than as the literal text "".
                    int(_r["manager_id"]) if _r["manager_id"] else None,
                ],
            )

        # projects, assignments, tasks and expenses have no self-referencing
        # foreign key, so each can be loaded in a single bulk statement --
        # read_csv_auto() lets DuckDB read the CSV directly and infer its
        # column types, and the SELECT list re-states the columns in the
        # exact order the CREATE TABLE above declared them, so nothing
        # lands in the wrong column even if the CSV's own column order ever
        # changes.
        _con.execute(
            f"""
            INSERT INTO projects
            SELECT project_id, name, client_name, category, budget, start_date, status
            FROM read_csv_auto('{(data_dir / "projects.csv").as_posix()}')
            """
        )
        _con.execute(
            f"""
            INSERT INTO assignments
            SELECT person_id, project_id, role, hours_per_week, date_joined
            FROM read_csv_auto('{(data_dir / "assignments.csv").as_posix()}')
            """
        )
        _con.execute(
            f"""
            INSERT INTO tasks
            SELECT task_id, project_id, description, created_date, assigned_to, due_date, completed_date
            FROM read_csv_auto('{(data_dir / "tasks.csv").as_posix()}')
            """
        )
        _con.execute(
            f"""
            INSERT INTO expenses
            SELECT expense_id, project_id, expense_date, amount, category, note
            FROM read_csv_auto('{(data_dir / "expenses.csv").as_posix()}')
            """
        )

        # a question the founders would ask every week: how is each
        # project's spend tracking against its budget? used again in
        # questions.py (Part B).
        _con.execute(
            """
            CREATE VIEW project_spend_summary AS
            SELECT
                p.project_id,
                p.name,
                p.status,
                p.budget,
                COALESCE(SUM(e.amount), 0) AS total_spent,                             -- SUM over a LEFT JOIN is NULL for a project with no expense rows at all; COALESCE turns that into 0
                p.budget - COALESCE(SUM(e.amount), 0) AS remaining_budget,
                ROUND(100.0 * COALESCE(SUM(e.amount), 0) / p.budget, 1) AS pct_spent    -- written as 100.0, not 100, so the multiplication promotes to floating-point before the division runs
            FROM projects p
            LEFT JOIN expenses e ON e.project_id = p.project_id   -- LEFT JOIN, not JOIN, so a project with zero expenses still gets one row here, with total_spent = 0 rather than vanishing entirely
            GROUP BY p.project_id, p.name, p.status, p.budget
            """
        )
    # Nothing is returned: every name this cell defines (_con, _people_rows,
    # _r, _f) is prefixed with an underscore, which marimo treats as
    # private to this cell. That's intentional -- later cells are meant to
    # reach the database only through ask(), never through this cell's own
    # open connection.
    return


# ============================================================================
# CELL: "The Data" markdown
# ----------------------------------------------------------------------------
# Markdown-only: documents where the CSVs come from and exactly which two
# task rows make_data.py breaks on purpose (see gen_tasks in make_data.py)
# and why neither one can be stopped by a CREATE TABLE constraint above.
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    # The Data

    `make_data.py` writes `people.csv`, `projects.csv`,
    `assignments.csv`, `tasks.csv` and `expenses.csv` into `data/`,
    covering the 12 months up to an as-of date of **2026-11-08**, with a
    fixed random seed so it writes the same files every time.

    Business question 7 checks the one rule a `CHECK` can't hold: a
    task's assignee has to work on its project, and never before their
    start date. Two tasks break that rule on purpose:

    - **task_id 1** is assigned to someone who is not staffed on that
      task's project at all.
    - **task_id 2** is assigned to someone who *is* staffed on the
      project, but the task's `created_date` is 30 days before that
      person's `start_date` at the company.

    Both rows load without complaint, because neither rule can be
    written as a `CHECK` -- the query in question 7 is what has to catch
    them.
    """)
    return


# ============================================================================
# CELL: "A Look at the Data" heading
# ----------------------------------------------------------------------------
# Markdown-only section header; the actual chart is built in the next
# cell.
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    # A Look at the Data
    """)
    return


# ============================================================================
# CELL: tasks-by-weekday chart
# ----------------------------------------------------------------------------
# Reads tasks.csv straight into a polars DataFrame (independent of the
# database) and groups it by the weekday name of created_date, then
# bar-charts the result in Monday-Sunday order.
# ----------------------------------------------------------------------------
# FIXED 2026-11-16, after actually running this notebook for the first
# time: this cell originally ran the group-by as SQL, through
# duckdb.sql("... FROM _tasks ..."), relying on DuckDB's "replacement
# scan" feature, which auto-detects a local Python variable matching a
# table name by inspecting the calling stack frame. That trick works in
# a plain script or a Jupyter cell, but it failed here with "Catalog
# Error: Table with name _tasks does not exist!" the first time this was
# actually run in marimo -- marimo renames underscore-prefixed variables
# internally to keep them private to their own cell, so the actual
# runtime variable DuckDB's frame inspection went looking for wasn't
# literally named `_tasks` anymore, even though the source still reads
# that way. Doing the group-by in plain polars instead sidesteps that
# fragile mechanism entirely, and a single-table group-by this simple
# never needed SQL in the first place.
# ============================================================================
@app.cell
def _(mo, pl, plt):
    _tasks = pl.read_csv(mo.notebook_dir() / "data" / "tasks.csv", try_parse_dates=True)
    # Counts rows per weekday name (e.g. "Monday"), in polars rather than SQL.
    _counts = (
        _tasks.with_columns(pl.col("created_date").dt.strftime("%A").alias("weekday"))
        .group_by("weekday")
        .agg(pl.len().alias("n"))
    )
    # Converts the two parallel columns of the result into a single
    # {weekday_name: count} lookup.
    _by_day = dict(zip(_counts["weekday"].to_list(), _counts["n"].to_list()))
    # Fixes the display order Monday through Sunday -- group_by alone would
    # leave the weekdays in whatever order polars happens to return them.
    _order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # Looks up each weekday's count in that order, defaulting to 0 for any
    # weekday with no tasks created on it at all.
    _values = [_by_day.get(_d, 0) for _d in _order]

    # Builds a bar chart: one bar per weekday, in Monday-Sunday order.
    fig, ax = plt.subplots()
    ax.bar(_order, _values, color="#4C72B0")
    ax.set_xlabel("Day of week")
    ax.set_ylabel("Tasks created")
    ax.set_title("Tasks created, by day of week")
    # Angles the weekday labels so they don't overlap each other along the
    # x-axis.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    # The last bare expression in a marimo cell is what renders as that
    # cell's output -- here, the chart itself.
    fig
    return


# ============================================================================
# CELL: reflection on the chart
# ----------------------------------------------------------------------------
# Markdown-only: the author's own write-up of what the chart showed and
# what was changed in make_data.py (weekday_bias in random_date()) in
# response -- this is the "one sentence on whether a real business would
# look like that" the assignment asks for.
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    A first pass at `make_data.py` picked `created_date` uniformly at
    random, so tasks showed up almost as often on a Saturday as a
    Tuesday -- not what a real company working a normal week would look
    like. I changed `random_date()` in `make_data.py` so it re-rolls a
    weekend date back to a weekday about 85% of the time (startups do
    still touch things on weekends occasionally, just not nearly half
    the time), which is the mostly-weekday shape the chart above now
    shows.
    """)
    return


# ============================================================================
# CELL: "Row Counts" heading
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    # Row Counts
    """)
    return


# ============================================================================
# CELL: row counts
# ----------------------------------------------------------------------------
# Runs one query, through the read-only ask() helper, that stacks a count
# of every table into a single two-column result (table_name, n_rows),
# using UNION ALL so each SELECT contributes exactly one row to the final
# result.
# ============================================================================
@app.cell
def _(ask):
    ask(
        """
        SELECT 'people' AS table_name, count(*) AS n_rows FROM people
        UNION ALL SELECT 'projects', count(*) FROM projects
        UNION ALL SELECT 'assignments', count(*) FROM assignments
        UNION ALL SELECT 'tasks', count(*) FROM tasks
        UNION ALL SELECT 'expenses', count(*) FROM expenses
        """
    )
    return


# ============================================================================
# CELL: "A Row It Refuses" heading
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    # A Row It Refuses
    """)
    return


# ============================================================================
# CELL: a row the database refuses
# ----------------------------------------------------------------------------
# Deliberately tries to insert an expense with a negative amount (-50.00),
# which violates the CHECK (amount > 0) constraint on expenses. This cell
# opens its own short-lived write connection -- ask() is read-only and
# couldn't run an INSERT even if asked -- wrapped in try/except so that a
# refusal here doesn't stop the rest of the notebook from running.
# ============================================================================
@app.cell
def _(database, duckdb):
    try:
        with duckdb.connect(database) as _con:
            _con.execute(
                "INSERT INTO expenses VALUES (99901, 1, '2026-01-05', -50.00, 'software', 'refused on purpose')"
            )
        # Only reached if the INSERT somehow succeeded -- which would mean
        # the CHECK constraint isn't doing its job.
        refusal = "No error was raised -- the row was accepted (unexpected)."
    except Exception as _e:
        # The expected path: DuckDB raises a constraint-violation error,
        # whose type and message are captured here as plain text to
        # display.
        refusal = f"{type(_e).__name__}: {_e}"
    # The last bare expression in a marimo cell is what renders as that
    # cell's output -- so this is what shows the refusal message.
    refusal
    return


# ============================================================================
# CELL: "Answers You Already Knew" heading
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    # Answers You Already Knew
    """)
    return


# ============================================================================
# CELLS: first predict/then/query pair
# ----------------------------------------------------------------------------
# A markdown cell stating what count was expected before running the
# query (and why, pointing at a specific line in make_data.py), followed
# immediately by the ask() call that actually runs it, so the stated
# expectation can be checked against the real result right underneath.
# ============================================================================
@app.cell
def _(mo):
    mo.md("""
    I expect **25** -- that's the `n` I passed to `gen_people(n=25)` in `make_data.py`.
    """)
    return


@app.cell
def _(ask):
    # Confirms the prediction above by counting every row of people.
    ask("SELECT count(*) AS n_people FROM people")
    return


# ============================================================================
# CELLS: second predict/then/query pair
# ============================================================================
@app.cell
def _(mo):
    # NOTE: this string carries a couple of stray `"..."` fragments baked
    # into the text (left over from an earlier edit) -- harmless to
    # marimo, since it's just literal characters inside the markdown, but
    # worth a cleanup pass. Left as-is here since this edit only adds
    # comments, it doesn't change any wording.
    mo.md("""
    I expect **2** -- only the two founders have `manager_id IS NULL`; "
        "everyone else reports to somebody.
    """)
    return


@app.cell
def _(ask):
    # Confirms the prediction above: counts only the people whose
    # manager_id is NULL.
    ask("SELECT count(*) AS n_founders FROM people WHERE manager_id IS NULL")
    return


# ============================================================================
# CELLS: third predict/then/query pair
# ============================================================================
@app.cell
def _(mo):
    # Same stray-quote note as above -- cosmetic only, not changed here.
    mo.md("""
    I expect **3** -- `gen_projects()` builds `status_plan` with exactly "
        "`['planned'] * 3` before shuffling it in.
    """)
    return


@app.cell
def _(ask):
    # Confirms the prediction above: counts only the projects whose
    # status is 'planned'.
    ask("SELECT count(*) AS n_planned FROM projects WHERE status = 'planned'")
    return


# ============================================================================
# CELL: "A View" markdown
# ----------------------------------------------------------------------------
# Markdown-only: explains what project_spend_summary (created back in the
# "build the database" cell) is for, and that Part B reuses it.
# ============================================================================
@app.cell
def _(mo):
    mo.md(r"""
    # A View

    `project_spend_summary`, created above alongside the tables, answers
    a question the founders would ask every week: how is each project's
    spend tracking against its budget? Part B's first question runs
    straight off this view.
    """)
    return


# ============================================================================
# CELL: query the view
# ----------------------------------------------------------------------------
# Demonstrates that project_spend_summary behaves like any other table to
# query from -- orders every project by pct_spent, largest share of
# budget spent first.
# ============================================================================
@app.cell
def _(ask):
    ask("SELECT * FROM project_spend_summary ORDER BY pct_spent DESC")
    return


# Only launches the interactive marimo editor/server when this file is run
# directly (`python3 build.py` or `marimo edit build.py`) -- not when
# something else imports names out of this module instead.
if __name__ == "__main__":
    app.run()
