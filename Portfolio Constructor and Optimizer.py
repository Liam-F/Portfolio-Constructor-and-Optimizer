#Project: Portfolio Construction and Optimization
#Name: Bilal Mustafa
#Date: 3/13/2018

import sys
from pandas_datareader import data, wb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as sco


def analyzePortfolio(input_portfolio):
    """"A function to print out the description of a portfolio (Return, Std Dev, Sharpe Ratio and Mix"""

    print("Return " + str(input_portfolio[1]))
    print("Standard Deviation " + str(input_portfolio[0]))
    print("Sharpe ratio " + str(input_portfolio[2]) )
    print("Mix: \n")
    for i in range(len(input_portfolio[3])):
        print(str(input_portfolio[4][i]) + ' ' + str(input_portfolio[3][i]).upper())
    print()

def objective(weights_matrix, sign = -1):
    """A function to set as the objective for optimization function"""

    portfolio_return = np.sum(mean_return * weights_matrix) * 252
    portfolio_std_dev = np.sqrt(np.dot(weights_matrix.T, np.dot(covariance_matrix, weights_matrix))) * np.sqrt(252)
    return sign * portfolio_return/portfolio_std_dev
    #(Sharpe ratio * -1) returned. By minimizing this function, the Sharpe ratio is maximized

def objective2(weights_matrix):
    """A function to set as the objective for the optimization function, to minimize the portfolio standard deviation"""

    portfolio_std_dev = np.sqrt(np.dot(weights_matrix.T, np.dot(covariance_matrix, weights_matrix))) * np.sqrt(252)
    return portfolio_std_dev

def constraint1(weights_matrix):
    """A function to set the constraint of the optimization function so that the sum of weights equals one"""

    return 1 - np.sum(weights_matrix)

def constraint2(weights_matrix):
    """A function to set the constraint of the optimization function so that the portfolio return
    equals the desired return"""

    portfolio_return = np.sum(mean_return * weights_matrix) * 252
    return desired_return - portfolio_return




stock_list = []
#initialize list for stocks- to be used later on

try:
    numberofStocks = int(input("How many stocks would you like in your portfolio? \n"))
except:
    print('Error Wrong Type')
    sys.exit()
#ask for the number of stocks in the desired portfolio, only integers can be given

for i in range(numberofStocks):
    stock_list.append(input("Enter ticker for stock " + str(i+1) + ':\n'))
    for char in stock_list[i]:
        if char == ' ':
            print("Error - whitespace in ticker")
            sys.exit()
    if stock_list[i] == "" or stock_list[i] == "\n":
        print("Error - incorrect ticker")
        sys.exit()
#ask for and create a list of the stock tickers for our desired portfolio

option = input("Press 1 if you want your portfolio optimized for a given return OR Press 2 if you want an optimized sharpe ratio for any return \n")
option = int(option)
if option != 2 and option != 1:
    print("Error - incorrect input")
    sys.exit()
#ask for the objective of this program- absolute optimization & variance minimization or optimization given a desired
#return

desired_return = 0
if int(option) == 1:
    desired_return = int(input("Please enter desired return \n"))
    desired_return = desired_return/100
#If a desired return was given, convert to decimals

trigger = False
killer = 0
while(trigger == False):
    try :
        if(killer == 6):
            sys.exit()
        df = data.DataReader(stock_list, data_source='yahoo', start='01/01/2010')['Adj Close']
        trigger = True
    except:
        killer += 1
#pull historical price data for our list of stocks. If an error is given (happens randomly), try again atleast 6 times

df.sort_index(inplace=True)
stock_returns = df.pct_change()
mean_return = stock_returns.mean()
covariance_matrix = stock_returns.cov()
#Invert the dates for the data frame and calculate the returns and covariances of the stocks


if option == 1:
    print("Mean returns are ")
    print(mean_return * 25200)
    print()
    some_greater = False
    some_lesser = False
    for i in mean_return:
        if (i*252) >= desired_return:
            some_greater = True
        if (i*252) <= desired_return:
            some_lesser = True
    if some_lesser == False:
        print("Impossible to get desired return. All returns are greater than our desired return.")
        sys.exit()
    if some_greater == False:
        print("Impossible to get desired return. All returns are lesser than our desired return")
        sys.exit()
#Make sure it is possible to get the desired return from a mix of portfolios we currently have

trials = 700
results = np.ones((trials, 3))
#Initialize an array for the results (to be plotted) and the number of simulations you want to conduct
#for your Monte Carlo

max_Sharpe = 0
max_Sharpe_index = 0
max_Sharpe_coordinates = []
max_Sharpe_Portfolio = 0
min_variance = 100000000
min_variance_index = 0
min_variance_coordinates = []
min_Variance_Porfolio = 0
#Initialize variables to record your optimal results generated from the Monte Carlo simulation

