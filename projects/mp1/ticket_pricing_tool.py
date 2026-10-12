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
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    I would use this ticket pricing tool for my networking event company, Corporates Connect (Cc). My question is "for each of the three ticket-pricing options, what is the minimum total number of tickets I need to sell within each tier to reach $3,000 in projected profit after all expenses?"
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    Note that this was written for my original question.

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
    """)
    return


@app.cell
def _():
    # Event assumptions. These can change for each event.
    capacity = 300
    venue_minimum_spend = 4000
    estimated_bar_spend_per_attendee = 15
    food_cost_per_attendee = 10
    spending_allowance_buffer = 500
    profit_goal = 3000

    # Each dictionary contains prices and maximum available tickets.
    # Tickets sell in order: Early Bird, GA1, then GA2.
    pricing_options = [
        {
            "name": "Low",
            "tiers": [
                {"name": "Early Bird", "price": 10, "available": 50},
                {"name": "GA1", "price": 15, "available": 150},
                {"name": "GA2", "price": 20, "available": 100},
            ],
        },
        {
            "name": "Base",
            "tiers": [
                {"name": "Early Bird", "price": 35, "available": 50},
                {"name": "GA1", "price": 40, "available": 150},
                {"name": "GA2", "price": 50, "available": 100},
            ],
        },
        {
            "name": "High",
            "tiers": [
                {"name": "Early Bird", "price": 50, "available": 50},
                {"name": "GA1", "price": 70, "available": 150},
                {"name": "GA2", "price": 100, "available": 100},
            ],
        },
    ]

    # Added for going further

    bar_spend_scenarios = [10, 15, 20]
    return (
        bar_spend_scenarios,
        capacity,
        estimated_bar_spend_per_attendee,
        food_cost_per_attendee,
        pricing_options,
        profit_goal,
        spending_allowance_buffer,
        venue_minimum_spend,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work
    """)
    return


@app.cell
def _(
    capacity,
    estimated_bar_spend_per_attendee,
    food_cost_per_attendee,
    pricing_options,
    profit_goal,
    spending_allowance_buffer,
    venue_minimum_spend,
):
    results = []

    for option in pricing_options:
        # Start this option with no ticket sales.
        tickets_sold = 0
        ticket_revenue = 0
        food_expense = 0
        estimated_bar_spend = 0

        minimum_spend_shortfall = venue_minimum_spend
        total_expenses = spending_allowance_buffer + minimum_spend_shortfall
        projected_profit = ticket_revenue - total_expenses

        goal_reached = projected_profit >= profit_goal

        # Track how many tickets sell in each tier.
        sales_by_tier = {}

        for tier in option["tiers"]:
            sales_by_tier[tier["name"]] = 0

        # Sell through the tiers in their listed order.
        for tier in option["tiers"]:

            # Try selling up to this tier's available allocation.
            for ticket_number in range(tier["available"]):

                # Stop if the goal or venue capacity is reached.
                if goal_reached or tickets_sold >= capacity:
                    break

                # Add one ticket sale.
                tickets_sold = tickets_sold + 1
                ticket_revenue = ticket_revenue + tier["price"]

                sales_by_tier[tier["name"]] = (
                    sales_by_tier[tier["name"]] + 1
                )

                # Calculate spending and expenses at this attendance.
                estimated_bar_spend = (
                    tickets_sold * estimated_bar_spend_per_attendee
                )

                minimum_spend_shortfall = (
                    venue_minimum_spend - estimated_bar_spend
                )

                if minimum_spend_shortfall < 0:
                    minimum_spend_shortfall = 0

                food_expense = tickets_sold * food_cost_per_attendee

                total_expenses = (
                    food_expense
                    + spending_allowance_buffer
                    + minimum_spend_shortfall
                )

                projected_profit = ticket_revenue - total_expenses

                # Check whether this sale reaches the profit goal.
                if projected_profit >= profit_goal:
                    goal_reached = True

            # Stop moving through tiers if the goal or capacity is reached.
            if goal_reached or tickets_sold >= capacity:
                break

        # Save this option's outcome after its selling loops finish.
        result = {
            "name": option["name"],
            "goal_reached": goal_reached,
            "sales_by_tier": sales_by_tier,
            "tickets_sold": tickets_sold,
            "ticket_revenue": ticket_revenue,
            "food_expense": food_expense,
            "estimated_bar_spend": estimated_bar_spend,
            "minimum_spend_shortfall": minimum_spend_shortfall,
            "total_expenses": total_expenses,
            "projected_profit": projected_profit,
        }

        results.append(result)
    return (results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    Under my current assumptions, the base option requires at least 173 ticket sales (50 Early Bird and 123 GA1) to produce $3,035 in projected profit, while the high option requires 114 sales (50 Early Bird and 64 GA1) to produce $3,050; the low option cannot reach the $3,000 goal even after selling all 300 available tickets.
    """)
    return


@app.cell
def _(results):
    print(
        f"{'Option':<8} {'Early Bird':>10} {'GA1':>6} {'GA2':>6} "
        f"{'Total':>7} {'Profit ($)':>12} {'Outcome':<20}"
    )

    for answer in results:
        if answer["goal_reached"]:
            outcome = "Goal reached"
        else:
            outcome = "Goal not reachable"

        print(
            f"{answer['name']:<8} "
            f"{answer['sales_by_tier']['Early Bird']:>10} "
            f"{answer['sales_by_tier']['GA1']:>6} "
            f"{answer['sales_by_tier']['GA2']:>6} "
            f"{answer['tickets_sold']:>7} "
            f"{answer['projected_profit']:>12,.2f} "
            f"{outcome:<20}"
        )

    print()
    print("For an option that cannot reach the goal, counts show all tickets tested.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right
    """)
    return


