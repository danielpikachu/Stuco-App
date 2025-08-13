import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from datetime import datetime
import time

# ------------------------------
# Initialize Session State (for storing data between interactions)
# ------------------------------
if 'scheduled_events' not in st.session_state:
    st.session_state.scheduled_events = pd.DataFrame(columns=['Event Name', 'Funds Per Event', 'Frequency Per Month', 'Total Funds'])

if 'occasional_events' not in st.session_state:
    st.session_state.occasional_events = pd.DataFrame(columns=[
        'Event Name', 'Total Funds Raised', 'Cost', 'Staff Many Or Not', 
        'Preparation Time', 'Rating'
    ])

if 'credit_data' not in st.session_state:
    # Load credit data (replace with your CSV path)
    st.session_state.credit_data = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Total_Credits': [200, 150, 300],
        'RedeemedCredits': [50, 0, 100]
    })

if 'reward_data' not in st.session_state:
    # Load reward data (replace with your CSV path)
    st.session_state.reward_data = pd.DataFrame({
        'Reward': ['Bubble Tea', 'Chips', 'Café Coupon'],
        'Cost': [50, 30, 80],
        'Stock': [10, 20, 5]
    })

if 'wheel_prizes' not in st.session_state:
    st.session_state.wheel_prizes = ["50 Credits", "Bubble Tea", "Chips", "100 Credits", "Café Coupon", "Free Prom Ticket"]
    st.session_state.wheel_colors = plt.cm.tab10(np.linspace(0, 1, len(st.session_state.wheel_prizes)))

if 'money_data' not in st.session_state:
    st.session_state.money_data = pd.DataFrame(columns=['Money', 'Time'])

if 'allocation_count' not in st.session_state:
    st.session_state.allocation_count = 0

# ------------------------------
# Helper Functions
# ------------------------------
def update_leaderboard():
    """Sort credit data by total credits (descending)"""
    st.session_state.credit_data = st.session_state.credit_data.sort_values(
        by='Total_Credits', ascending=False
    ).reset_index(drop=True)

def draw_wheel(rotation_angle=0):
    """Draw the lucky draw wheel with matplotlib"""
    n = len(st.session_state.wheel_prizes)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw sectors
    for i in range(n):
        start_angle = np.rad2deg(2 * np.pi * i / n + rotation_angle)
        end_angle = np.rad2deg(2 * np.pi * (i + 1) / n + rotation_angle)
        wedge = Wedge(center=(0, 0), r=1, theta1=start_angle, theta2=end_angle, 
                      width=1, facecolor=st.session_state.wheel_colors[i], edgecolor='black')
        ax.add_patch(wedge)

        # Add prize text
        mid_angle = np.deg2rad((start_angle + end_angle) / 2)
        text_x = 0.7 * np.cos(mid_angle)
        text_y = 0.7 * np.sin(mid_angle)
        ax.text(text_x, text_y, st.session_state.wheel_prizes[i],
                ha='center', va='center', rotation=np.rad2deg(mid_angle) - 90,
                fontsize=8)

    # Draw center circle
    circle = plt.Circle((0, 0), 0.1, color='white', edgecolor='black')
    ax.add_patch(circle)

    # Draw pointer
    ax.plot([0, 0], [0, 0.9], color='black', linewidth=2)
    ax.plot([-0.05, 0.05], [0.85, 0.9], color='black', linewidth=2)
    ax.plot([-0.05, 0.05], [0.85, 0.9], color='black', linewidth=2)

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    return fig

# ------------------------------
# Main App Layout
# ------------------------------
st.set_page_config(page_title="Student Council Fund Management", layout="wide")
st.title("Student Council Fund Management")

# Create tabs (matching MATLAB TabGroup)
tab1, tab2, tab3, tab4 = st.tabs([
    "Financial Optimizing", 
    "Credit & Reward System", 
    "SCIS Specific AI", 
    "Money Transfer"
])

