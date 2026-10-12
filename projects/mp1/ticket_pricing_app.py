import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Corporates Connect Ticket Planner

    Compare low, base, and high ticket prices to find the minimum
    sales needed to reach your profit goal.

    Adjust the event assumptions below to explore different scenarios.
    """)
    return


@app.cell
def _(mo):
    capacity_input = mo.ui.number(
        start=1,
        step=1,
        value=300,
        label="Maximum attendees",
    )

    profit_goal_input = mo.ui.number(
        start=0,
        step=100,
        value=3000,
        label="Profit goal ($)",
    )

    food_cost_input = mo.ui.number(
        start=0,
        step=1,
        value=10,
        label="Food cost per attendee ($)",
    )

    bar_spend_input = mo.ui.number(
        start=0,
        step=1,
        value=15,
        label="Estimated bar spend per attendee ($)",
    )

    venue_minimum_input = mo.ui.number(
        start=0,
        step=100,
        value=4000,
        label="Venue minimum bar spend ($)",
    )

    allowance_input = mo.ui.number(
        start=0,
        step=50,
        value=500,
        label="Other spending allowance ($)",
    )

    mo.vstack([
        mo.md("## Event assumptions"),
        capacity_input,
        profit_goal_input,
        food_cost_input,
        bar_spend_input,
        venue_minimum_input,
        allowance_input,
    ])
    return (
        allowance_input,
        bar_spend_input,
        capacity_input,
        food_cost_input,
        profit_goal_input,
        venue_minimum_input,
    )


@app.cell
def _(mo):
    # Maximum tickets available in each tier.
    early_bird_limit_input = mo.ui.number(
        start=0, step=1, value=50,
        label="Early Bird tickets available",
    )

    ga1_limit_input = mo.ui.number(
        start=0, step=1, value=150,
        label="GA1 tickets available",
    )

    ga2_limit_input = mo.ui.number(
        start=0, step=1, value=100,
        label="GA2 tickets available",
    )

    # Low pricing option.
    low_early_input = mo.ui.number(
        start=0, step=1, value=10, label="Early Bird price ($)",
    )
    low_ga1_input = mo.ui.number(
        start=0, step=1, value=15, label="GA1 price ($)",
    )
    low_ga2_input = mo.ui.number(
        start=0, step=1, value=20, label="GA2 price ($)",
    )

    # Base pricing option.
    base_early_input = mo.ui.number(
        start=0, step=1, value=35, label="Early Bird price ($)",
    )
    base_ga1_input = mo.ui.number(
        start=0, step=1, value=40, label="GA1 price ($)",
    )
    base_ga2_input = mo.ui.number(
        start=0, step=1, value=50, label="GA2 price ($)",
    )

    # High pricing option.
    high_early_input = mo.ui.number(
        start=0, step=1, value=50, label="Early Bird price ($)",
    )
    high_ga1_input = mo.ui.number(
        start=0, step=1, value=70, label="GA1 price ($)",
    )
    high_ga2_input = mo.ui.number(
        start=0, step=1, value=100, label="GA2 price ($)",
    )

    # Arrange the controls on the page.
    mo.vstack([
        mo.md("## Ticket availability"),
        mo.md(
            "Tickets sell in order: Early Bird, GA1, then GA2. "
            "These quantities are limits, not guaranteed sales."
        ),
        early_bird_limit_input,
        ga1_limit_input,
        ga2_limit_input,
        mo.md("## Ticket prices"),
        mo.hstack([
            mo.vstack([
                mo.md("### Low"),
                low_early_input,
                low_ga1_input,
                low_ga2_input,
            ]),
            mo.vstack([
                mo.md("### Base"),
                base_early_input,
                base_ga1_input,
                base_ga2_input,
            ]),
            mo.vstack([
                mo.md("### High"),
                high_early_input,
                high_ga1_input,
                high_ga2_input,
            ]),
        ]),
    ])
    return (
        base_early_input,
        base_ga1_input,
        base_ga2_input,
        early_bird_limit_input,
        ga1_limit_input,
        ga2_limit_input,
        high_early_input,
        high_ga1_input,
        high_ga2_input,
        low_early_input,
        low_ga1_input,
        low_ga2_input,
    )


@app.cell
def _(
    allowance_input,
    bar_spend_input,
    base_early_input,
    base_ga1_input,
    base_ga2_input,
    capacity_input,
    early_bird_limit_input,
    food_cost_input,
    ga1_limit_input,
    ga2_limit_input,
    high_early_input,
    high_ga1_input,
    high_ga2_input,
    low_early_input,
    low_ga1_input,
    low_ga2_input,
    profit_goal_input,
    venue_minimum_input,
):
    # Read the current values from the input boxes.
    app_capacity = int(capacity_input.value)
    app_profit_goal = profit_goal_input.value
    app_food_cost = food_cost_input.value
    app_bar_spend = bar_spend_input.value
    app_venue_minimum = venue_minimum_input.value
    app_allowance = allowance_input.value

    app_allocations = [
        int(early_bird_limit_input.value),
        int(ga1_limit_input.value),
        int(ga2_limit_input.value),
    ]

    app_options = [
        {
            "name": "Low",
            "prices": [
                low_early_input.value,
                low_ga1_input.value,
                low_ga2_input.value,
            ],
        },
        {
            "name": "Base",
            "prices": [
                base_early_input.value,
                base_ga1_input.value,
                base_ga2_input.value,
            ],
        },
        {
            "name": "High",
            "prices": [
                high_early_input.value,
                high_ga1_input.value,
                high_ga2_input.value,
            ],
        },
    ]

    app_results = []

    for app_option in app_options:
        app_tickets = 0
        app_revenue = 0
        app_sales = [0, 0, 0]
        app_shortfall = app_venue_minimum
        app_expenses = app_allowance + app_shortfall
        app_profit = app_revenue - app_expenses
        app_reached = app_profit >= app_profit_goal

        # Positions 0, 1, and 2 represent Early Bird, GA1, and GA2.
        for app_tier_index in range(3):
            for app_ticket in range(app_allocations[app_tier_index]):

                if app_reached or app_tickets >= app_capacity:
                    break

                app_tickets = app_tickets + 1
                app_sales[app_tier_index] = app_sales[app_tier_index] + 1
                app_revenue = (
                    app_revenue + app_option["prices"][app_tier_index]
                )

                app_shortfall = (
                    app_venue_minimum - app_tickets * app_bar_spend
                )

                if app_shortfall < 0:
                    app_shortfall = 0

                app_expenses = (
                    app_tickets * app_food_cost
                    + app_allowance
                    + app_shortfall
                )

                app_profit = app_revenue - app_expenses
                app_reached = app_profit >= app_profit_goal

            if app_reached or app_tickets >= app_capacity:
                break

        app_results.append({
            "name": app_option["name"],
            "reached": app_reached,
            "tickets": app_tickets,
            "early_bird": app_sales[0],
            "ga1": app_sales[1],
            "ga2": app_sales[2],
            "revenue": app_revenue,
            "shortfall": app_shortfall,
            "profit": app_profit,
        })
    return app_profit_goal, app_results


@app.cell
def _(app_profit_goal, app_results, mo):
    app_table = (
        "| Option | Outcome | Total sold | Early Bird | GA1 | GA2 | "
        "Venue shortfall | Projected profit |\n"
        "|:--|:--|--:|--:|--:|--:|--:|--:|\n"
    )

    for app_display in app_results:
        if app_display["reached"]:
            app_outcome = "Goal reached"
        else:
            app_outcome = "Goal not reachable"

        app_table = app_table + (
            f"| {app_display['name']} "
            f"| {app_outcome} "
            f"| {app_display['tickets']} "
            f"| {app_display['early_bird']} "
            f"| {app_display['ga1']} "
            f"| {app_display['ga2']} "
            f"| ${app_display['shortfall']:,.2f} "
            f"| ${app_display['profit']:,.2f} |\n"
        )

    mo.vstack([
        mo.md("## Sales targets"),
        mo.md(f"**Projected profit goal: ${app_profit_goal:,.2f}**"),
        mo.md(app_table),
        mo.md(
            "For qualifying options, counts show the minimum sales needed. "
            "For unreachable goals, counts show the maximum sales tested."
        ),
        mo.md(
            "These projections assume each ticket sold represents one attendee "
            "and that attendees spend the estimated amount at the bar. "
            "They do not predict demand for tickets."
        ),
    ])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