@app.cell
def _(profit_goal, results):
    # Fixed manual checks for my current inputs.
    # Profit = ticket revenue - food - allowance - bar shortfall.

    low_check = (50 * 10 + 150 * 15 + 100 * 20) - 3000 - 500 - 0
    base_check = (50 * 35 + 123 * 40) - 1730 - 500 - 1405
    high_check = (50 * 50 + 64 * 70) - 1140 - 500 - 2290

    print(f"{'Option':<8} {'Manual profit':>15} {'Tool profit':>15}")
    print(f"{'Low':<8} {low_check:>15,.2f} {results[0]['projected_profit']:>15,.2f}")
    print(f"{'Base':<8} {base_check:>15,.2f} {results[1]['projected_profit']:>15,.2f}")
    print(f"{'High':<8} {high_check:>15,.2f} {results[2]['projected_profit']:>15,.2f}")

    # One fewer ticket removes its price, saves $10 in food,
    # and increases the bar shortfall by $15.
    base_one_fewer = base_check - 40 + 10 - 15
    high_one_fewer = high_check - 70 + 10 - 15

    print()
    print(f"Goal: ${profit_goal:,.2f}")
    print(f"Base with 172 tickets: ${base_one_fewer:,.2f}")
    print(f"High with 113 tickets: ${high_one_fewer:,.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I checked the tool’s profit calculations by separately multiplying tickets sold in each tier by their prices, then subtracting food costs, the $500 spending allowance, and any venue minimum-spend shortfall. My calculations matched the tool: $1,250 for Low, $3,035 for Base, and $3,050 for High.

    I also checked one fewer ticket for the options that met my $3,000 goal. Base produced $2,990 with 172 tickets, compared with $3,035 with 173. High produced $2,975 with 113 tickets, compared with $3,050 with 114. Because profit increases with each sale under my current assumptions, these checks confirm the minimum sales needed. Low did not meet the goal even with all 300 tickets sold.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    The agent helped me reframe my original question around finding the lowest average ticket price that would produce at least $3,000 in projected profit without exceeding venue capacity. I did not keep that approach because I needed to input a number of tickets sold for each combination. Instead, I wanted the tool to tell me how many tickets I needed to sell. When I am planning events I am most stressed about not selling "enough" tickets but find it hard to know what the amount I need to sell is. Therefore, I changed my question to match what I felt is more important versus keeping the question that my Agent thought was better.

    I wanted to find the minimum ticket sales needed for each pricing option: low, base, and high. Ticket quantities now represent the maximum available in each tier, rather than assumed sales. The tool adds sales one at a time in order for Early Bird, GA1, then GA2 until it reaches the profit goal of $3,000 or reaches a ticket or capacity limit.

    The revised question appears in Section 1, and the ticket-by-ticket calculation is in the code cell under Section 4. I verified the results in Section 6 by calculating profit independently and checking that one fewer ticket would miss the goal for the base and high options.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    I extended the tool to compare estimated bar spending of $10, $15, and $20 per attendee. The code cell in Section 8 recalculates the minimum ticket sales needed for each pricing option.

    For the base option, the required sales were 194, 173, and 155 tickets respectively. For the high option, they were 122, 114, and 107. The low option could not reach the profit goal in any scenario.

    This showed that lower bar spending increases the ticket sales needed to cover the venue shortfall and reach my profit goal.
    """)
    return


@app.cell
def _(
    bar_spend_scenarios,
    capacity,
    food_cost_per_attendee,
    pricing_options,
    profit_goal,
    spending_allowance_buffer,
    venue_minimum_spend,
):
    extension_results = []

    for extension_option in pricing_options:
        for extension_bar_spend in bar_spend_scenarios:

            # Start this pricing and bar-spending scenario from zero.
            extension_tickets = 0
            extension_revenue = 0
            extension_profit = (
                -spending_allowance_buffer - venue_minimum_spend
            )
            extension_goal_reached = extension_profit >= profit_goal

            # Sell Early Bird first, then GA1, then GA2.
            for extension_tier in extension_option["tiers"]:
                for extension_ticket in range(extension_tier["available"]):

                    if extension_goal_reached or extension_tickets >= capacity:
                        break

                    # Add one ticket sale.
                    extension_tickets = extension_tickets + 1
                    extension_revenue = (
                        extension_revenue + extension_tier["price"]
                    )

                    # Use this scenario's bar-spending estimate.
                    extension_shortfall = (
                        venue_minimum_spend
                        - extension_tickets * extension_bar_spend
                    )

                    if extension_shortfall < 0:
                        extension_shortfall = 0

                    extension_profit = (
                        extension_revenue
                        - extension_tickets * food_cost_per_attendee
                        - spending_allowance_buffer
                        - extension_shortfall
                    )

                    extension_goal_reached = extension_profit >= profit_goal

                if extension_goal_reached or extension_tickets >= capacity:
                    break

            extension_results.append({
                "option": extension_option["name"],
                "bar_spend": extension_bar_spend,
                "tickets": extension_tickets,
                "profit": extension_profit,
                "goal_reached": extension_goal_reached,
            })

    # Display all scenarios.
    print(
        f"{'Option':<8} {'Bar/person ($)':>15} "
        f"{'Min tickets':>12} {'Profit ($)':>12} {'Outcome':<20}"
    )

    for extension_row in extension_results:
        if extension_row["goal_reached"]:
            extension_minimum = str(extension_row["tickets"])
            extension_status = "Goal reached"
        else:
            extension_minimum = "--"
            extension_status = "Goal not reachable"

        print(
            f"{extension_row['option']:<8} "
            f"{extension_row['bar_spend']:>15,.2f} "
            f"{extension_minimum:>12} "
            f"{extension_row['profit']:>12,.2f} "
            f"{extension_status:<20}"
        )

    print()
    print("For unreachable goals, profit is shown at the maximum sales tested.")
    return


if __name__ == "__main__":
    app.run()
