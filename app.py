import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# SportaMath Lab
# Version: v2.0
#
# Module 1: Race Pacing Simulator
# Module 2: Basketball Shot Probability Visualizer
#
# Goal:
# Help middle and high school students learn math through
# interactive sports simulations.
# ------------------------------------------------------------


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="SportaMath Lab",
    page_icon="🏀",
    layout="wide"
)


# -----------------------------
# General helper functions
# -----------------------------

def format_time(seconds):
    """
    Converts seconds into minutes:seconds format.
    Example: 320 seconds becomes 5:20.0
    """
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:04.1f}"


def make_bar_chart(labels, values, y_label, title):
    """
    Creates a simple bar chart with value labels.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(labels, values)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)

    max_value = max(values) if len(values) > 0 else 0
    label_padding = max(max_value * 0.02, 0.5)
    ax.set_ylim(0, max_value + label_padding * 4)

    for index, value in enumerate(values):
        ax.text(
            index,
            value + label_padding,
            f"{value:.1f}" if isinstance(value, float) else f"{value}",
            ha="center",
            va="bottom"
        )

    return fig


# -----------------------------
# Race module helper functions
# -----------------------------

def get_race_segments(race):
    """
    Returns the number of segments and segment name for each race.
    For 800m and 1600m, we use 400m laps.
    For 5K, we use 1K segments.
    """
    if race == "800m":
        return 2, "400m"
    elif race == "1600m":
        return 4, "400m"
    else:
        return 5, "1K"


def get_race_distance_meters(race):
    """
    Returns the race distance in meters.
    """
    if race == "800m":
        return 800
    elif race == "1600m":
        return 1600
    else:
        return 5000


def normalize_splits(raw_splits, target_total):
    """
    Adjusts a pacing strategy so that the splits add up to the target goal time.
    This lets every strategy finish in the same total time.
    """
    current_total = sum(raw_splits)
    scale_factor = target_total / current_total
    return [split * scale_factor for split in raw_splits]


def explain_time_difference(difference):
    """
    Explains whether the user's custom pacing plan is faster or slower than the goal.
    """
    if abs(difference) < 0.5:
        return "You matched the goal almost exactly."
    elif difference > 0:
        return f"You are {difference:.1f} seconds slower than the goal."
    else:
        return f"You are {abs(difference):.1f} seconds faster than the goal."


def create_pacing_strategies(average_split, segments, total_seconds):
    """
    Creates three pacing strategies:
    1. Even pace
    2. Fast start
    3. Negative split
    """
    even_splits = [average_split] * segments

    fast_start_raw = np.linspace(
        average_split * 0.94,
        average_split * 1.06,
        segments
    )
    fast_start_splits = normalize_splits(fast_start_raw, total_seconds)

    negative_raw = np.linspace(
        average_split * 1.06,
        average_split * 0.94,
        segments
    )
    negative_splits = normalize_splits(negative_raw, total_seconds)

    return even_splits, fast_start_splits, negative_splits


def calculate_consistency_score(splits):
    """
    Calculates variation using standard deviation.
    Lower standard deviation means more consistent pacing.
    """
    return np.std(splits)


def calculate_speed_metrics(distance_meters, total_seconds):
    """
    Calculates speed and pace using unit conversion.
    """
    meters_per_second = distance_meters / total_seconds
    miles_per_hour = meters_per_second * 2.23694

    meters_per_mile = 1609.344
    distance_miles = distance_meters / meters_per_mile
    mile_pace_seconds = total_seconds / distance_miles

    return meters_per_second, miles_per_hour, mile_pace_seconds


def calculate_accuracy_score(difference):
    """
    Gives a score from 0 to 100 based on how close the custom plan is to the goal time.
    Each second away from the goal reduces the score by 5 points.
    """
    score = 100 - abs(difference) * 5
    return max(0, min(100, score))


def calculate_consistency_component(variation, target_variation):
    """
    Gives a score from 0 to 100 based on how low the pacing variation is.
    Lower variation gives a higher score.
    """
    score = 100 - (variation / target_variation) * 30
    return max(0, min(100, score))


def calculate_optimization_score(accuracy_score, consistency_component):
    """
    Combines accuracy and consistency into one optimization score.
    """
    return (accuracy_score * 0.6) + (consistency_component * 0.4)


def give_optimization_feedback(difference, variation, target_variation, optimization_score):
    """
    Gives student-friendly feedback based on the user's custom pacing plan.
    """
    if optimization_score >= 90:
        return "Excellent optimization. Your plan is close to the goal time and keeps pacing controlled."
    elif abs(difference) > 5:
        return "Focus first on getting closer to the goal time. Your total time is the biggest issue right now."
    elif variation > target_variation:
        return "Your time is close, but your splits vary too much. Try making your segment times more even."
    else:
        return "Good plan. You are balancing time accuracy and pacing consistency reasonably well."


def make_strategy_graph(x, segment_name, even_splits, fast_start_splits, negative_splits):
    """
    Creates the pacing strategy comparison graph.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(x, even_splits, marker="o", label="Even Pace")
    ax.plot(x, fast_start_splits, marker="o", label="Fast Start")
    ax.plot(x, negative_splits, marker="o", label="Negative Split")

    ax.set_xlabel("Race Segment")
    ax.set_ylabel(f"Seconds per {segment_name}")
    ax.set_title("Comparing Pacing Strategies")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


