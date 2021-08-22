"""
This module manage the creation of random circle in sparse matrix using numpy package.
"""

import numpy as np
import matplotlib.pyplot as plt
import LordOfRings.inputHandling as ih
import os
import sys

def center_radius_generator(mu, sigma, rmin, rmax, n):
    """center_radius_generator generate three random numbers, two from
    a normal distribution and one from an uniform distribuion (with randint).
    The number extracted from the normal distribution are turned to integer
    values because we are working with matrix of integers.

    Parameters
    ----------
    mu : float, greater than or equal to zero, lower than the grid linear size
        The mean for the normal distribution.
    sigma : float, positive value
        The standard deviation for the normal distribution.
    rmax : float, positive value, greater than rmin
        The maximum radius for the uniform extraction.
    rmin : float, greater than or equal to zero, lower than rmax
        The minimum radius for the uniform extraction.
    n : int
        The linear size of the grid.

    Returns
    -------
    (1d numpy-array [int], int)
        the first element of the returned tuple contain the center position,
        the second element contain the radius.

    """
    # Testing input values
    ih.raise_value_error('mu', mu, min = 0, max = n)
    ih.raise_value_error('sigma', sigma, min = 0)
    ih.raise_value_error('rmax', rmax, min = rmin)
    ih.raise_value_error('rmin', rmin, max = rmax)
    ih.raise_value_error('n', n, min = 0)

    n_rand = np.random.normal(loc = mu, scale = sigma, size = 2).astype(int)
    # If obtain negative values or greater then the grid linear size repeat the extraction
    while (n_rand < 0).any() or (n_rand >= n).any():
        n_rand = np.random.normal(loc = mu, scale = sigma, size = 2).astype(int)
    c = n_rand
    r = np.random.randint(rmin, rmax)
    return c, r


def circle_generator(n, c, r):
    """circle_generator create a sparse matrix nxn with values 0 or 1.
    The only elements of the matrix that are 1 belong to a circle of radius r
    and center c.

    Parameters
    ----------
    n : int
        The linear size of the matrix
    c : 1d numpy array [float]
        The center's coordinates.
    r : float
        The radius of the circle.

    Returns
    -------
    2d numpy-array [int]
        The matrix of zeros containing the circle as 1 values.

    """

    # Testing input values
    ih.raise_value_error('n', n, min = 0)
    ih.raise_value_error('r', r, min = 0)
    for ci in c:
        if ci < 0:
            raise ValueError(f'x should be greater than or equal to {0}. The given value was {ci}')
        if ci >= n:
            raise ValueError(f'y should be lower than or equal to {n}. The given value was {ci}')

    v = np.arange(1, n+1)
    Y, X = np.meshgrid(v, v)
    deltaX = np.abs(X-c[0])
    deltaY = np.abs(Y-c[1])
    distance = np.sqrt(deltaX**2 + deltaY**2)
    circle = np.empty(distance.shape)
    circle[np.abs(distance - r) > 0.3 ] = 0
    circle[np.abs(distance - r) <= 0.3 ] = 1
    return circle


def rnd_circle_pruning(circle, threshold = 0.3, maxhits = 64):
    """rnd_circle_pruning modifies the input sparse matrix randomly removing
    some ones that belongs to the ring. The random selection uses a uniform
    distribution.

    Parameters
    ----------
    circle : 2d numpy-array [int]
        The input sparse matrix that contains the ring as ones.
    threshold : float
        Parameter that controll the extraction, i.e. lower values correspond to
        higer number of ones in the returned matrix and vice versa.
    maxhits : int
        The maximum number of points after the second pruning. If a circle has 
        more than maxhits points after the first pruning remove them randomly
        until they reach maxhits.

    Returns
    -------
    2d numpy-array [int]
        The matrix obtained from the random pruning.

    """

    # Testing input values
    if np.logical_and(circle != 0, circle != 1).any():
        raise ValueError('The input circle must be a sparse matrix of ones.')
    ih.raise_value_error('threshold', threshold, min = 0, max = 1)

    #first pruning
    randvector = np.random.rand( len(circle[circle!=0]) )
    randvector[randvector > threshold] = 1
    randvector[randvector <= threshold] = 0
    circle[circle!=0] = randvector
    
    #second pruning
    ones_arr = circle[circle == 1]
    len_ones = len(ones_arr)
    idx_ones = np.arange(len_ones)
    if len_ones >= maxhits :
        idx_to_zero = np.random.choice(idx_ones, size = len_ones - maxhits, replace = False, p = None)
        ones_arr[idx_to_zero] = 0
        circle[circle == 1] = ones_arr
    return circle


def data_gen(n, ndata, ncircle, mu = None, sigma = None, rmin = None, rmax = None, threshold = 0.3, seed = None):
    """data_gen create set of data containing sparse matrixes of ones in txt
    format. Data are created in a folder named 'data' in the current directory.

    Parameters
    ----------
    n : int
        The linear size of the grid.
    ndata : int
        The number of data set to generate.
    ncircle : int
        The number of circle in each sparse matrix.
    mu : float, greater than or equal to zero, lower than the grid linear size
        The mean for the normal distribution.
    sigma : float, positive value
        The standard deviation for the normal distribution.
    rmin : float, greater than or equal to zero, lower than rmax
        The minimum radius for the uniform extraction.
    rmax : float, positive value, greater than rmin
        The maximum radius for the uniform extraction.
    threshold : float
        Parameter that controll the extraction, i.e. lower values correspond to
        higer number of ones in the returned matrix and vice versa.
    seed : int, default = None
        The seed for the random numbers extraction for reproducibility.

    Returns
    -------
    
    """
    np.random.seed(seed)
    if mu == None: mu = n/2
    if sigma == None: sigma = mu/2
    if rmin == None: rmin = mu/4
    if rmax == None: rmax = mu
    circle = np.zeros((n, n), dtype=int)

    zerosdata = len(str(ndata - 1)) 
    zeroscirc = len(str(ncircle - 1)) 
    
    # get the working directory
    work_dir = os.getcwd()
    # define the data directory
    data_dir = os.path.join(work_dir,"data")
    #if the directory does not exist, you can create it
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    os.chdir(data_dir)
    mu0 = mu
    try:
        for i in range(ndata):
            list_info = '    cx    cy    r    ncircle    \n'
            for j in range(ncircle):
                mu = mu0 + (-1)**(j+i)*n/6
                c, r = center_radius_generator(mu, sigma, rmin, rmax, n)
                circle = np.logical_or(circle_generator(n, c, r), circle)
                list_info += f'    {c[0]}    {c[1]}    {r}    {ncircle}    \n'
            circle = rnd_circle_pruning(circle, threshold = threshold)
            np.savetxt(f'{str(ncircle).zfill(zeroscirc)}circle_{str(i).zfill(zerosdata)}.txt', circle, fmt='%0.f' ,header=list_info)
            circle = np.zeros((n, n), dtype=int)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info() 
        print(exc_tb.tb_lineno, ':', e)
    os.chdir(work_dir)