# ------------------------------
# Tab 1: Financial Optimizing
# ------------------------------
with tab1:
    st.subheader("Financial Progress")
    col1, col2 = st.columns(2)
    with col1:
        current_fund_raised = st.number_input("Current Fund Raised", value=0.0, step=100.0)
    with col2:
        total_funds_needed = st.number_input("Total Funds Needed", value=10000.0, step=1000.0)
    
    # Calculate progress percentage
    progress = min(100.0, (current_fund_raised / total_funds_needed) * 100) if total_funds_needed > 0 else 0
    st.slider("Current Progress", 0.0, 100.0, progress, disabled=True)

    # Split into Scheduled Events and Occasional Events panels
    col_left, col_right = st.columns(2)

    # Left Panel: Scheduled Events
    with col_left:
        st.subheader("Scheduled Events")
        st.dataframe(st.session_state.scheduled_events, use_container_width=True)

        # Input new scheduled event
        with st.expander("Add New Scheduled Event"):
            event_name = st.text_input("Event Name", "Fundraiser")
            funds_per_event = st.number_input("Funds Per Event", value=100.0)
            freq_per_month = st.number_input("Frequency Per Month", value=1, step=1)
            
            if st.button("Add Scheduled Event"):
                total = funds_per_event * freq_per_month * 11  # 11 weeks
                new_event = pd.DataFrame({
                    'Event Name': [event_name],
                    'Funds Per Event': [funds_per_event],
                    'Frequency Per Month': [freq_per_month],
                    'Total Funds': [total]
                })
                st.session_state.scheduled_events = pd.concat(
                    [st.session_state.scheduled_events, new_event], ignore_index=True
                )
                st.success("Event added!")

        # Delete scheduled event
        if not st.session_state.scheduled_events.empty:
            event_to_delete = st.selectbox("Select Event to Delete", st.session_state.scheduled_events['Event Name'])
            if st.button("Delete Scheduled Event"):
                st.session_state.scheduled_events = st.session_state.scheduled_events[
                    st.session_state.scheduled_events['Event Name'] != event_to_delete
                ].reset_index(drop=True)
                st.success("Event deleted!")

        # Total funds for scheduled events
        total_scheduled = st.session_state.scheduled_events['Total Funds'].sum()
        st.metric("Aggregate Funds (Scheduled)", f"${total_scheduled:.2f}")

    # Right Panel: Occasional Events
    with col_right:
        st.subheader("Occasional Events")
        st.dataframe(st.session_state.occasional_events, use_container_width=True)

        # Input new occasional event
        with st.expander("Add New Occasional Event"):
            event_name = st.text_input("Event Name (Occasional)", "Charity Drive")
            funds_raised = st.number_input("Total Funds Raised", value=500.0)
            cost = st.number_input("Cost", value=100.0)
            staff_many = st.selectbox("Staff Many? (1=Yes, 0=No)", [0, 1])
            prep_time = st.selectbox("Prep Time <1 Week? (1=Yes, 0=No)", [0, 1])
            
            if st.button("Add Occasional Event"):
                # Calculate rating (matching MATLAB logic)
                rating = (funds_raised * 0.5) - (cost * 0.5) + (staff_many * 0.1 * 100) + (prep_time * 0.1 * 100)
                new_event = pd.DataFrame({
                    'Event Name': [event_name],
                    'Total Funds Raised': [funds_raised],
                    'Cost': [cost],
                    'Staff Many Or Not': [staff_many],
                    'Preparation Time': [prep_time],
                    'Rating': [rating]
                })
                st.session_state.occasional_events = pd.concat(
                    [st.session_state.occasional_events, new_event], ignore_index=True
                )
                st.success("Event added!")

        # Delete occasional event
        if not st.session_state.occasional_events.empty:
            event_to_delete = st.selectbox("Select Event to Delete", st.session_state.occasional_events['Event Name'])
            if st.button("Delete Occasional Event"):
                st.session_state.occasional_events = st.session_state.occasional_events[
                    st.session_state.occasional_events['Event Name'] != event_to_delete
                ].reset_index(drop=True)
                st.success("Event deleted!")

        # Sort by rating
        if st.button("Sort by Rating (Descending)"):
            st.session_state.occasional_events = st.session_state.occasional_events.sort_values(
                by='Rating', ascending=False
            ).reset_index(drop=True)
            st.success("Sorted!")

        # Optimize event allocation
        if not st.session_state.occasional_events.empty:
            total_target = st.number_input("Total Fundraising Target", value=5000.0)
            if st.button("Optimize Allocation"):
                net_profits = st.session_state.occasional_events['Total Funds Raised'] - st.session_state.occasional_events['Cost']
                allocated_times = np.zeros(len(net_profits), dtype=int)
                remaining = total_target

                # Ensure each event is held at least once (if affordable)
                for i in range(len(net_profits)):
                    if remaining >= net_profits[i] and allocated_times[i] < 3:
                        allocated_times[i] = 1
                        remaining -= net_profits[i]

                # Greedy allocation for remaining funds
                while remaining > 0:
                    available = np.where(allocated_times < 3)[0]
                    if len(available) == 0:
                        break
                    best_idx = available[np.argmax(net_profits[available])]
                    if net_profits[best_idx] <= remaining:
                        allocated_times[best_idx] += 1
                        remaining -= net_profits[best_idx]
                    else:
                        break

                # Add allocation as a new column
                st.session_state.allocation_count += 1
                col_name = f'Allocated Times (Target: ${total_target}, Count: {st.session_state.allocation_count})'
                st.session_state.occasional_events[col_name] = allocated_times
                st.success("Optimization complete!")

        # Total net funds for occasional events
        if not st.session_state.occasional_events.empty:
            total_occasional = (st.session_state.occasional_events['Total Funds Raised'] - st.session_state.occasional_events['Cost']).sum()
            st.metric("Aggregate Funds (Occasional)", f"${total_occasional:.2f}")

