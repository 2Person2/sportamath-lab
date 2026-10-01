import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# SportaMath Lab
# Version: v2.5
#
# v2.5 focus:
# - Bite-sized lessons
# - Measurable progress
# - Lesson checkpoints
# - Guided learning path
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
# Lesson progress setup
# -----------------------------

LESSONS = {
    "race_average": {
        "module": "Race",
        "title": "Race Lesson 1: Average Split",
        "goal": "Understand how total time becomes an average segment split."
    },
    "race_strategies": {
        "module": "Race",
        "title": "Race Lesson 2: Pacing Strategies",
        "goal": "Compare even pace, fast start, and negative split pacing."
    },
    "race_consistency": {
        "module": "Race",
        "title": "Race Lesson 3: Consistency and Variation",
        "goal": "Use variation to measure how steady a pacing plan is."
    },
    "race_challenge": {
        "module": "Race",
        "title": "Race Lesson 4: Pacing Challenge",
        "goal": "Build a pacing plan and improve an optimization score."
    },
    "basketball_probability": {
        "module": "Basketball",
        "title": "Basketball Lesson 1: Probability",
        "goal": "Convert shooting percentage into probability."
    },
    "basketball_expected": {
        "module": "Basketball",
        "title": "Basketball Lesson 2: Expected Points",
        "goal": "Use expected value to compare 2-point and 3-point shots."
    },
    "basketball_simulation": {
        "module": "Basketball",
        "title": "Basketball Lesson 3: Simulation",
        "goal": "Compare expected results with one random simulated outcome."
    },
    "basketball_challenge": {
        "module": "Basketball",
        "title": "Basketball Lesson 4: Strategy Challenge",
        "goal": "Choose a shot mix and evaluate the strategy score."
    }
}


def initialize_progress():
    if "completed_lessons" not in st.session_state:
        st.session_state.completed_lessons = {lesson_key: False for lesson_key in LESSONS}


def get_completed_count():
    return sum(1 for is_done in st.session_state.completed_lessons.values() if is_done)


def get_total_lessons():
    return len(LESSONS)


def get_progress_fraction():
    total = get_total_lessons()
    if total == 0:
        return 0
    return get_completed_count() / total


def render_progress_summary(location="main"):
    completed = get_completed_count()
    total = get_total_lessons()
    progress_fraction = get_progress_fraction()

    if location == "sidebar":
        st.sidebar.write(f"Progress: **{completed}/{total} lessons complete**")
        st.sidebar.progress(progress_fraction)
    else:
        st.write(f"Progress: **{completed}/{total} lessons complete**")
        st.progress(progress_fraction)


def mark_lesson_complete(lesson_key):
    st.session_state.completed_lessons[lesson_key] = True


def render_lesson_complete_button(lesson_key):
    lesson_title = LESSONS[lesson_key]["title"]

    if st.session_state.completed_lessons[lesson_key]:
        st.success(f"Completed: {lesson_title}")
    else:
        if st.button(f"Mark complete: {lesson_title}", key=f"complete_{lesson_key}"):
            mark_lesson_complete(lesson_key)
            st.success(f"Completed: {lesson_title}")


def render_checkpoint_feedback(question_key, selected_answer, correct_answer):
    if selected_answer is None:
        return

    if selected_answer == correct_answer:
        st.success("Correct. You are ready to mark this lesson complete.")
    else:
        st.warning("Not quite. Review the explanation above and try again.")


def reset_progress():
    for lesson_key in st.session_state.completed_lessons:
        st.session_state.completed_lessons[lesson_key] = False


initialize_progress()


# -----------------------------
# General helper functions
# -----------------------------

def format_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:04.1f}"


def make_bar_chart(labels, values, y_label, title):
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(labels, values)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)

    max_value = max(values) if len(values) > 0 else 0
    label_padding = max(max_value * 0.02, 0.5)
    ax.set_ylim(0, max_value + label_padding * 4)

    for index, value in enumerate(values):
        label = f"{value:.1f}" if isinstance(value, float) else f"{value}"
        ax.text(index, value + label_padding, label, ha="center", va="bottom")

    return fig


# -----------------------------
# Race module helper functions
# -----------------------------

def get_race_segments(race):
    if race == "800m":
        return 2, "400m"
    elif race == "1600m":
        return 4, "400m"
    else:
        return 5, "1K"


