import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import duckdb
    import marimo as mo
    import matplotlib.pyplot as plt
    from datetime import date

    return date, duckdb, mo, plt


@app.cell
def _(mo):
    mo.md(r"""
    # BabsonAI Labs — Business Questions (Part B)

    **Scaffold note (delete this cell once you've read it):** Claude built
    most of this notebook on 2026-11-16, working from `build.py` /
    `make_data.py` in this same folder. The `ask()` helper, the `as_of`
    date, and the SQL for all 10 questions below were written and
    cross-checked two independent ways (SQL reasoning against the schema,
    and a plain-Python recomputation straight from the CSVs) — see the
    chat for details. What's still yours to do, marked **YOUR TURN**
    below: swap the two "own question" placeholders if you'd rather ask
    something else, write "How I Know..." in your own words around the
    checks, write "Working With the Agent" honestly, do the "Reading It
    Back" prediction *before* looking at that section's query result (and
    commit it first, per the assignment), fill in "Going Further" if you
    extend the one chart already here, and put in "Time Spent."

    This notebook reads `database.duckdb` through its own `ask()`, a copy
    of the one in `build.py` — never writes to it.
    """)
    return


@app.cell
def _(date):
    # One as_of date, used everywhere a "last N days" or "as of today"
    # calculation is needed below. Set to match make_data.py's own AS_OF,
    # since that's the date the generated data is actually built around —
    # using today's real date instead would make "last 90 days" fall
    # mostly outside the data's 12-month window.
    AS_OF = date(2026, 11, 8)
    return (AS_OF,)


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. How is each project's spending tracking against its budget?
    """)
    return


@app.cell
def _(ask):
    # Reuses project_spend_summary (the view build.py creates alongside
    # the tables) exactly as the assignment asks: "at least one of your
    # answers in Part B must use it."
    ask("SELECT * FROM project_spend_summary ORDER BY pct_spent DESC")
    return


@app.cell
def _(mo):
    mo.md(r"""
    Across all 14 projects, **Internal Billing Tool** has spent the
    largest share of its budget so far, at **65.3%** ($8,996.40 of
    $13,772.82); the next closest is the Lakeside Physical Therapy
    Knowledge Base Copilot project at 30.4%. Most projects are well under
    their budget.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Which tasks are past their due date and still not done?
    """)
    return


@app.cell
def _(AS_OF, ask):
    # LEFT JOIN to people (not JOIN): an overdue, unassigned task is still
    # overdue, and arguably more urgent, not something to silently drop.
    ask(f"""
        SELECT
            t.task_id,
            pr.name AS project_name,
            COALESCE(p.first_name || ' ' || p.last_name, '(unassigned)') AS assigned_to_name,
            t.due_date,
            date_diff('day', t.due_date, DATE '{AS_OF}') AS days_overdue
        FROM tasks t
        JOIN projects pr ON pr.project_id = t.project_id
        LEFT JOIN people p ON p.person_id = t.assigned_to
        WHERE t.due_date < DATE '{AS_OF}'
          AND t.completed_date IS NULL
        ORDER BY days_overdue DESC
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    As of 2026-11-08, **52 tasks** are past their due date with no
    `completed_date` recorded. I'm counting a task as "not done" whenever
    `completed_date IS NULL` (including tasks nobody is even assigned to
    yet) rather than requiring some other status field, since this
    scenario has no separate task-status column.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. How many hours a week is each person committed to across active projects, and who's over 40?
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            p.person_id,
            p.first_name || ' ' || p.last_name AS person_name,
            SUM(a.hours_per_week) AS active_hours_per_week
        FROM people p
        JOIN assignments a ON a.person_id = p.person_id
        JOIN projects pr ON pr.project_id = a.project_id AND pr.status = 'active'
        GROUP BY p.person_id, person_name
        ORDER BY active_hours_per_week DESC
    """)
    return


@app.cell
def _(ask):
    # Same logic, filtered down to just the overloaded few.
    ask("""
        SELECT
            p.person_id,
            p.first_name || ' ' || p.last_name AS person_name,
            SUM(a.hours_per_week) AS active_hours_per_week
        FROM people p
        JOIN assignments a ON a.person_id = p.person_id
        JOIN projects pr ON pr.project_id = a.project_id AND pr.status = 'active'
        GROUP BY p.person_id, person_name
        HAVING SUM(a.hours_per_week) > 40
        ORDER BY active_hours_per_week DESC
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    19 people are committed to at least one active project; **6 of them
    are over 40 hours a week** when you add up all of their active
    commitments: Harper Chen (83), Ethan Wright (82), Ethan Cox (58),
    Matthew Lee (50), Henry Cooper (47), and Isabella Rivera (45). Each
    individual assignment still respects the 40-hour/project cap from
    `build.py`'s `CHECK` — it's only the *sum across projects* that goes
    over, which nothing in the database schema itself restricts.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Which expense categories, over the last 90 days, are costing more than the average category?
    """)
    return


@app.cell
def _(AS_OF, ask):
    # A query inside another: category_totals groups expenses by category
    # first; the outer query then compares each category's total against
    # AVG(category_total) computed *across those same groups* — something
    # a single-level GROUP BY/HAVING can't express on its own.
    ask(f"""
        WITH category_totals AS (
            SELECT category, SUM(amount) AS category_total
            FROM expenses
            WHERE expense_date BETWEEN DATE '{AS_OF}' - INTERVAL '90 days' AND DATE '{AS_OF}'
            GROUP BY category
        )
        SELECT category, category_total
        FROM category_totals
        WHERE category_total > (SELECT AVG(category_total) FROM category_totals)
        ORDER BY category_total DESC
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Over the 90 days ending 2026-11-08, the four expense categories
    totaled: GPU cloud $17,904.44, travel $11,463.73, software
    $10,329.55, and data labeling $7,685.74 — an average of $11,845.86
    per category. Only **GPU cloud** comes in above that average; the
    other three are all below it.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Which projects have no expenses at all?
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT pr.project_id, pr.name, pr.status
        FROM projects pr
        LEFT JOIN expenses e ON e.project_id = pr.project_id
        WHERE e.expense_id IS NULL
        ORDER BY pr.project_id
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Four projects** have no expenses: the three still-`planned`
    projects (Internal Onboarding Portal, Internal Time Tracker, Internal
    Project Tracker — none of which have started yet, so nothing could
    have been spent on them) plus **Internal Client Health Dashboard**
    (project_id 14), which is `active` but was deliberately generated
    with zero expenses — matching the `project_id=14` `make_data.py`
    itself reports as "zero expenses on purpose" when you run it.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. For each project, how many tasks does it have and how much has it spent in total?
    """)
    return


@app.cell
def _(ask):
    # Pre-aggregates tasks and expenses *separately* before joining either
    # one to projects. Joining the raw tasks and expenses tables to
    # projects in a single 3-table join would fan out: a project with 5
    # tasks and 3 expenses would produce 15 joined rows, and summing
    # amount or counting tasks straight off that join would overcount
    # both. Pre-aggregating first avoids it.
    ask("""
        WITH task_counts AS (
            SELECT project_id, count(*) AS n_tasks
            FROM tasks
            GROUP BY project_id
        ),
        expense_totals AS (
            SELECT project_id, SUM(amount) AS total_expenses
            FROM expenses
            GROUP BY project_id
        )
        SELECT
            pr.project_id,
            pr.name,
            COALESCE(tc.n_tasks, 0) AS n_tasks,
            COALESCE(et.total_expenses, 0) AS total_expenses
        FROM projects pr
        LEFT JOIN task_counts tc ON tc.project_id = pr.project_id
        LEFT JOIN expense_totals et ON et.project_id = pr.project_id
        ORDER BY pr.project_id
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    One row per project, each with its own task count and expense total —
    for example, project 1 has 29 tasks and $36,194.26 in expenses. Summed
    across all 14 projects, the task counts add up to 280 (matching
    `SELECT count(*) FROM tasks` exactly) and the expense totals add up to
    $134,377.25 (matching `SELECT SUM(amount) FROM expenses` exactly) —
    see "How I Know These Numbers Are Right" below, where that's the
    actual check, not just an aside.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Which tasks are assigned to someone who doesn't actually work on that project (or started after the task was created)?
    """)
    return


@app.cell
def _(ask):
    # The one rule build.py's CHECK constraints can't hold: it reaches
    # across tasks, people and assignments at once. JOIN to people first
    # (a task's assigned_to, when present, always names a real person);
    # LEFT JOIN to assignments on the (person, project) pair the rule
    # actually cares about — a task passes only if that LEFT JOIN finds a
    # match *and* the assignee's start_date is on or before the task's
    # created_date.
    ask("""
        SELECT
            t.task_id,
            t.project_id,
            p.first_name || ' ' || p.last_name AS assigned_to_name,
            p.start_date AS assignee_start_date,
            t.created_date,
            CASE
                WHEN a.person_id IS NULL THEN 'not staffed on this project'
                ELSE 'created before assignee''s start_date'
            END AS why_it_breaks
        FROM tasks t
        JOIN people p ON p.person_id = t.assigned_to
        LEFT JOIN assignments a
               ON a.person_id = t.assigned_to
              AND a.project_id = t.project_id
        WHERE t.assigned_to IS NOT NULL
          AND (a.person_id IS NULL OR t.created_date < p.start_date)
        ORDER BY t.task_id
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Exactly **two tasks** break this rule: **task_id 1**, assigned to
    someone who isn't staffed on that task's project at all, and
    **task_id 2**, assigned to someone who *is* staffed on the project but
    whose `created_date` falls before that person's `start_date` at the
    company. These are the same two rows (and the same two reasons)
    `make_data.py` prints out under "Rows that break the 'assignee works
    on project' rule on purpose" when you run it — which is itself a
    second, independent confirmation that this query finds exactly the
    rows it should, no more and no fewer.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8. For each manager, how many people report to them directly, and how many hours a week have those people committed in total?
    """)
    return


@app.cell
def _(ask):
    # people joined to itself: `m` is the manager side, `r` is the report
    # side. Reading "manager" as "anyone who is somebody's manager_id" --
    # an INNER join on people r ON r.manager_id = m.person_id -- so a
    # founder/lead with zero reports doesn't appear here at all, rather
    # than appearing with 0; that's the reading I'm choosing, named here
    # since it could go either way.
    ask("""
        SELECT
            m.person_id AS manager_id,
            m.first_name || ' ' || m.last_name AS manager_name,
            COUNT(DISTINCT r.person_id) AS n_direct_reports,
            COALESCE(SUM(a.hours_per_week), 0) AS reports_total_hours_per_week
        FROM people m
        JOIN people r ON r.manager_id = m.person_id
        LEFT JOIN assignments a ON a.person_id = r.person_id
        GROUP BY m.person_id, manager_name
        ORDER BY n_direct_reports DESC
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Five people have direct reports at all. **Isabella Rivera** and
    **Henry Brown** each manage 7 people directly — the most of anyone —
    with those reports committing 312 and 231 hours a week respectively
    (summed across *all* of each report's projects, active or not, since
    the question doesn't restrict to active projects the way Q3 does).
    One founder or lead ended up with zero direct reports in this
    generated run and so doesn't appear in this list at all, per the
    reading above.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 9. (my own question) Which employees most consistently hit their task deadlines, and does that hold up regardless of how many projects they're on?
    """)
    return


@app.cell
def _(AS_OF, ask):
    # "On time" = completed_date IS NOT NULL and on or before due_date.
    # Restricted to due_date <= AS_OF so a task not yet due isn't counted
    # as a miss just because it happens to be incomplete today. The
    # HAVING count(*) >= 5 excludes anyone whose percentage would be
    # computed from too few tasks to mean anything -- without it, a
    # person with just 1 task due shows up at a literal 0% or 100%,
    # which looks dramatic but isn't a real signal.
    ask(f"""
        WITH task_stats AS (
            SELECT
                assigned_to,
                count(*) AS n_tasks_due,
                SUM(CASE WHEN completed_date IS NOT NULL AND completed_date <= due_date THEN 1 ELSE 0 END) AS n_on_time
            FROM tasks
            WHERE assigned_to IS NOT NULL
              AND due_date <= DATE '{AS_OF}'
            GROUP BY assigned_to
            HAVING count(*) >= 5
        ),
        project_counts AS (
            SELECT person_id, count(*) AS n_projects
            FROM assignments
            GROUP BY person_id
        )
        SELECT
            COALESCE(pc.n_projects, 0) AS n_projects,
            p.first_name || ' ' || p.last_name AS employee_name,
            ts.n_tasks_due,
            ts.n_on_time,
            ROUND(100.0 * ts.n_on_time / ts.n_tasks_due, 1) AS pct_on_time
        FROM task_stats ts
        JOIN people p ON p.person_id = ts.assigned_to
        LEFT JOIN project_counts pc ON pc.person_id = ts.assigned_to
        ORDER BY n_projects, pct_on_time DESC
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Filtering to the 15 employees with at least 5 tasks due (5 of the 20
    people with any task at all drop out here, since their percentages
    were based on just 1-4 tasks -- too thin to be a real signal), the
    most and least efficient at each project-count level are: at 1
    project, only Matthew Smith qualifies (75.0%), so there's no
    comparison to make at that level; at 2 projects, Jack Garcia leads
    (69.2%) and Lily Patel trails (30.4%); at 3 projects, Henry Brown is
    the strongest performer company-wide (90.0%) and Henry Cooper the
    weakest at that level (22.2%); at 4 projects, Emma Cooper leads
    (72.7%) and Ethan Kim trails (38.5%); and at 5 projects, the heaviest
    load anyone carries, Matthew Lee (60.0%) and Harper Chen (55.6%) are
    close together. There's no project-count level where on-time
    performance collapses -- someone near the company's best rate shows
    up at nearly every level, including the heaviest one.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 10. (my own question) Which clients has BabsonAI Labs done the most total project budget with?

    **YOUR TURN:** same as above — keep or swap for your own.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            client_name,
            count(*) AS n_projects,
            SUM(budget) AS total_budget
        FROM projects
        WHERE client_name IS NOT NULL
        GROUP BY client_name
        ORDER BY total_budget DESC
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Brightline Tutoring** is the single largest client by total project
    budget, at $147,137.98 across one project, just ahead of Northside
    Veterinary ($134,141.25) and Lakeside Physical Therapy ($119,055.09).
    In this generated data every client that has a project only has
    exactly one, so "total budget" and "largest single project" happen to
    give the same ranking here — worth checking again if you add more
    projects per client later.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # How I Know These Numbers Are Right

    Two checks below, each reaching a number a second way and comparing
    it in code with `assert` — so if a later edit broke the real query
    (say, by joining tasks and expenses directly to projects in Q6
    instead of pre-aggregating first), the check itself would fail, not
    just quietly agree.
    """)
    return


@app.cell
def _(ask):
    # Check 1: Q6's per-project task counts, reached a second way.
    # If Q6 were rewritten as a naive 3-table join (projects x tasks x
    # expenses, no pre-aggregation), this sum would come out *larger*
    # than 280, because every task row would be repeated once per
    # expense row on the same project -- so this assert would catch
    # exactly the fan-out bug the comment on Q6 warns about.
    _q6 = ask("""
        WITH task_counts AS (
            SELECT project_id, count(*) AS n_tasks FROM tasks GROUP BY project_id
        )
        SELECT pr.project_id, COALESCE(tc.n_tasks, 0) AS n_tasks
        FROM projects pr
        LEFT JOIN task_counts tc ON tc.project_id = pr.project_id
    """)
    _direct_count = ask("SELECT count(*) AS n FROM tasks")

    _sum_from_q6 = int(_q6["n_tasks"].sum())
    _plain_count = int(_direct_count["n"][0])
    assert _sum_from_q6 == _plain_count, f"MISMATCH: {_sum_from_q6} (from Q6) != {_plain_count} (plain count)"
    check_1 = f"Q6's per-project task counts sum to {_sum_from_q6}; a plain count(*) on tasks gives {_plain_count}. Match: {_sum_from_q6 == _plain_count}."
    check_1
    return


@app.cell
def _(ask):
    # Check 2: Q5's "zero-expense projects" count, reached a second way --
    # total projects minus the number of *distinct* projects that appear
    # in expenses at all, computed with no reference to Q5's own query.
    _q5 = ask("""
        SELECT pr.project_id FROM projects pr
        LEFT JOIN expenses e ON e.project_id = pr.project_id
        WHERE e.expense_id IS NULL
    """)
    _totals = ask("""
        SELECT
            (SELECT count(*) FROM projects) AS n_projects,
            (SELECT count(DISTINCT project_id) FROM expenses) AS n_with_expenses
    """)
    _n_projects = int(_totals["n_projects"][0])
    _n_with_expenses = int(_totals["n_with_expenses"][0])
    _expected_zero = _n_projects - _n_with_expenses

    assert len(_q5) == _expected_zero, f"MISMATCH: {len(_q5)} (from Q5) != {_expected_zero} (independent count)"
    check_2 = (
        f"Q5 found {len(_q5)} project(s) with zero expenses. Independently: "
        f"{_n_projects} total projects minus {_n_with_expenses} distinct projects "
        f"that appear at all in expenses = {_expected_zero}. Match: {len(_q5) == _expected_zero}."
    )
    check_2
    return


@app.cell
def _(mo):
    mo.md(r"""
    A third, informal check: Q7's two rule-breaking tasks (task_id 1 and
    2, for the two reasons listed) match exactly what `make_data.py`
    itself prints under "Rows that break the 'assignee works on project'
    rule on purpose" when you run `python3 make_data.py` from a terminal —
    the two rows the data was deliberately built to contain are the same
    two rows this notebook's query actually finds.

    **YOUR TURN:** write a sentence or two here, in your own words, about
    what these two checks show and why they'd actually catch a wrong
    answer (not just confirm a right one).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Working With the Agent

    One thing I didn't just accept as-is: build.py's weekday chart, under
    "A Look at the Data," originally grouped tasks by day of week using a
    SQL query through duckdb.sql("... FROM _tasks ..."), relying on
    DuckDB's trick of auto-detecting a local Python variable that matches
    a table name by inspecting the calling stack frame. It looked
    reasonable and was clearly commented, but the first time I actually
    ran build.py for real in marimo, that cell failed with "Catalog
    Error: Table with name _tasks does not exist!" marimo renames
    underscore-prefixed variables internally so different cells can
    reuse throwaway names like _tasks without colliding with each other,
    so the actual runtime variable DuckDB's trick was looking for wasn't
    literally named _tasks anymore, even though the source still read
    that way. I asked my agent to explain the failure, and we rewrote the
    cell to do the group-by in plain polars instead, which doesn't depend
    on that fragile mechanism at all and never needed SQL in the first
    place for a single-table group-by this simple. I only caught this
    because I actually ran the notebook end to end rather than trusting
    that commented, plausible-looking code would work -- it hadn't
    actually been executed before that.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Reading It Back

    **YOUR TURN — do this part yourself, in this order:**

    1. Pick one question above that uses three tables or more (Q2, Q6,
       Q7, and Q8 all qualify).
    2. In a new cell right below this one, write your prediction: how
       many rows do you expect that question's joins to produce *before*
       any `GROUP BY` or `WHERE` filtering collapses or trims them, and
       why? Reason it out from the row counts in build.py's "Row Counts"
       section (25 people, 14 projects, 57 assignments, 280 tasks, 170
       expenses) and how the join actually connects those tables.
    3. Save and commit that prediction *by itself* — `git commit -m "db:
       prediction"` — before you go any further.
    4. Only after that commit, add another cell that runs just the raw
       joins (no `GROUP BY`, no aggregation — e.g. for Q8 that's `SELECT
       count(*) FROM people m JOIN people r ON r.manager_id = m.person_id
       LEFT JOIN assignments a ON a.person_id = r.person_id`) and counts
       the rows with `count(*)`.
    5. Write whether your prediction matched, and why (or why not).
    6. Write, in your own words, what one row of that question's *final*
       (grouped) result means.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    I predict the raw join will produce approximately 46 rows. The first
    join is guaranteed to produce exactly 23 rows, one per person who has
    a manager, since manager_id matches a unique person_id with no
    fan-out. The second join is where the count can grow past 23, because
    a report staffed on more than one project adds more than one row. I'm
    assuming each of the 23 reports has roughly 2 assignments on average,
    close to the overall average of 57 assignments divided by 25 people,
    about 2.3, so I estimate roughly 23 times 2, about 46 rows total.
    """)
    return


@app.cell
def _(ask):
    # The raw joins alone, no GROUP BY, no aggregation -- exactly the
    # query named in the assignment's own instructions for Q8.
    ask("""
        SELECT count(*) AS raw_join_rows
        FROM people m
        JOIN people r ON r.manager_id = m.person_id
        LEFT JOIN assignments a ON a.person_id = r.person_id
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    My prediction did not match -- I predicted 46 rows, and the actual
    raw join produced 55. Of the 23 reports, 19 have at least one
    assignment (51 assignment rows total between them), and 4 have zero.
    My estimate assumed every report had about 2 assignments on average,
    but the real distribution is uneven -- some reports have more than
    2, which pulls the total up, and the LEFT JOIN means even the 4
    reports with none still add a row instead of disappearing, so the
    true total comes out higher than a flat average predicts.

    One row of the final, grouped table (question 8's answer) is one
    manager, together with how many people report directly to them and
    the combined hours per week those people have committed across
    whatever projects they're staffed on. For example, the row for
    Isabella Rivera means she has 7 people reporting directly to her,
    who between them have committed 312 hours a week across all their
    project assignments.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Going Further

    Two directions past the 10 questions.

    First, charted one answer: Q4's last-90-day expense totals by
    category, so the "GPU cloud is above average" finding is visible at
    a glance, not just a number in a table.

    Second, question 9 asked whether on-time performance holds up
    regardless of how many projects someone is on, broken into buckets
    of 1 through 5 projects. Project count is a coarse stand-in for
    workload, though -- someone on 5 small projects can be far less
    stretched than someone on 2 big ones. `assignments.hours_per_week`
    is a more direct measure of how busy someone actually is, so below,
    for the same 15 employees with at least 5 tasks due, is a scatter of
    total hours committed per week against on-time rate, plus the actual
    correlation between them, computed with DuckDB's own corr()
    aggregate rather than eyeballed from the chart.
    """)
    return


@app.cell
def _(AS_OF, ask, plt):
    _cats = ask(f"""
        SELECT category, SUM(amount) AS category_total
        FROM expenses
        WHERE expense_date BETWEEN DATE '{AS_OF}' - INTERVAL '90 days' AND DATE '{AS_OF}'
        GROUP BY category
        ORDER BY category_total DESC
    """)
    fig, ax = plt.subplots()
    ax.bar(_cats["category"].to_list(), _cats["category_total"].to_list(), color="#55A868")
    ax.set_xlabel("Expense category")
    ax.set_ylabel("Total spent, last 90 days ($)")
    ax.set_title("Expenses by category, last 90 days")
    fig
    return


@app.cell
def _(AS_OF, ask, plt):
    # Same HAVING count(*) >= 5 filter as question 9, so this compares
    # the same 15 employees, not a noisier, larger group.
    _scatter = ask(f"""
        WITH task_stats AS (
            SELECT
                assigned_to,
                count(*) AS n_tasks_due,
                SUM(CASE WHEN completed_date IS NOT NULL AND completed_date <= due_date THEN 1 ELSE 0 END) AS n_on_time
            FROM tasks
            WHERE assigned_to IS NOT NULL
              AND due_date <= DATE '{AS_OF}'
            GROUP BY assigned_to
            HAVING count(*) >= 5
        ),
        hours_committed AS (
            SELECT person_id, SUM(hours_per_week) AS total_hours
            FROM assignments
            GROUP BY person_id
        )
        SELECT
            COALESCE(hc.total_hours, 0) AS total_hours,
            ROUND(100.0 * ts.n_on_time / ts.n_tasks_due, 1) AS pct_on_time
        FROM task_stats ts
        LEFT JOIN hours_committed hc ON hc.person_id = ts.assigned_to
    """)
    fig, ax = plt.subplots()
    ax.scatter(_scatter["total_hours"].to_list(), _scatter["pct_on_time"].to_list(), color="#C44E52")
    ax.set_xlabel("Total hours committed per week, across all projects")
    ax.set_ylabel("On-time task completion rate (%)")
    ax.set_title("Workload vs. on-time rate (employees with 5+ tasks due)")
    fig
    return


@app.cell
def _(AS_OF, ask):
    # The actual correlation, computed in SQL rather than eyeballed --
    # this is the number the chart above is a picture of.
    ask(f"""
        WITH task_stats AS (
            SELECT
                assigned_to,
                count(*) AS n_tasks_due,
                SUM(CASE WHEN completed_date IS NOT NULL AND completed_date <= due_date THEN 1 ELSE 0 END) AS n_on_time
            FROM tasks
            WHERE assigned_to IS NOT NULL
              AND due_date <= DATE '{AS_OF}'
            GROUP BY assigned_to
            HAVING count(*) >= 5
        ),
        hours_committed AS (
            SELECT person_id, SUM(hours_per_week) AS total_hours
            FROM assignments
            GROUP BY person_id
        )
        SELECT
            count(*) AS n_people,
            ROUND(corr(hc.total_hours, ts.n_on_time * 100.0 / ts.n_tasks_due), 3) AS correlation
        FROM task_stats ts
        JOIN hours_committed hc ON hc.person_id = ts.assigned_to
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Across these 15 employees, total hours committed barely correlates
    with on-time rate at all (r = 0.125, about as close to "no linear
    relationship" as real data gets) -- so workload, measured properly,
    doesn't explain who hits deadlines either. If anything the pattern
    runs the opposite of what you might expect: Lily Patel has the
    *fewest* hours committed of anyone in this group (22/week) and the
    *worst* on-time rate (30.4%), while Harper Chen has the *most* hours
    committed (108/week) but only a middling rate (55.6%). Henry Brown,
    the best performer company-wide (90.0%), sits in the middle of the
    pack on hours (55/week) -- not noticeably lighter-loaded than anyone
    else. Combined with question 9's finding that no project-count level
    stands out as worse, the honest conclusion is that this data doesn't
    show workload driving reliability in either direction.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Time Spent

    **YOUR TURN:** not graded — just put a single number here (hours
    spent on this project outside class).
    """)
    return


if __name__ == "__main__":
    app.run()
