"""Script demonstrating the concept of idempotence / 'no side effects',
and distinguishing carefully between operations that modify a DataFrame
in-place versus those that create a transformed copy of a DataFrame.
"""


import pandas as pd


def compute_average_fahrenheit_inplace(df):
    """Compute average temperature in Fahrenheit.  This version modifies
    the DataFrame `df` in-place - so after calling this function the temperature
    column has been converted.
    
    This is an example of a 'side-effect', because the function changes
    the content of its input values, and this persists as the program continues
    to run.
    
    Side-effects can cause difficult-to-recognise (and difficult-to-debug)
    errors.
    """
    print("Computing average Fahrenheit temperature with in-place changes")
    df['temperature'] = 32 + 9*df['temperature']/5
    print(df['temperature'].mean())


def example_inplace():
    df = pd.DataFrame(
        [{'city': "Aberdeen", 'temperature': 0},
         {'city': "Norwich", 'temperature': 5}]
    )
    compute_average_fahrenheit_inplace(df)    
    compute_average_fahrenheit_inplace(df)    


def compute_average_fahrenheit_transform(df):
    """Compute average temperature in Fahrenheit.  This version converts
    Centigrade to Fahrenheit by means of a transformation operation - so
    the original DataFrame is unchanged.
    
    Because we write the code this way, nothing we do in this function
    "leaks" outside the function.  This is a very useful technique for
    managing the complexity in your program - especially when your program
    for cleaning and analysing data runs to hundreds or thousands of lines,
    which is typical for real-world projects.
    """
    print("Computing average Fahrenheit temperature by transformation operations")
    print(
        df.assign(temperature=lambda x: 32 + 9*x['temperature']/5)
        ['temperature'].mean()
    )


def example_transform():
    df = pd.DataFrame(
        [{'city': "Aberdeen", 'temperature': 0},
         {'city': "Norwich", 'temperature': 5}]
    )
    compute_average_fahrenheit_transform(df)    
    compute_average_fahrenheit_transform(df)    
    

def main():
    example_inplace()
    example_transform()
    


if __name__ == "__main__":
    main()