# ------------------------------
# Tab 2: Credit & Reward System
# ------------------------------
with tab2:
    col_credits, col_rewards = st.columns(2)

    # Left: Credit Management
    with col_credits:
        st.subheader("Student Credits")
        update_leaderboard()
        st.dataframe(st.session_state.credit_data, use_container_width=True)

        # Input new credits
        with st.expander("Log New Contribution"):
            student_name = st.text_input("Student Name", "Dave")
            contribution_type = st.selectbox("Contribution Type", ["Money", "Hours", "Events"])
            amount = st.number_input("Amount", value=10.0)
            
            if st.button("Add Credits"):
                # Calculate credits (matching MATLAB logic)
                if contribution_type == "Money":
                    credits = amount * 10  # $1 = 10 credits
                elif contribution_type == "Hours":
                    credits = amount * 5   # 1 hour = 5 credits
                else:  # Events
                    credits = amount * 25  # 1 event = 25 credits

                # Update or add student
                if student_name in st.session_state.credit_data['Name'].values:
                    st.session_state.credit_data.loc[
                        st.session_state.credit_data['Name'] == student_name, 'Total_Credits'
                    ] += credits
                else:
                    new_student = pd.DataFrame({
                        'Name': [student_name],
                        'Total_Credits': [credits],
                        'RedeemedCredits': [0]
                    })
                    st.session_state.credit_data = pd.concat(
                        [st.session_state.credit_data, new_student], ignore_index=True
                    )
                st.success(f"Added {credits} credits to {student_name}!")

    # Right: Reward Management
    with col_rewards:
        st.subheader("Available Rewards")
        st.dataframe(st.session_state.reward_data, use_container_width=True)

        # Redeem rewards
        with st.expander("Redeem Reward"):
            student_name = st.selectbox("Select Student", st.session_state.credit_data['Name'])
            reward_name = st.selectbox("Select Reward", st.session_state.reward_data['Reward'])
            
            if st.button("Redeem"):
                # Check if student and reward exist
                student = st.session_state.credit_data[st.session_state.credit_data['Name'] == student_name].iloc[0]
                reward = st.session_state.reward_data[st.session_state.reward_data['Reward'] == reward_name].iloc[0]

                # Check credits and stock
                available_credits = student['Total_Credits'] - student['RedeemedCredits']
                if available_credits >= reward['Cost'] and reward['Stock'] > 0:
                    # Update student credits
                    st.session_state.credit_data.loc[
                        st.session_state.credit_data['Name'] == student_name, 'RedeemedCredits'
                    ] += reward['Cost']
                    # Update reward stock
                    st.session_state.reward_data.loc[
                        st.session_state.reward_data['Reward'] == reward_name, 'Stock'
                    ] -= 1
                    st.success(f"{student_name} redeemed {reward_name}!")
                else:
                    st.error("Not enough credits or reward out of stock!")

    # Lucky Draw Wheel
    st.subheader("Lucky Draw")
    col_wheel, col_result = st.columns(2)
    
    with col_wheel:
        student_name = st.selectbox("Select Student for Lucky Draw", st.session_state.credit_data['Name'])
        if st.button("Spin Wheel"):
            # Check credits
            student = st.session_state.credit_data[st.session_state.credit_data['Name'] == student_name].iloc[0]
            if student['Total_Credits'] < 50:
                st.error("Need at least 50 credits to spin!")
            else:
                # Deduct credits
                st.session_state.credit_data.loc[
                    st.session_state.credit_data['Name'] == student_name, 'Total_Credits'
                ] -= 50

                # Animate wheel
                st.write("Spinning...")
                for i in range(50):  # 50 animation steps
                    rotation = (3 * 360) + (i * 10)  # Spin 3 full circles + incremental
                    fig = draw_wheel(np.deg2rad(rotation))
                    col_wheel.pyplot(fig)
                    time.sleep(0.05)

                # Final result
                prize_idx = np.random.randint(0, len(st.session_state.wheel_prizes))
                final_rotation = 3 * 360 + (prize_idx * (360 / len(st.session_state.wheel_prizes)))
                fig = draw_wheel(np.deg2rad(final_rotation))
                col_wheel.pyplot(fig)
                st.session_state.winner = st.session_state.wheel_prizes[prize_idx]

    with col_result:
        if 'winner' in st.session_state:
            st.success(f"Winner: {st.session_state.winner}!")

