from flask import Flask, render_template, request
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

app = Flask(__name__)

df_a = pd.read_csv("D://atchut//atchut//gujarat_db.csv")

CATEGORIES = ["CLASS/STANDARD", "GENDER", "CASTE", "REASON"]

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/analysis")
def analysis():
    return render_template("analysis.html", categories=CATEGORIES)

@app.route("/analyse", methods=["POST"])
def analysis_res():
    key = request.form.get("key")
    on = request.form.get("on") if key != "AREA" else int(request.form.get("on"))
    category = request.form.get("category")
    criteria, data = analyse(df_a, key=key, on=on, cat=category)

    image_paths = []

    if category == "all":
        image_paths = display_all(criteria, on, data)
        return render_template("plot_all.html", image_paths=image_paths)
    else:
        image_paths = display_single_plot(category, on, data[criteria.index(category)])
        return render_template("Blank_Graph.html", image_paths=image_paths)

def analyse(DF: pd.DataFrame, key: str = "STATE", on="GUJARAT", cat="all"):
    if key != "AREA":
        key = key.upper()
        on = on.upper()
    Dict = {"ACADEMIC": 0, "MOVED": 0, "POVERTY": 0, "OTHERS": 0}
    Dict_percentages = {}
    Gender = {"MALE": 0, "FEMALE": 0}
    Gender_Percent = {}
    Standard_Dict = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
    }
    Standard_Dictper = {}
    Caste = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    Casteper = {}
    for i in range(len(DF)):
        if (DF.loc[i, key] == on) and ((DF.loc[i, "GRADE"]) < 4):
            class_drops = DF.loc[i, "CLASS/STANDARD"]
            Standard_Dict[class_drops] += 1
            caste_drops = DF.loc[i, "CASTE"]
            Caste[str(caste_drops)] += 1
            if DF.loc[i, "GRADE"] != 0:
                Dict["ACADEMIC"] += 1
            if (DF.loc[i, "GENDER"]) == "M":
                Gender["MALE"] += 1
            if (DF.loc[i, "GENDER"]) == "F":
                Gender["FEMALE"] += 1
            if DF.loc[i, "GRADE"] == 0:
                if DF.loc[i, "MOVED"] == "YES":
                    Dict["MOVED"] += 1
                elif DF.loc[i, "OTHERS"] == "YES":
                    Dict["OTHERS"] += 1
                elif DF.loc[i, "POVERTY"] == "YES":
                    Dict["POVERTY"] += 1

    q, r, s, t = (
        sum(Dict.values()),
        sum(Standard_Dict.values()),
        sum(Caste.values()),
        sum(Gender.values()),
    )

    if sum(Dict.values()) == 0:
        q = 1

    for i in Dict.keys():
        percentage = (Dict[i] / q) * 100
        Dict_percentages[i] = percentage

    if sum(Standard_Dict.values()) == 0:
        r = 1

    for i in Standard_Dict.keys():
        percentage = (Standard_Dict[i] / r) * 100
        Standard_Dictper[i] = percentage

    if sum(Caste.values()) == 0:
        s = 1

    for i in Caste.keys():
        percentage = (Caste[i] / s) * 100
        Casteper[i] = percentage

    if sum(Gender.values()) == 0:
        t = 1

    for i in Gender.keys():
        percentage = (Gender[i] / t) * 100
        Gender_Percent[i] = percentage
    criteria = ["REASON", "CLASS/STANDARD", "CASTE", "GENDER"]
    data = [Dict_percentages, Standard_Dictper, Casteper, Gender_Percent]
    return criteria, data

def display_all(criteria: list[str], parameter: str, data: list[dict]):
    fig, ax = plt.subplots(2, 2, layout="constrained")
    fig = plt.gcf()
    fig.set_size_inches(10.2, 7.9)
    colors = ["#FF9933", "lightblue", "green"]

    for i in range(4):
        data_dict = data[i]
        axis = ax[i // 2, i % 2]  # Calculate subplot position
        bars = axis.bar(
            data_dict.keys(),
            data_dict.values(),
            label=data_dict.keys(),
            color=colors,
            align="center",
        )
        fig.suptitle(f"{parameter} DROPOUT ANALYSIS", c="#FF9933", fontweight="bold")
        axis.set_xticks(range(len(data_dict.keys())))
        axis.set_xlabel(f"{criteria[i]} CRITERION", c="green", fontweight="bold")
        axis.set_ylabel("PERCENTAGE", c="green", fontweight="bold")
        axis.bar_label(bars, padding=0, fmt="%.1f")
    # Clear the entire figure to release memory
    # plt.clf()
    image_paths = []
    for i, axs in enumerate(ax.flat):
        buffer = BytesIO()
        axs.get_figure().savefig(buffer, format="png")
        buffer.seek(0)
        image_path = f"D://atchut//atchut//static//plot_{i + 1}.png"
        image_paths.append(image_path)
        with open(image_path, "wb") as img_file:
            img_file.write(buffer.read())

        plt.clf()
        plt.close()
        # Return a list of image paths
    return image_paths

def display_single_plot(criteria: str, parameter: str, drop_percent: dict):
    # global tkinter_result

    fig, ax = plt.subplots()
    colors = ["#FF9933", "lightblue", "green"]
    ans = ax.bar(
        drop_percent.keys(),
        drop_percent.values(),
        label=drop_percent.keys(),
        color=colors,
        align="center",
    )
    fig.suptitle(f"{parameter} DROPOUT ANALYSIS", c="#FF9933", fontweight="bold")
    ax.set_xticks(range(len(drop_percent.keys())))
    ax.set_xlabel(f"{criteria} CRITERION", c="green", fontweight="bold")
    ax.set_ylabel("PERCENTAGE", c="green", fontweight="bold")
    ax.bar_label(ans, padding=0, fmt="%.2f")

    buffer = BytesIO()
    ax.get_figure().savefig(buffer, format="png")
    buffer.seek(0)
    image_path = "D://atchut//atchut//static//plot_single.png"

    with open(image_path, "wb") as img_file:
        img_file.write(buffer.read())

    ax.get_figure().clf()
    plt.close(ax.get_figure())

    # tkinter_result = image_path
    return image_path

if __name__ == "__main__":
    app.run(debug=True)