for i in range(trials):

    weights_matrix = np.random.random(numberofStocks)
    weights_matrix /= np.sum(weights_matrix)
    #Randomly generate a matrix of weights for the Monte Carlo Simulation such that they add up to 1

    portfolio_return = np.sum(mean_return*weights_matrix) *252
    portfolio_std_dev = np.sqrt(np.dot(weights_matrix.T,np.dot(covariance_matrix, weights_matrix))) * np.sqrt(252)
    #Calculate the portfolio returns and the standard deviation of those returns
    #volatility = X'(CX) where X are the weights and C is the covariance matrix
    #https://www.fool.com/knowledge-center/how-to-calculate-annualized-volatility.aspx

    results[i] = [portfolio_return, portfolio_std_dev, (portfolio_return/portfolio_std_dev)]
    #Stored the return, volatility, sharpe ratio from this Monte Carlo Simulation in the results array

    if (portfolio_std_dev < min_variance):
        min_variance = portfolio_std_dev
        min_variance_index = i
        min_variance_coordinates = [portfolio_std_dev, portfolio_return]
        min_Variance_Porfolio = [portfolio_std_dev, portfolio_return, (portfolio_return/portfolio_std_dev), stock_list, weights_matrix]
    #Store information concerning the mimimum variance portfolio

    if ((portfolio_return/portfolio_std_dev) > max_Sharpe):
        max_Sharpe = portfolio_return/portfolio_std_dev
        max_Sharpe_index = i
        max_Sharpe_coordinates = [portfolio_std_dev, portfolio_return]
        max_Sharpe_Portfolio = [portfolio_std_dev, portfolio_return, (portfolio_return/portfolio_std_dev),stock_list, weights_matrix]
    #Store information concerning the portfolio with the highest Sharpe ratio

bnds = []
for i in stock_list:
    bnds.append((0,1))
con1 = {'type' : 'eq', 'fun' : constraint1}
#Create a list of bounds for our weights not to escape the range of zero to one
#Create a map for the first constraint (sum of weights to be equal to one)

if option == 1:
    con2 = {'type' :'eq', 'fun' : constraint2}
    cons = [con1, con2]
    #If a desired return is given, create a second constraint to make sure the potfolio return equals desired return

    solution = sco.minimize(objective, weights_matrix, method='SLSQP', bounds=bnds, constraints=cons)
    #Optimize to get the highest sharpe ratio (and hence lowest std. dev. for a given return)
    #Using Sequential Least Squares Programming

else:
    cons = [con1]
    solution = sco.minimize(objective, weights_matrix, method = 'SLSQP', bounds = bnds, constraints = cons)
    solution2 = sco.minimize(objective2, weights_matrix, method = 'SLSQP', bounds = bnds, constraints = cons)
    #Else if the global Maximum Sharpe Ratio and Minimum return is desired, optimize for both
    # Using Sequential Least Squares Programming

optimizer_optimal_return = np.sum(mean_return*solution.x) *252
optimizer_optimal_stddev = np.sqrt(np.dot(solution.x.T,np.dot(covariance_matrix, solution.x))) * np.sqrt(252)
optimal_sharpe_ratio = optimizer_optimal_return/optimizer_optimal_stddev
max_Sharpe_Portfolio_optimizer = [optimizer_optimal_stddev, optimizer_optimal_return, optimal_sharpe_ratio, stock_list, solution.x]
#Initialize variables to store information concerning the portfolio with the highest Sharpe ratio given our
#constraints

print()
if option != 1:
    print("The portfolio with the Maximum Sharpe Ratio (via Sequential Least Squares Programming) is \n")
else:
    print("The portfolio with the Maximum Sharpe Ratio and Minimum Variance (via Sequential Least Squares Programming) with our desired return is \n")
analyzePortfolio(max_Sharpe_Portfolio_optimizer)
#Print out details concerning our optimal portfolio (generated via SLSQP)

if option != 1:
    minimum_variance_return = np.sum(mean_return*solution2.x) *252
    minimum_variance_stddev = np.sqrt(np.dot(solution2.x.T,np.dot(covariance_matrix, solution2.x))) * np.sqrt(252)
    minimum_variance_sharpe_ratio = minimum_variance_return/minimum_variance_stddev
    minimum_variance_portfolio_optimizer = [minimum_variance_stddev, minimum_variance_return, minimum_variance_sharpe_ratio, stock_list, solution2.x]
    print("The portfolio with the Minimum variance (via Sequential Least Squares Programming) is \n")
    analyzePortfolio(minimum_variance_portfolio_optimizer)
#In the case where no desired return is rquired, also print out details conceerning our minimum variance portfolio

results_df = pd.DataFrame(results, columns = ['Returns', 'Standard Deviation', 'Sharpe Ratio'])
plt.style.use('seaborn-paper')
plt.figure(1)
plt.scatter(results_df.iloc[:,1], results_df.iloc[:,0], c=results_df.iloc[:,2], cmap='RdYlBu', s = 50)
plt.colorbar()
plt.xlabel('Standard Deviation')
plt.ylabel('Returns')
plt.title('Portfolio Distribution')
#Plot the results of our Monte Carlo Simulation on a scatterplot

plt.scatter(optimizer_optimal_stddev, optimizer_optimal_return, marker = 'X', color = 'r', s = 200)
if option != 1:
    plt.scatter(minimum_variance_stddev, minimum_variance_return, marker = 'X', color = 'g', s = 200)
#Add a point for the highest sharpe ratio and minimum variance (if no desired return asked) portfolios

if option != 1:
    print("The portfolio with the Maximum Sharpe Ratio (via Monte Carlo simulation) is \n")
    analyzePortfolio(max_Sharpe_Portfolio)
    print("The portfolio with the Minimum variance (via Monte Carlo simulation) is \n")
    analyzePortfolio(min_Variance_Porfolio)
#print our the details of our maximum sharpe ratio and minimum variance portfolios from our Monte Carlo Simulation


plt.figure(2)
plt.pie(solution.x, labels = stock_list, autopct = '%1.1f%%')
plt.title("Optimal Portfolio Mix")
#Plot a pie chart showing the distribution of stocks for our portfolio with the highest sharpe ratio

if option != 1:
    plt.figure(3)
    plt.pie(solution2.x, labels = stock_list, autopct= '%1.1f%%')
    plt.title("Minimum Variance Portfolio Mix")
#If a desired return was not given, also plot a pie chart showing the distribution of our minimum vairance portfolio

plt.show()