def make_custom_graph(x, segment_name, custom_splits, average_split):
    """
    Creates the user's custom pacing graph for Challenge Mode.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(x, custom_splits, marker="o", label="Your Plan")
    ax.axhline(average_split, linestyle="--", label="Goal Average Split")

    ax.set_xlabel("Race Segment")
    ax.set_ylabel(f"Seconds per {segment_name}")
    ax.set_title("Your Custom Pacing Plan")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


# -----------------------------
# Basketball module helper functions
# -----------------------------

def calculate_expected_points(shot_value, make_percentage):
    """
    Expected points = shot value times make probability.
    """
    make_probability = make_percentage / 100
    return shot_value * make_probability


def compare_shots(expected_two, expected_three):
    """
    Compares expected points for 2-point and 3-point shots.
    """
    if abs(expected_two - expected_three) < 0.01:
        return "About equal"
    elif expected_two > expected_three:
        return "2-point shot"
    else:
        return "3-point shot"


def calculate_break_even_three_percentage(expected_two):
    """
    Calculates what 3-point percentage is needed to match the expected points
    of the 2-point shot.
    """
    return (expected_two / 3) * 100


def make_expected_points_chart(expected_two, expected_three):
    """
    Creates a bar chart comparing expected points per shot.
    """
    fig, ax = plt.subplots(figsize=(7, 4))

    shot_types = ["2-point shot", "3-point shot"]
    expected_values = [expected_two, expected_three]

    ax.bar(shot_types, expected_values)
    ax.set_ylabel("Expected points per shot")
    ax.set_title("Expected Points Comparison")
    ax.grid(axis="y", alpha=0.3)

    max_value = max(expected_values)
    label_padding = max(max_value * 0.02, 0.03)
    ax.set_ylim(0, max_value + label_padding * 5 + 0.1)

    for index, value in enumerate(expected_values):
        ax.text(
            index,
            value + label_padding,
            f"{value:.2f}",
            ha="center",
            va="bottom"
        )

    return fig


def simulate_shots(shot_value, make_percentage, possessions, seed):
    """
    Simulates a fixed number of shot attempts.
    Each possession becomes one shot attempt.
    The seed controls which random scenario is generated.
    """
    make_probability = make_percentage / 100
    rng = np.random.default_rng(seed)
    makes = rng.binomial(possessions, make_probability)
    misses = possessions - makes
    total_points = makes * shot_value

    return makes, misses, total_points


def make_simulation_chart(two_point_total, three_point_total, expected_two_total, expected_three_total):
    """
    Creates a chart comparing simulated and expected totals.
    """
    labels = [
        "2PT simulated",
        "3PT simulated",
        "2PT expected",
        "3PT expected"
    ]

    values = [
        two_point_total,
        three_point_total,
        expected_two_total,
        expected_three_total
    ]

    return make_bar_chart(
        labels,
        values,
        "Total points",
        "Simulated Points vs Expected Points"
    )


def simulate_mixed_strategy(
    two_point_percentage,
    three_point_percentage,
    possessions,
    three_point_share,
    seed
):
    """
    Simulates a mixed basketball strategy.
    Some possessions become 2-point attempts.
    Some possessions become 3-point attempts.
    """
    three_attempts = int(round(possessions * three_point_share / 100))
    two_attempts = possessions - three_attempts

    rng = np.random.default_rng(seed)

    two_makes = rng.binomial(two_attempts, two_point_percentage / 100)
    three_makes = rng.binomial(three_attempts, three_point_percentage / 100)

    two_points = two_makes * 2
    three_points = three_makes * 3
    total_points = two_points + three_points

    return two_attempts, three_attempts, two_makes, three_makes, total_points


def calculate_strategy_expected_total(
    two_attempts,
    three_attempts,
    expected_two,
    expected_three
):
    """
    Calculates the expected total points for a mixed 2PT/3PT strategy.
    """
    return (two_attempts * expected_two) + (three_attempts * expected_three)


def calculate_strategy_score(strategy_expected_total, best_expected_total):
    """
    Scores a mixed strategy against the best pure expected-value strategy.
    """
    if best_expected_total <= 0:
        return 0

    score = (strategy_expected_total / best_expected_total) * 100
    return max(0, min(100, score))


def give_basketball_challenge_feedback(
    three_point_share,
    expected_two,
    expected_three,
    strategy_score
):
    """
    Gives feedback for the basketball mixed-strategy challenge.
    """
    if strategy_score >= 98:
        return "Excellent strategy. Your shot mix is very close to the best expected-value choice."
    elif expected_three > expected_two and three_point_share < 50:
        return "The 3-point shot has higher expected value right now, so try increasing the 3-point attempt share."
    elif expected_two > expected_three and three_point_share > 50:
        return "The 2-point shot has higher expected value right now, so try lowering the 3-point attempt share."
    elif abs(expected_two - expected_three) < 0.01:
        return "The two shots are almost equal in expected value, so many shot mixes can be reasonable."
    else:
        return "Good attempt. Adjust the shot mix and watch how the strategy score changes."


def make_mixed_strategy_chart(two_attempts, three_attempts, two_makes, three_makes):
    """
    Creates a chart showing attempts and makes for the mixed strategy.
    """
    labels = [
        "2PT attempts",
        "2PT makes",
        "3PT attempts",
        "3PT makes"
    ]

    values = [
        two_attempts,
        two_makes,
        three_attempts,
        three_makes
    ]

    return make_bar_chart(
        labels,
        values,
        "Number of possessions",
        "Challenge Strategy: Attempts and Makes"
    )


# -----------------------------
# Project overview
# -----------------------------

def render_project_overview():
    st.title("🏀🏃 SportaMath Lab")
    st.subheader("Interactive Math Through Sports")
    st.caption("v2.0 — Complete Two-Module Demo")

    st.markdown(
        """
        **SportaMath Lab** is an interactive educational app that helps middle and high school students
        learn math through sports simulations.

        The project connects abstract math ideas to decisions athletes and coaches actually make:
        pacing a race, comparing shot choices, understanding randomness, and optimizing strategy.
        """
    )

    st.success(
        "Project status: v2.0 complete. The app now has two working modules and is ready for demo, user testing, and portfolio documentation."
    )

    st.info(
        "Mission: Make math feel visible, useful, and fun by connecting it to sports."
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric("Modules", "2")

    with metric_col2:
        st.metric("Main Sports", "Running + Basketball")

    with metric_col3:
        st.metric("Version", "v2.0")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Modules",
            "Math Concepts",
            "Design Process",
            "Demo Guide"
        ]
    )

    with tab1:
        st.header("Current Modules")

        st.subheader("Module 1: Race Pacing Simulator")

        st.write(
            "Students choose a race distance and goal time, compare pacing strategies, "
            "study graphs, and build their own pacing plan in Challenge Mode."
        )

        st.markdown(
            """
            **Concepts:** averages, rates, unit conversion, graph interpretation,
            standard deviation, constraints, and optimization.
            """
        )

        st.subheader("Module 2: Basketball Shot Probability Visualizer")

        st.write(
            "Students enter shooting percentages, compare expected points, simulate possessions, "
            "and build a shot-selection strategy."
        )

        st.markdown(
            """
            **Concepts:** probability, expected value, break-even analysis,
            randomness, simulation, and strategic decision-making.
            """
        )

    with tab2:
        st.header("Math Concepts Across the App")

        concept_data = pd.DataFrame({
            "Concept": [
                "Average",
                "Rate",
                "Unit conversion",
                "Variation",
                "Graph interpretation",
                "Optimization",
                "Probability",
                "Expected value",
                "Simulation",
                "Break-even analysis"
            ],
            "Where it appears": [
                "Race average split",
                "Race speed and pace",
                "Meters/second, mph, mile pace",
                "Race split consistency",
                "Race and basketball charts",
                "Race pacing and basketball strategy scores",
                "Basketball make percentages",
                "2PT and 3PT shot value comparison",
                "Random possession outcomes",
                "3PT percentage needed to match 2PT expected value"
            ]
        })

        st.table(concept_data)

    with tab3:
        st.header("Design Process")

        st.markdown(
            """
            This project was built in stages:

            1. Built a working Race Pacing Simulator.
            2. Added layout polish with sidebar controls, tabs, metrics, and graphs.
            3. Added beginner and advanced explanations.
            4. Added optimization scoring for race pacing.
            5. Added Basketball Shot Probability as a second module.
            6. Added expected points, charts, simulation, and strategy challenge.
            7. Polished the app into a two-module demo.
            """
        )

        st.subheader("Engineering and Modeling Thinking")

        st.write(
            "Both modules are simplified models. They do not claim to perfectly predict sports performance. "
            "Instead, they isolate important variables so students can explore how inputs affect outcomes."
        )

        st.subheader("Current Limitations")

        st.markdown(
            """
            - Race module does not include hills, fatigue, wind, terrain, or biomechanics.
            - Basketball module does not include defense, rebounding, turnovers, fouls, or player fatigue.
            - Scoring systems are simplified and could be improved with real data.
            - Future versions could include real datasets, user accounts, or more sports modules.
            """
        )

    with tab4:
        st.header("Suggested Demo Guide")

        st.subheader("Demo 1: Race Pacing")

        st.markdown(
            """
            1. Choose **Race Pacing Simulator** from the sidebar.
            2. Set race to **1600m** and goal time to **5:20**.
            3. Show the strategy comparison table and graph.
            4. Open Challenge Mode and adjust splits.
            5. Explain how the optimization score balances goal accuracy and consistency.
            """
        )

        st.subheader("Demo 2: Basketball Probability")

        st.markdown(
            """
            1. Choose **Basketball Shot Probability** from the sidebar.
            2. Use **50% 2PT** and **35% 3PT** as starting values.
            3. Show expected points and the chart.
            4. Change the simulation scenario to show randomness.
            5. Open Challenge Mode and test different 3-point attempt shares.
            """
        )

        st.subheader("Portfolio Summary")

        st.write(
            "A strong one-sentence description: "
            "**Built SportaMath Lab, a Python/Streamlit educational app that teaches math through interactive running and basketball simulations, including pacing optimization, expected value, and probability-based strategy.**"
        )


# -----------------------------
# Race module render function
# -----------------------------

def render_race_module(learning_mode):
    st.sidebar.write("Race Pacing Simulator")

    race = st.sidebar.selectbox(
        "Choose a race distance:",
        ["800m", "1600m", "5K"]
    )

    goal_minutes = st.sidebar.number_input(
        "Goal minutes:",
        min_value=0,
        max_value=60,
        value=5
    )

    goal_seconds = st.sidebar.number_input(
        "Goal seconds:",
        min_value=0,
        max_value=59,
        value=20
    )

    st.sidebar.markdown("---")

    st.sidebar.info(
        "Set a race goal, compare pacing strategies, then use Challenge Mode to design your own pacing plan."
    )

    total_seconds = goal_minutes * 60 + goal_seconds

    if total_seconds <= 0:
        st.error("Please enter a goal time greater than 0 seconds.")
        st.stop()

    segments, segment_name = get_race_segments(race)
    distance_meters = get_race_distance_meters(race)
    average_split = total_seconds / segments

    meters_per_second, miles_per_hour, mile_pace_seconds = calculate_speed_metrics(
        distance_meters,
        total_seconds
    )

    even_splits, fast_start_splits, negative_splits = create_pacing_strategies(
        average_split,
        segments,
        total_seconds
    )

    data = pd.DataFrame({
        "Segment": [f"{segment_name} {i+1}" for i in range(segments)],
        "Even Pace": even_splits,
        "Fast Start": fast_start_splits,
        "Negative Split": negative_splits
    })

    display_data = data.copy()

    for column in ["Even Pace", "Fast Start", "Negative Split"]:
        display_data[column] = display_data[column].apply(format_time)

    even_std = calculate_consistency_score(even_splits)
    fast_start_std = calculate_consistency_score(fast_start_splits)
    negative_std = calculate_consistency_score(negative_splits)

    variation_scores = {
        "Even Pace": even_std,
        "Fast Start": fast_start_std,
        "Negative Split": negative_std
    }

    most_consistent = min(variation_scores, key=variation_scores.get)
    x = list(range(1, segments + 1))

    st.title("🏃 SportaMath Lab")
    st.subheader("Module 1: Race Pacing Simulator")
    st.caption("v2.0 — Complete Two-Module Demo")

    st.markdown(
        """
        This module uses race pacing to teach averages, rate, unit conversion,
        variation, graph interpretation, and optimization.
        """
    )

    st.success(
        "Module status: complete. This module is part of the v2.0 two-module SportaMath Lab app."
    )

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

    with metric_col1:
        st.metric("Race", race)

    with metric_col2:
        st.metric("Goal Time", f"{goal_minutes}:{goal_seconds:02d}")

    with metric_col3:
        st.metric(f"Average {segment_name} Split", format_time(average_split))

    with metric_col4:
        st.metric("Speed", f"{meters_per_second:.2f} m/s")

    with metric_col5:
        st.metric("Mile Pace", format_time(mile_pace_seconds))

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Strategy Comparison",
            "Challenge Mode",
            "Learn the Math",
            "Project Info"
        ]
    )

    with tab1:
        st.header("Strategy Comparison")

        st.write(
            "All three strategies below reach the same goal time, but they distribute effort differently."
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Pacing Strategy Table")
            st.table(display_data)

        with col2:
            st.subheader("Consistency Score")
            st.write(f"Even pace variation: **{even_std:.2f} seconds**")
            st.write(f"Fast start variation: **{fast_start_std:.2f} seconds**")
            st.write(f"Negative split variation: **{negative_std:.2f} seconds**")
            st.info(f"The most consistent pacing strategy is: **{most_consistent}**")

        st.subheader("Pacing Strategy Graph")

        strategy_fig = make_strategy_graph(
            x,
            segment_name,
            even_splits,
            fast_start_splits,
            negative_splits
        )

        st.pyplot(strategy_fig)

        st.subheader("What should I notice?")

        st.write(
            "The average split tells us the overall pace needed to hit the goal time. "
            "However, it does not show whether the runner ran smoothly or unevenly."
        )

        st.write(
            "That is why we also look at variation. Two runners can finish in the same total time "
            "but have very different pacing patterns."
        )

    with tab2:
        st.header("Challenge Mode")
        st.subheader("Build Your Own Pacing Plan")

        st.write(
            "Adjust each split and try to match the goal time while keeping your pacing consistent."
        )

        target_variation = max(3, average_split * 0.04)

        st.success(
            f"Challenge: Hit the goal time while keeping variation near or below "
            f"{target_variation:.2f} seconds."
        )

        custom_splits = []

        slider_min = max(1, int(average_split - 30))
        slider_max = max(slider_min + 1, int(average_split + 30))
        slider_default = max(slider_min, min(slider_max, int(round(average_split))))

        for i in range(segments):
            split = st.slider(
                f"{segment_name} {i+1} split, in seconds",
                min_value=slider_min,
                max_value=slider_max,
                value=slider_default,
                step=1
            )
            custom_splits.append(split)

        custom_total = sum(custom_splits)
        difference = custom_total - total_seconds
        custom_variation = calculate_consistency_score(custom_splits)
        accuracy_score = calculate_accuracy_score(difference)
        consistency_component = calculate_consistency_component(custom_variation, target_variation)
        optimization_score = calculate_optimization_score(accuracy_score, consistency_component)

        result_col1, result_col2, result_col3, result_col4 = st.columns(4)

        with result_col1:
            st.metric("Your Total Time", format_time(custom_total))

        with result_col2:
            st.metric("Time Accuracy", f"{accuracy_score:.0f}/100")

        with result_col3:
            st.metric("Consistency", f"{consistency_component:.0f}/100")

        with result_col4:
            st.metric("Optimization", f"{optimization_score:.0f}/100")

        st.write(f"Goal time: **{format_time(total_seconds)}**")
        st.write(explain_time_difference(difference))
        st.write(f"Your pacing variation: **{custom_variation:.2f} seconds**")
        st.write(f"Target variation: **{target_variation:.2f} seconds**")

        feedback = give_optimization_feedback(
            difference,
            custom_variation,
            target_variation,
            optimization_score
        )

        st.info(feedback)

        if abs(difference) <= 1 and custom_variation <= target_variation:
            st.success("Excellent! You hit the goal and kept your pacing controlled.")
        elif abs(difference) <= 1:
            st.success("You hit the goal time, but your pacing could be more consistent.")
        elif custom_total < total_seconds:
            st.warning("You beat the goal time, but check whether the pacing plan is realistic.")
        else:
            st.warning("You missed the goal time. Try adjusting your splits.")

        if learning_mode == "Advanced":
            st.info(
                "Advanced note: This challenge has two competing goals: minimize time error "
                "and minimize variation. The optimization score weights time accuracy at 60% "
                "and consistency at 40%."
            )

        st.subheader("Your Pacing Graph")

        custom_fig = make_custom_graph(
            x,
            segment_name,
            custom_splits,
            average_split
        )

        st.pyplot(custom_fig)

    with tab3:
        st.header("Learn the Math")

        st.write(f"Current learning mode: **{learning_mode}**")

        if learning_mode == "Beginner":
            st.subheader("1. Average Split")

            st.write(
                "The average split tells us the time needed for each race segment "
                "if every segment is run at the same pace."
            )

            st.latex(r"\text{Average split} = \frac{\text{Total time}}{\text{Number of segments}}")

            st.write(
                f"For this race, the average {segment_name} split is **{format_time(average_split)}**."
            )

            st.subheader("2. Rate and Speed")

            st.latex(r"\text{Speed} = \frac{\text{Distance}}{\text{Time}}")

            st.write(
                f"This race is **{distance_meters} meters** long and the goal time is "
                f"**{total_seconds} seconds**, so the average speed is "
                f"**{meters_per_second:.2f} meters per second**."
            )

            st.subheader("3. Consistency")

            st.write(
                "Consistency means keeping splits close to each other. Lower variation means more consistent pacing."
            )

            st.subheader("4. Optimization")

            st.write(
                "Optimization means trying to make the best plan while following rules. "
                "Here, the goal is to get close to the target time while keeping the splits controlled."
            )

        else:
            st.subheader("1. Average as a Model")

            st.latex(r"\bar{x} = \frac{x_1 + x_2 + \cdots + x_n}{n}")

            st.write(
                f"The target average split is **{format_time(average_split)}**."
            )

            st.subheader("2. Rate and Unit Conversion")

            st.latex(r"v = \frac{d}{t}")

            st.write(f"Distance: **{distance_meters} meters**")
            st.write(f"Time: **{total_seconds} seconds**")
            st.write(f"Average speed: **{meters_per_second:.2f} m/s**")
            st.write(f"Converted speed: **{miles_per_hour:.2f} mph**")
            st.write(f"Equivalent mile pace: **{format_time(mile_pace_seconds)} per mile**")

            st.subheader("3. Standard Deviation and Variation")

            st.latex(
                r"\sigma = \sqrt{\frac{(x_1-\bar{x})^2 + (x_2-\bar{x})^2 + \cdots + (x_n-\bar{x})^2}{n}}"
            )

            st.write(
                "The simulator uses standard deviation to measure pacing variation."
            )

            st.subheader("4. Optimization Under Constraints")

            st.latex(
                r"\text{Optimization score} = 0.6(\text{time accuracy}) + 0.4(\text{consistency})"
            )

            st.write(
                "This is similar to engineering design because a strong solution needs to satisfy constraints, "
                "not just maximize one variable."
            )

    with tab4:
        st.header("Race Module Project Info")

        st.subheader("Purpose")

        st.write(
            "This module helps students understand how pacing decisions can be modeled mathematically."
        )

        st.subheader("Features")

        st.markdown(
            """
            - Race goal input
            - Pacing strategy comparison
            - Pacing graph
            - Consistency score
            - Challenge Mode
            - Rate and unit conversion
            - Beginner and Advanced learning modes
            - Optimization score
            """
        )

        st.subheader("Limitations")

        st.write(
            "This simplified model does not account for fatigue, hills, weather, terrain, tactics, or biomechanics."
        )


# -----------------------------
# Basketball module render function
# -----------------------------

def render_basketball_module(learning_mode):
    st.sidebar.write("Basketball Shot Probability")

    two_point_percentage = st.sidebar.slider(
        "2-point shot percentage:",
        min_value=0,
        max_value=100,
        value=50,
        step=1
    )

    three_point_percentage = st.sidebar.slider(
        "3-point shot percentage:",
        min_value=0,
        max_value=100,
        value=35,
        step=1
    )

    possessions = st.sidebar.slider(
        "Number of possessions:",
        min_value=10,
        max_value=500,
        value=100,
        step=10
    )

    simulation_seed = st.sidebar.number_input(
        "Simulation scenario:",
        min_value=1,
        max_value=9999,
        value=42,
        step=1,
        help="Changing the scenario creates a different random outcome without changing the shooting percentages."
    )

    st.sidebar.caption(
        "Same scenario = same random trial. Different scenario = different possible outcome."
    )

    st.sidebar.markdown("---")

    st.sidebar.info(
        "Change the shooting percentages, possessions, or simulation scenario to see how expected and simulated results change."
    )

    expected_two = calculate_expected_points(2, two_point_percentage)
    expected_three = calculate_expected_points(3, three_point_percentage)
    better_shot = compare_shots(expected_two, expected_three)
    difference = abs(expected_two - expected_three)
    break_even_three_percentage = calculate_break_even_three_percentage(expected_two)

    expected_two_total = expected_two * possessions
    expected_three_total = expected_three * possessions

    two_makes, two_misses, two_simulated_points = simulate_shots(
        2,
        two_point_percentage,
        possessions,
        simulation_seed
    )

    three_makes, three_misses, three_simulated_points = simulate_shots(
        3,
        three_point_percentage,
        possessions,
        simulation_seed + 1
    )

    st.title("🏀 SportaMath Lab")
    st.subheader("Module 2: Basketball Shot Probability Visualizer")
    st.caption("v2.0 — Complete Two-Module Demo")

    st.markdown(
        """
        This module helps students understand probability, expected value, risk and reward,
        randomness, simulation, and decision-making through basketball shot selection.
        """
    )

    st.success(
        "Module status: complete. This module is part of the v2.0 two-module SportaMath Lab app."
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("2PT Expected", f"{expected_two:.2f} pts/shot")

    with metric_col2:
        st.metric("3PT Expected", f"{expected_three:.2f} pts/shot")

    with metric_col3:
        st.metric("Better by EV", better_shot)

    with metric_col4:
        st.metric("Possessions", possessions)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Expected Points",
            "Shot Comparison Chart",
            "Possession Simulation",
            "Challenge Mode",
            "Learn the Math",
            "Project Info"
        ]
    )

    with tab1:
        st.header("Expected Points Calculator")

        st.write(
            "Expected points tells us the average number of points a shot is worth "
            "if the same shot is taken many times."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("2-Point Shot")

            st.write(f"Shot value: **2 points**")
            st.write(f"Make percentage: **{two_point_percentage}%**")
            st.write(f"Make probability: **{two_point_percentage / 100:.2f}**")

            st.latex(
                rf"\text{{Expected points}} = 2 \times {two_point_percentage / 100:.2f}"
            )

            st.metric("Expected 2PT Value", f"{expected_two:.2f} points/shot")

        with col2:
            st.subheader("3-Point Shot")

            st.write(f"Shot value: **3 points**")
            st.write(f"Make percentage: **{three_point_percentage}%**")
            st.write(f"Make probability: **{three_point_percentage / 100:.2f}**")

            st.latex(
                rf"\text{{Expected points}} = 3 \times {three_point_percentage / 100:.2f}"
            )

            st.metric("Expected 3PT Value", f"{expected_three:.2f} points/shot")

        st.subheader("Recommendation")

        if better_shot == "About equal":
            st.info(
                "The two shots are almost equal in expected value. Other factors like defense, spacing, "
                "rebounds, or game situation may matter more."
            )
        else:
            st.info(
                f"Based only on expected points, the stronger option is the **{better_shot}**."
            )

    with tab2:
        st.header("Shot Comparison Chart")

        comparison_data = pd.DataFrame({
            "Shot Type": ["2-point shot", "3-point shot"],
            "Shot Value": [2, 3],
            "Make Percentage": [
                f"{two_point_percentage}%",
                f"{three_point_percentage}%"
            ],
            "Expected Points": [
                round(expected_two, 2),
                round(expected_three, 2)
            ]
        })

        st.table(comparison_data)

        st.subheader("Visual Comparison")

        chart_fig = make_expected_points_chart(expected_two, expected_three)
        st.pyplot(chart_fig)

        st.subheader("Break-Even Point")

        st.write(
            "The break-even 3-point percentage tells us what 3-point percentage would be needed "
            "to match the expected points of the current 2-point shot."
        )

        st.metric(
            "Break-even 3PT percentage",
            f"{break_even_three_percentage:.1f}%"
        )

        if three_point_percentage >= break_even_three_percentage:
            st.success(
                "At this 3-point percentage, the 3-point shot matches or beats the expected value of the 2-point shot."
            )
        else:
            st.warning(
                "At this 3-point percentage, the 3-point shot has lower expected value than the 2-point shot."
            )

    with tab3:
        st.header("Possession Simulation")

        st.write(
            "Expected value describes the long-run average. Simulation shows what might happen "
            "over a specific number of possessions."
        )

        st.info(
            "Each possession is modeled as one shot attempt. This simplified version does not yet include fouls, turnovers, rebounds, or shot selection changes."
        )

        st.info(
            f"Simulation scenario **{simulation_seed}** controls the random trial. "
            "Keeping the same scenario recreates the same simulated result. "
            "Changing the scenario creates a different possible outcome with the same shooting percentages."
        )

        result_col1, result_col2 = st.columns(2)

        with result_col1:
            st.subheader("2-Point Strategy")

            st.metric("Simulated Makes", f"{two_makes}/{possessions}")
            st.metric("Simulated Points", two_simulated_points)
            st.metric("Expected Total Points", f"{expected_two_total:.1f}")

            st.write(
                f"This simulation made **{two_makes}** two-point shots and missed **{two_misses}**."
            )

        with result_col2:
            st.subheader("3-Point Strategy")

            st.metric("Simulated Makes", f"{three_makes}/{possessions}")
            st.metric("Simulated Points", three_simulated_points)
            st.metric("Expected Total Points", f"{expected_three_total:.1f}")

            st.write(
                f"This simulation made **{three_makes}** three-point shots and missed **{three_misses}**."
            )

        st.subheader("Simulation Chart")

        simulation_fig = make_simulation_chart(
            two_simulated_points,
            three_simulated_points,
            expected_two_total,
            expected_three_total
        )

        st.pyplot(simulation_fig)

        st.write(
            "Try changing the simulation scenario. The expected values stay the same, but the simulated results may change."
        )

    with tab4:
        st.header("Basketball Challenge Mode")
        st.subheader("Build Your Own Shot Strategy")

        st.write(
            "Choose what percentage of possessions should be 3-point attempts. "
            "The rest will be 2-point attempts."
        )

        st.success(
            "Challenge: Build a shot strategy that gets as close as possible to the best expected-value strategy."
        )

        three_point_share = st.slider(
            "What percentage of possessions should be 3-point attempts?",
            min_value=0,
            max_value=100,
            value=50,
            step=5
        )

        two_attempts, three_attempts, challenge_two_makes, challenge_three_makes, challenge_total_points = simulate_mixed_strategy(
            two_point_percentage,
            three_point_percentage,
            possessions,
            three_point_share,
            simulation_seed + 10
        )

        challenge_expected_total = calculate_strategy_expected_total(
            two_attempts,
            three_attempts,
            expected_two,
            expected_three
        )

        best_expected_total = max(expected_two_total, expected_three_total)

        strategy_score = calculate_strategy_score(
            challenge_expected_total,
            best_expected_total
        )

        feedback = give_basketball_challenge_feedback(
            three_point_share,
            expected_two,
            expected_three,
            strategy_score
        )

        challenge_col1, challenge_col2, challenge_col3, challenge_col4 = st.columns(4)

        with challenge_col1:
            st.metric("2PT Attempts", two_attempts)

        with challenge_col2:
            st.metric("3PT Attempts", three_attempts)

        with challenge_col3:
            st.metric("Expected Points", f"{challenge_expected_total:.1f}")

        with challenge_col4:
            st.metric("Strategy Score", f"{strategy_score:.0f}/100")

        st.subheader("Simulated Result")

        sim_col1, sim_col2, sim_col3 = st.columns(3)

        with sim_col1:
            st.metric("2PT Makes", f"{challenge_two_makes}/{two_attempts}")

        with sim_col2:
            st.metric("3PT Makes", f"{challenge_three_makes}/{three_attempts}")

        with sim_col3:
            st.metric("Simulated Points", challenge_total_points)

        st.info(feedback)

        if strategy_score >= 98:
            st.success(
                "Strong strategy. Based on expected value, your shot mix is very close to optimal."
            )
        elif strategy_score >= 90:
            st.info(
                "Reasonable strategy. It is not perfect, but it captures much of the available expected value."
            )
        else:
            st.warning(
                "This strategy leaves expected points on the table. Try shifting toward the shot with higher expected value."
            )

        st.subheader("Challenge Strategy Chart")

        challenge_fig = make_mixed_strategy_chart(
            two_attempts,
            three_attempts,
            challenge_two_makes,
            challenge_three_makes
        )

        st.pyplot(challenge_fig)

        st.subheader("What should I notice?")

        st.write(
            "The best strategy depends on expected value, not just the point value of the shot. "
            "If the 3-point shot has higher expected value, taking more threes usually improves the strategy score. "
            "If the 2-point shot has higher expected value, taking more twos usually improves the strategy score."
        )

        st.write(
            "However, the simulated result can still vary because basketball outcomes are random. "
            "That is why expected value is useful for long-term decision-making."
        )

    with tab5:
        st.header("Learn the Math")

        st.write(f"Current learning mode: **{learning_mode}**")

        if learning_mode == "Beginner":
            st.subheader("1. Probability")

            st.write(
                "Probability tells us how likely something is to happen. "
                "A 50% shot means we expect about 50 makes out of 100 similar shots."
            )

            st.subheader("2. Expected Points")

            st.write(
                "Expected points is the average value of a shot over many attempts."
            )

            st.latex(
                r"\text{Expected points} = \text{Shot value} \times \text{Make probability}"
            )

            st.write(
                f"Right now, the 2-point shot is worth **{expected_two:.2f} expected points**."
            )

            st.write(
                f"Right now, the 3-point shot is worth **{expected_three:.2f} expected points**."
            )

            st.subheader("3. Simulation")

            st.write(
                "A simulation uses randomness to model possible results. "
                "Even if one shot has better expected value, it may not always win in a short simulation."
            )

            st.write(
                "The simulation scenario chooses one random version of the results. "
                "Changing the scenario is like replaying the same experiment again."
            )

            st.subheader("4. Challenge Mode")

            st.write(
                "Challenge Mode asks you to build a strategy. "
                "You choose how often to take 2-point shots and how often to take 3-point shots."
            )

            st.write(
                "A strong strategy usually uses more of the shot with higher expected points."
            )

        else:
            st.subheader("1. Probability as a Decimal")

            st.write(
                "A shooting percentage can be converted into a probability by dividing by 100."
            )

            st.write(
                f"The current 2-point probability is **{two_point_percentage / 100:.2f}**."
            )

            st.write(
                f"The current 3-point probability is **{three_point_percentage / 100:.2f}**."
            )

            st.subheader("2. Expected Value Model")

            st.latex(
                r"E(X) = \text{point value} \times P(\text{make})"
            )

            st.write(
                f"For the 2-point shot: **2 × {two_point_percentage / 100:.2f} = {expected_two:.2f}**."
            )

            st.write(
                f"For the 3-point shot: **3 × {three_point_percentage / 100:.2f} = {expected_three:.2f}**."
            )

            st.subheader("3. Break-Even Analysis")

            st.latex(
                r"3p = \text{Expected points from 2PT shot}"
            )

            st.write(
                f"With the current 2-point expected value of **{expected_two:.2f}**, "
                f"the 3-point shot needs to be made at about **{break_even_three_percentage:.1f}%** "
                f"to break even."
            )

            st.subheader("4. Mixed Strategy Expected Value")

            st.write(
                "In Challenge Mode, the user chooses a mixed strategy with some 2-point attempts "
                "and some 3-point attempts."
            )

            st.latex(
                r"E(\text{strategy}) = n_2(2p_2) + n_3(3p_3)"
            )

            st.write(
                "Here, n₂ is the number of 2-point attempts, n₃ is the number of 3-point attempts, "
                "p₂ is the 2-point make probability, and p₃ is the 3-point make probability."
            )

            st.subheader("5. Simulation and Randomness")

            st.write(
                "The simulation uses a binomial model. Each shot attempt is treated as a make-or-miss trial "
                "with the same make probability."
            )

            st.latex(
                r"\text{Makes} \sim \text{Binomial}(\text{attempts}, p)"
            )

            st.write(
                "The expected value predicts the long-run average, but the simulation shows one possible outcome. "
                "This helps students distinguish between theoretical expectation and actual random results."
            )

            st.write(
                "The simulation scenario is the random seed. It makes the random trial reproducible: "
                "the same scenario gives the same result, while a different scenario gives a different possible result."
            )

            st.subheader("6. Model Assumptions")

            st.write(
                "This basketball model is simplified. It assumes independent shots and does not yet include fouls, "
                "free throws, rebounds, turnovers, defense, player fatigue, shot location, or game situation."
            )

    with tab6:
        st.header("Basketball Module Project Info")

        st.subheader("Purpose")

        st.write(
            "This module helps students understand how probability and expected value can guide basketball shot selection."
        )

        st.subheader("Features")

        st.markdown(
            """
            - 2PT and 3PT shooting percentage inputs
            - Expected points calculator
            - Shot comparison chart
            - Break-even 3PT percentage
            - Possession simulation
            - Simulation scenario explanation
            - Basketball Challenge Mode
            - Beginner and Advanced learning modes
            """
        )

        st.subheader("Limitations")

        st.write(
            "This simplified model assumes independent shots and does not include defense, fouls, free throws, rebounds, turnovers, fatigue, or game situation."
        )


# -----------------------------
# Sidebar and app routing
# -----------------------------

st.sidebar.title("SportaMath Lab")
st.sidebar.caption("Version v2.0")

selected_module = st.sidebar.selectbox(
    "Choose module:",
    [
        "Project Overview",
        "Race Pacing Simulator",
        "Basketball Shot Probability"
    ]
)

learning_mode = st.sidebar.selectbox(
    "Learning mode:",
    ["Beginner", "Advanced"]
)

st.sidebar.markdown("---")

if selected_module == "Project Overview":
    st.sidebar.info(
        "Start here to see the full project summary and demo guide."
    )
    render_project_overview()
elif selected_module == "Race Pacing Simulator":
    render_race_module(learning_mode)
else:
    render_basketball_module(learning_mode)