def get_race_distance_meters(race):
    if race == "800m":
        return 800
    elif race == "1600m":
        return 1600
    else:
        return 5000


def normalize_splits(raw_splits, target_total):
    current_total = sum(raw_splits)
    scale_factor = target_total / current_total
    return [split * scale_factor for split in raw_splits]


def create_pacing_strategies(average_split, segments, total_seconds):
    even_splits = [average_split] * segments

    fast_start_raw = np.linspace(average_split * 0.94, average_split * 1.06, segments)
    fast_start_splits = normalize_splits(fast_start_raw, total_seconds)

    negative_raw = np.linspace(average_split * 1.06, average_split * 0.94, segments)
    negative_splits = normalize_splits(negative_raw, total_seconds)

    return even_splits, fast_start_splits, negative_splits


def calculate_consistency_score(splits):
    return np.std(splits)


def calculate_speed_metrics(distance_meters, total_seconds):
    meters_per_second = distance_meters / total_seconds
    miles_per_hour = meters_per_second * 2.23694

    meters_per_mile = 1609.344
    distance_miles = distance_meters / meters_per_mile
    mile_pace_seconds = total_seconds / distance_miles

    return meters_per_second, miles_per_hour, mile_pace_seconds


def explain_time_difference(difference):
    if abs(difference) < 0.5:
        return "You matched the goal almost exactly."
    elif difference > 0:
        return f"You are {difference:.1f} seconds slower than the goal."
    else:
        return f"You are {abs(difference):.1f} seconds faster than the goal."


def calculate_accuracy_score(difference):
    score = 100 - abs(difference) * 5
    return max(0, min(100, score))


def calculate_consistency_component(variation, target_variation):
    score = 100 - (variation / target_variation) * 30
    return max(0, min(100, score))


def calculate_optimization_score(accuracy_score, consistency_component):
    return (accuracy_score * 0.6) + (consistency_component * 0.4)


def give_optimization_feedback(difference, variation, target_variation, optimization_score):
    if optimization_score >= 90:
        return "Excellent optimization. Your plan is close to the goal time and keeps pacing controlled."
    elif abs(difference) > 5:
        return "Focus first on getting closer to the goal time. Your total time is the biggest issue right now."
    elif variation > target_variation:
        return "Your time is close, but your splits vary too much. Try making your segment times more even."
    else:
        return "Good plan. You are balancing time accuracy and pacing consistency reasonably well."


def make_strategy_graph(x, segment_name, even_splits, fast_start_splits, negative_splits):
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
    make_probability = make_percentage / 100
    return shot_value * make_probability


def compare_shots(expected_two, expected_three):
    if abs(expected_two - expected_three) < 0.01:
        return "About equal"
    elif expected_two > expected_three:
        return "2-point shot"
    else:
        return "3-point shot"


def calculate_break_even_three_percentage(expected_two):
    return (expected_two / 3) * 100


def make_expected_points_chart(expected_two, expected_three):
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
        ax.text(index, value + label_padding, f"{value:.2f}", ha="center", va="bottom")

    return fig


def simulate_shots(shot_value, make_percentage, possessions, seed):
    make_probability = make_percentage / 100
    rng = np.random.default_rng(seed)
    makes = rng.binomial(possessions, make_probability)
    misses = possessions - makes
    total_points = makes * shot_value

    return makes, misses, total_points


def make_simulation_chart(two_point_total, three_point_total, expected_two_total, expected_three_total):
    labels = ["2PT simulated", "3PT simulated", "2PT expected", "3PT expected"]
    values = [two_point_total, three_point_total, expected_two_total, expected_three_total]

    return make_bar_chart(labels, values, "Total points", "Simulated Points vs Expected Points")


def simulate_mixed_strategy(two_point_percentage, three_point_percentage, possessions, three_point_share, seed):
    three_attempts = int(round(possessions * three_point_share / 100))
    two_attempts = possessions - three_attempts

    rng = np.random.default_rng(seed)

    two_makes = rng.binomial(two_attempts, two_point_percentage / 100)
    three_makes = rng.binomial(three_attempts, three_point_percentage / 100)

    two_points = two_makes * 2
    three_points = three_makes * 3
    total_points = two_points + three_points

    return two_attempts, three_attempts, two_makes, three_makes, total_points


