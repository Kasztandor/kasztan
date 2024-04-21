requiredCharacters = "+-*/"
allowedCharacters = "0123456789 ()"

equation = " "

def calculate(x):
    try:
        return eval(x)
    except:
        return "Invalid equation"

if not equation:
    print("Equation is empty")
elif all(char in allowedCharacters or char in requiredCharacters for char in equation):
    print(calculate(equation))
else:
    print("Invalid character in equation")