# ------------------------------
# Tab 3: SCIS Specific AI
# ------------------------------
with tab3:
    st.subheader("Lunch Menu Information")
    user_query = st.text_input("Ask about lunch menus...", "What's for lunch?")
    if st.button("Send"):
        lunch_menu = """
        On Monday at Hongqiao Campus, the lunch includes:
        - Main Course: Three Cup Chicken
        - Staple Food: Steamed Rice
        - Vegetables: Sautéed Bok Choy
        - Specialties: Steamed Pork Siu Mai
        - Sandwich Bar: Ham, Peanut Butter, Strawberry Jam
        - Vegetarian Dish: Three Cup Tofu (on request)
        - Salad Bar: Fresh Greens with Dressings
        - Drinks: Milk, Plain Yogurt, Apple Juice, Orange Juice
        - Fruits: Seasonal Fruit
        """
        st.text_area("Response", lunch_menu, height=300)

# ------------------------------
# Tab 4: Money Transfer
# ------------------------------
with tab4:
    st.subheader("Money Transfer Records")
    if st.button("Load Money Data"):
        # Load from Excel (replace with your file path)
        try:
            st.session_state.money_data = pd.read_excel("Money.xlsm")  # Use openpyxl engine for .xlsm
            st.dataframe(st.session_state.money_data, use_container_width=True)
        except FileNotFoundError:
            st.warning("No 'Money.xlsm' file found. Using sample data.")
            st.session_state.money_data = pd.DataFrame({
                'Money': [1000, 500, 750],
                'Time': [datetime(2025, 6, 1), datetime(2025, 6, 5), datetime(2025, 6, 10)]
            })
            st.dataframe(st.session_state.money_data, use_container_width=True)