def calculate_strategy_expected_total(two_attempts, three_attempts, expected_two, expected_three):
    return (two_attempts * expected_two) + (three_attempts * expected_three)


def calculate_strategy_score(strategy_expected_total, best_expected_total):
    if best_expected_total <= 0:
        return 0

    score = (strategy_expected_total / best_expected_total) * 100
    return max(0, min(100, score))


def give_basketball_challenge_feedback(three_point_share, expected_two, expected_three, strategy_score):
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
    labels = ["2PT attempts", "2PT makes", "3PT attempts", "3PT makes"]
    values = [two_attempts, two_makes, three_attempts, three_makes]

    return make_bar_chart(labels, values, "Number of possessions", "Challenge Strategy: Attempts and Makes")


# -----------------------------
# Project overview
# -----------------------------

def render_project_overview():
    st.title("🏀🏃 SportaMath Lab")
    st.subheader("Interactive Math Through Sports")
    st.caption("v2.5 — Bite-Sized Lessons + Progress Tracking")

    st.markdown(
        """
        **SportaMath Lab** is an interactive educational app that helps middle and high school students
        learn math through sports simulations.

        The project connects abstract math ideas to sports decisions: pacing a race, comparing shot choices,
        understanding randomness, and optimizing strategy.
        """
    )

    st.success(
        "v2.5 responds to user testing feedback: the app is now organized into bite-sized lessons with measurable progress."
    )

    st.info(
        "Mission: Make math feel visible, useful, and fun by connecting it to sports."
    )

    render_progress_summary()

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric("Modules", "2")

    with metric_col2:
        st.metric("Lessons", get_total_lessons())

    with metric_col3:
        st.metric("Completed", get_completed_count())

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Learning Path",
            "Math Concepts",
            "Design Response",
            "Demo Guide"
        ]
    )

    with tab1:
        st.header("Guided Learning Path")

        st.write(
            "Instead of showing each module as one large dashboard, v2.5 breaks the app into short lessons."
        )

        lesson_rows = []

        for lesson_key, lesson_info in LESSONS.items():
            lesson_rows.append({
                "Status": "✅ Complete" if st.session_state.completed_lessons[lesson_key] else "⬜ Not yet",
                "Module": lesson_info["module"],
                "Lesson": lesson_info["title"],
                "Learning Goal": lesson_info["goal"]
            })

        st.table(pd.DataFrame(lesson_rows))

        st.subheader("How to Use the App")

        st.markdown(
            """
            1. Start with **Race Lesson 1** or **Basketball Lesson 1**.
            2. Read the learning goal.
            3. Try the interactive controls.
            4. Answer the checkpoint question.
            5. Mark the lesson complete.
            6. Watch your progress bar increase.
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
        st.header("How v2.5 Responds to User Feedback")

        st.write(
            "A user said the idea was strong, but the modules felt clumped and should be consumed in bite-sized lessons where progress is measurable."
        )

        st.subheader("What Changed")

        st.markdown(
            """
            - Added a guided learning path.
            - Broke each module into four lessons.
            - Added lesson goals.
            - Added checkpoint questions.
            - Added progress tracking.
            - Added completion buttons for each lesson.
            """
        )

        st.subheader("Why This Matters")

        st.write(
            "This makes the app feel more like a learning tool instead of a collection of calculators. "
            "It also shows an engineering design cycle: build, test, collect feedback, and revise."
        )

    with tab4:
        st.header("Suggested Demo Guide")

        st.subheader("Demo 1: Race Pacing")

        st.markdown(
            """
            1. Choose **Race Pacing Simulator** from the sidebar.
            2. Open **Lesson 1: Average Split** and show how the target split is calculated.
            3. Open **Lesson 2: Pacing Strategies** and compare the graph/table.
            4. Open **Lesson 4: Pacing Challenge** and adjust splits to improve the score.
            """
        )

        st.subheader("Demo 2: Basketball Probability")

        st.markdown(
            """
            1. Choose **Basketball Shot Probability** from the sidebar.
            2. Open **Lesson 2: Expected Points** and compare 2PT vs 3PT shots.
            3. Open **Lesson 3: Simulation** and change the simulation scenario.
            4. Open **Lesson 4: Strategy Challenge** and test different 3-point attempt shares.
            """
        )

        st.subheader("Portfolio Summary")

        st.write(
            "Built SportaMath Lab, a Python/Streamlit educational app that teaches math through interactive "
            "running and basketball simulations, including pacing optimization, expected value, "
            "probability-based strategy, user testing, and iterative redesign."
        )


# -----------------------------
# Race module
# -----------------------------

def render_race_module(learning_mode):
    st.sidebar.write("Race Pacing Simulator")

    race = st.sidebar.selectbox("Choose a race distance:", ["800m", "1600m", "5K"])

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
        "Use the lesson selector to work through race pacing in smaller steps."
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
    st.caption("v2.5 — Bite-Sized Lessons + Progress Tracking")

    st.markdown(
        """
        This module teaches race pacing through four short lessons:
        average split, pacing strategies, consistency, and challenge mode.
        """
    )

    render_progress_summary()

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

    lesson = st.radio(
        "Choose a bite-sized race lesson:",
        [
            "Lesson 1: Average Split",
            "Lesson 2: Pacing Strategies",
            "Lesson 3: Consistency and Variation",
            "Lesson 4: Pacing Challenge"
        ],
        horizontal=True
    )

    if lesson == "Lesson 1: Average Split":
        st.header("Race Lesson 1: Average Split")
        st.info(LESSONS["race_average"]["goal"])

        st.write(
            "The average split tells us how fast each segment should be if the race is paced evenly."
        )

        st.latex(r"\text{Average split} = \frac{\text{Total time}}{\text{Number of segments}}")

        st.write(f"Total time: **{format_time(total_seconds)}**")
        st.write(f"Number of segments: **{segments}**")
        st.write(f"Average {segment_name} split: **{format_time(average_split)}**")

        st.subheader("Rate Connection")

        st.latex(r"\text{Speed} = \frac{\text{Distance}}{\text{Time}}")

        st.write(f"Average speed: **{meters_per_second:.2f} m/s**")
        st.write(f"Equivalent mile pace: **{format_time(mile_pace_seconds)} per mile**")

        st.subheader("Checkpoint")

        answer = st.radio(
            "How do you calculate average split?",
            [
                "Total time divided by number of segments",
                "Number of segments divided by total time",
                "Fastest split minus slowest split"
            ],
            key="checkpoint_race_average"
        )

        render_checkpoint_feedback(
            "checkpoint_race_average",
            answer,
            "Total time divided by number of segments"
        )

        render_lesson_complete_button("race_average")

    elif lesson == "Lesson 2: Pacing Strategies":
        st.header("Race Lesson 2: Pacing Strategies")
        st.info(LESSONS["race_strategies"]["goal"])

        st.write(
            "All three strategies below reach the same total goal time, but they distribute effort differently."
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Pacing Strategy Table")
            st.table(display_data)

        with col2:
            st.subheader("Strategy Definitions")
            st.markdown(
                """
                - **Even pace:** each segment is about the same.
                - **Fast start:** early segments are faster.
                - **Negative split:** later segments are faster.
                """
            )

        st.subheader("Pacing Strategy Graph")

        strategy_fig = make_strategy_graph(
            x,
            segment_name,
            even_splits,
            fast_start_splits,
            negative_splits
        )

        st.pyplot(strategy_fig)

        st.subheader("Checkpoint")

        answer = st.radio(
            "Which strategy keeps the segment times most similar?",
            [
                "Even pace",
                "Fast start",
                "Negative split"
            ],
            key="checkpoint_race_strategies"
        )

        render_checkpoint_feedback("checkpoint_race_strategies", answer, "Even pace")
        render_lesson_complete_button("race_strategies")

    elif lesson == "Lesson 3: Consistency and Variation":
        st.header("Race Lesson 3: Consistency and Variation")
        st.info(LESSONS["race_consistency"]["goal"])

        st.write(
            "Averages do not tell the whole story. Two runners can finish with the same total time but have very different pacing patterns."
        )

        st.subheader("Variation Scores")

        variation_data = pd.DataFrame({
            "Strategy": ["Even Pace", "Fast Start", "Negative Split"],
            "Variation, seconds": [
                round(even_std, 2),
                round(fast_start_std, 2),
                round(negative_std, 2)
            ]
        })

        st.table(variation_data)

        st.info(f"The most consistent pacing strategy is: **{most_consistent}**")

        if learning_mode == "Advanced":
            st.subheader("Advanced Note")

            st.write(
                "The app uses standard deviation as a simple measure of pacing variation."
            )

            st.latex(
                r"\sigma = \sqrt{\frac{(x_1-\bar{x})^2 + (x_2-\bar{x})^2 + \cdots + (x_n-\bar{x})^2}{n}}"
            )

        st.subheader("Checkpoint")

        answer = st.radio(
            "What does lower variation mean in this pacing model?",
            [
                "The splits are more consistent",
                "The runner always finishes faster",
                "The race distance becomes shorter"
            ],
            key="checkpoint_race_consistency"
        )

        render_checkpoint_feedback(
            "checkpoint_race_consistency",
            answer,
            "The splits are more consistent"
        )

        render_lesson_complete_button("race_consistency")

    else:
        st.header("Race Lesson 4: Pacing Challenge")
        st.info(LESSONS["race_challenge"]["goal"])

        st.write(
            "Adjust each split and try to match the goal time while keeping your pacing consistent."
        )

        target_variation = max(3, average_split * 0.04)

        st.success(
            f"Challenge: Hit the goal time while keeping variation near or below {target_variation:.2f} seconds."
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

        st.subheader("Your Pacing Graph")

        custom_fig = make_custom_graph(x, segment_name, custom_splits, average_split)
        st.pyplot(custom_fig)

        st.subheader("Checkpoint")

        answer = st.radio(
            "What two goals does the optimization score balance?",
            [
                "Goal-time accuracy and pacing consistency",
                "Weather and shoe choice",
                "Height and weight"
            ],
            key="checkpoint_race_challenge"
        )

        render_checkpoint_feedback(
            "checkpoint_race_challenge",
            answer,
            "Goal-time accuracy and pacing consistency"
        )

        render_lesson_complete_button("race_challenge")


# -----------------------------
# Basketball module
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
        "Use the lesson selector to work through basketball probability in smaller steps."
    )

    expected_two = calculate_expected_points(2, two_point_percentage)
    expected_three = calculate_expected_points(3, three_point_percentage)
    better_shot = compare_shots(expected_two, expected_three)
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
    st.caption("v2.5 — Bite-Sized Lessons + Progress Tracking")

    st.markdown(
        """
        This module teaches basketball shot selection through four short lessons:
        probability, expected points, simulation, and strategy challenge.
        """
    )

    render_progress_summary()

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("2PT Expected", f"{expected_two:.2f} pts/shot")

    with metric_col2:
        st.metric("3PT Expected", f"{expected_three:.2f} pts/shot")

    with metric_col3:
        st.metric("Better by EV", better_shot)

    with metric_col4:
        st.metric("Possessions", possessions)

    lesson = st.radio(
        "Choose a bite-sized basketball lesson:",
        [
            "Lesson 1: Probability",
            "Lesson 2: Expected Points",
            "Lesson 3: Simulation",
            "Lesson 4: Strategy Challenge"
        ],
        horizontal=True
    )

    if lesson == "Lesson 1: Probability":
        st.header("Basketball Lesson 1: Probability")
        st.info(LESSONS["basketball_probability"]["goal"])

        st.write(
            "A shooting percentage can be converted into a probability by dividing by 100."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("2-Point Shot")
            st.write(f"Shooting percentage: **{two_point_percentage}%**")
            st.write(f"Probability: **{two_point_percentage / 100:.2f}**")

        with col2:
            st.subheader("3-Point Shot")
            st.write(f"Shooting percentage: **{three_point_percentage}%**")
            st.write(f"Probability: **{three_point_percentage / 100:.2f}**")

        st.subheader("Checkpoint")

        answer = st.radio(
            "What is the probability form of a 35% shot?",
            [
                "0.35",
                "3.5",
                "35.0"
            ],
            key="checkpoint_basketball_probability"
        )

        render_checkpoint_feedback("checkpoint_basketball_probability", answer, "0.35")
        render_lesson_complete_button("basketball_probability")

    elif lesson == "Lesson 2: Expected Points":
        st.header("Basketball Lesson 2: Expected Points")
        st.info(LESSONS["basketball_expected"]["goal"])

        st.write(
            "Expected points tells us the average value of a shot over many attempts."
        )

        st.latex(
            r"\text{Expected points} = \text{Shot value} \times \text{Make probability}"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("2-Point Shot")
            st.write(f"Shot value: **2 points**")
            st.write(f"Make probability: **{two_point_percentage / 100:.2f}**")
            st.metric("Expected 2PT Value", f"{expected_two:.2f} points/shot")

        with col2:
            st.subheader("3-Point Shot")
            st.write(f"Shot value: **3 points**")
            st.write(f"Make probability: **{three_point_percentage / 100:.2f}**")
            st.metric("Expected 3PT Value", f"{expected_three:.2f} points/shot")

        st.subheader("Visual Comparison")

        chart_fig = make_expected_points_chart(expected_two, expected_three)
        st.pyplot(chart_fig)

        st.subheader("Break-Even Point")

        st.write(
            "The break-even 3-point percentage tells us what 3-point percentage would match the expected value of the current 2-point shot."
        )

        st.metric("Break-even 3PT percentage", f"{break_even_three_percentage:.1f}%")

        st.subheader("Checkpoint")

        answer = st.radio(
            "If a 2-point shot is made 50% of the time, what is its expected value?",
            [
                "1.00 point per shot",
                "2.00 points per shot",
                "0.50 points per shot"
            ],
            key="checkpoint_basketball_expected"
        )

        render_checkpoint_feedback(
            "checkpoint_basketball_expected",
            answer,
            "1.00 point per shot"
        )

        render_lesson_complete_button("basketball_expected")

    elif lesson == "Lesson 3: Simulation":
        st.header("Basketball Lesson 3: Simulation")
        st.info(LESSONS["basketball_simulation"]["goal"])

        st.write(
            "Expected value describes the long-run average. Simulation shows what might happen in one specific set of possessions."
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
            st.write(f"This simulation made **{two_makes}** two-point shots and missed **{two_misses}**.")

        with result_col2:
            st.subheader("3-Point Strategy")
            st.metric("Simulated Makes", f"{three_makes}/{possessions}")
            st.metric("Simulated Points", three_simulated_points)
            st.metric("Expected Total Points", f"{expected_three_total:.1f}")
            st.write(f"This simulation made **{three_makes}** three-point shots and missed **{three_misses}**.")

        st.subheader("Simulation Chart")

        simulation_fig = make_simulation_chart(
            two_simulated_points,
            three_simulated_points,
            expected_two_total,
            expected_three_total
        )

        st.pyplot(simulation_fig)

        st.subheader("Checkpoint")

        answer = st.radio(
            "What changes when you change only the simulation scenario?",
            [
                "The random simulated result may change",
                "The shooting percentages change",
                "The point values change"
            ],
            key="checkpoint_basketball_simulation"
        )

        render_checkpoint_feedback(
            "checkpoint_basketball_simulation",
            answer,
            "The random simulated result may change"
        )

        render_lesson_complete_button("basketball_simulation")

    else:
        st.header("Basketball Lesson 4: Strategy Challenge")
        st.info(LESSONS["basketball_challenge"]["goal"])

        st.write(
            "Choose what percentage of possessions should be 3-point attempts. The rest will be 2-point attempts."
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

        st.subheader("Challenge Strategy Chart")

        challenge_fig = make_mixed_strategy_chart(
            two_attempts,
            three_attempts,
            challenge_two_makes,
            challenge_three_makes
        )

        st.pyplot(challenge_fig)

        st.subheader("Checkpoint")

        answer = st.radio(
            "A strong long-run strategy usually uses more of which shot?",
            [
                "The shot with higher expected value",
                "Always the 3-point shot",
                "Always the 2-point shot"
            ],
            key="checkpoint_basketball_challenge"
        )

        render_checkpoint_feedback(
            "checkpoint_basketball_challenge",
            answer,
            "The shot with higher expected value"
        )

        render_lesson_complete_button("basketball_challenge")


# -----------------------------
# Sidebar and app routing
# -----------------------------

st.sidebar.title("SportaMath Lab")
st.sidebar.caption("Version v2.5")

render_progress_summary(location="sidebar")

if st.sidebar.button("Reset progress"):
    reset_progress()
    st.sidebar.success("Progress reset.")

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
    st.sidebar.info("Start here to see the guided learning path.")
    render_project_overview()
elif selected_module == "Race Pacing Simulator":
    render_race_module(learning_mode)
else:
    render_basketball_module(learning_mode)
