bmi = 27

def classify_bmi(bmi):
    if bmi >= 30:
        category = "Obese"
    elif bmi >= 25:
        category = "Overweight"
    elif bmi >= 18.5:
        category = "Normal"
    else:
        category = "Underweight"
    # print(category)
    return category

def main():
    weight = float(input("Enter your weight in kg: "))
    height = float(input("Enter your height in meters: "))
    bmi_value = compute_bmi(weight, height)
    result = classify_bmi(bmi_value)
    print(f"Your BMI is {bmi_value:.2f}, which is classified as: {result}")

if __name__ == "__main__":
    main()