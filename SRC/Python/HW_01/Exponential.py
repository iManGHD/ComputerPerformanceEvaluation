
'''
    Author : Iman Ghadimi
    S.Num : 99210742
    Date : 11/27/2022
'''

# Calling Libraries :

import numpy as np
from queue import Queue
import math
import random

# Customer :

class Customer:

    def __init__(self, id, arrival_time, waiting_time, service_time):
        self.arrival_time = arrival_time
        self.waiting_time = waiting_time
        self.service_time = service_time
        self.id = id

    def __str__(self):
        return "id:" + str(self.id) + "\t arrival time:" + str(self.arrival_time) + "\t waiting time:" + str(
            self.waiting_time)

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

# Event :

class Event:

    def __init__(self, customer_id, type_idx, occ_time):
        self.types = ['arrival', 'deadline', 'done']
        self.type_idx = type_idx
        self.occ_time = occ_time
        self.customer_id = customer_id

    def __str__(self):
        return "customer id:" + str(self.customer_id) + "\t occurence time:" + str(self.occ_time) + "\t type:" + str(
            self.types[self.type_idx])

    def __lt__(self, other):
        return self.occ_time < other.occ_time

    def __le__(self, other):
        return self.occ_time <= other.occ_time

    def __sub__(self, other):
        if isinstance(other, Event):
            return self.occ_time - other.occ_time
        else:
            return self.occ_time - other

def exp_rv(rate):
    return -1.0 * np.log(1.0 - random.random()) / rate

# Binary Searching :

def BS(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
    while low <= high:
        mid = (high + low) // 2
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return mid
    return low

# Insertion :

def insertion(arr, value):
    idx = BS(arr, value)
    if idx >= len(arr):
        idx = len(arr)
        arr.insert(idx, value)
    else:
        if value <= arr[idx]:
            arr.insert(idx, value)
        else:
            while idx <= len(arr) - 1 and value > arr[idx]:
                idx += 1
            arr.insert(idx, value)
    return arr

# Making Customer :

def creat_customer(pre_cc_time, id):
    if const_theta:
        waiting_time = theta
    else:
        waiting_time = exp_rv(1.0 / theta)

    service_time = exp_rv(mu)
    arrival_time = pre_cc_time + exp_rv(lamda_value)
    customer = Customer(id, arrival_time, waiting_time, service_time)
    return customer

def phi_n(n, is_const_theta, mu, theta):
    if not is_const_theta:
        denom = 1
        for i in range(n + 1):
            denom *= (mu + (i / theta))
        return math.factorial(n) / (denom)
    else:
        summation = 0
        for i in range(n):
            summation += ((mu * theta) ** i / math.factorial(i))
        return (math.factorial(n) / mu ** (n + 1)) * (1 - math.exp(-1 * mu * theta) * summation)

# P(i) :

def p_n(n, p0, lamba, is_const_theta, mu, theta):
    if n == 1:
        return p0 * lamba / mu
    else:
        return p0 * lamba ** n * phi_n(n - 1, is_const_theta, mu, theta) / math.factorial(n - 1)

# P_0 :

def p_0(lamba, constant_theta, mu, theta):
    sum = 0
    for i in range(2, 15):
        sum += lamba ** i * phi_n(i - 1, constant_theta, mu, theta) / math.factorial(i - 1)
    p0 = 1.0 / (1 + lamba / mu + sum)
    return p0

        # ============================= Main =============================

if __name__ == "__main__":

    # Reading parameters :

    f = open("parameters.conf", "r")
    theta = int(f.readline())
    mu = int(f.readline())

    const_theta = False
    Customers = 1_000_000

    for lamba in np.arange(0.1,3.1,0.1):

        lamda_value = lamba

        ###  Analytics  ###

        p0 = p_0(lamba, const_theta, mu, theta)

        # P_b

        pb_analytics = p_n(14, p0, lamba, const_theta, mu, theta)

        # P_d

        pd_analytics = 1 - pb_analytics - (mu / lamba) * (1 - p0)

        # Nc

        Nc_analytics = 0
        i= 1
        while i<= 14:
            Nc_analytics += (i* p_n(i, p0, lamba, const_theta, mu, theta))
            i = i+ 1

        ### Simulation ###

        arrival_time = 0
        pre_cc_time = 0

        # cc : created customer
        cc = creat_customer(pre_cc_time, id=0)

        queue = []

        Blocks = 0
        DeadLined = 0
        Nc_total = 0
        Nc_simulation = 0

        events = []

        time = 0
        counter = 0

        events.append(Event(counter, type_idx=0, occ_time=cc.arrival_time))
        pre_cc = cc
        counter += 1

        nxt_cc= creat_customer(cc.arrival_time, 1)
        done = False

        # Main Loop :

        while len(events) > 0 or counter < Customers:
            if counter < Customers:
                if len(events) == 0:
                    events.append(Event(counter, type_idx=0, occ_time=nxt_cc.arrival_time))
                    counter += 1
                    pre_cc= nxt_cc
                    nxt_cc= creat_customer(pre_cc.arrival_time, counter)
                elif nxt_cc.arrival_time < events[0].occ_time:
                    events.insert(0, Event(counter, type_idx=0, occ_time=nxt_cc.arrival_time))
                    counter += 1
                    pre_cc= nxt_cc
                    nxt_cc= creat_customer(pre_cc.arrival_time, counter)

            event = events.pop(0)
            time = event.occ_time

            if event.type_idx == 0:
                if len(queue) >= 14:
                    Blocks += 1
                    Nc_total += len(queue)
                else:
                    customer = pre_cc
                    queue.append(customer)

                    if len(queue) == 1:
                        insertion(events, Event(event.customer_id, 2, time + customer.service_time))
                    else:
                        insertion(events, Event(event.customer_id, 1, time + customer.waiting_time))

            # DeadLine :

            if event.type_idx == 1:
                customer = next((x for x in queue if x.id == event.customer_id), None)

                if customer and (customer.id != queue[0].id):
                    queue.remove(customer)
                    DeadLined += 1
                    Nc_total += len(queue)

            # Done :

            if event.type_idx == 2:
                customer = next((x for x in queue if x.id == event.customer_id), None)
                queue.remove(customer)
                Nc_total += len(queue)

                if len(queue) >= 1:
                    cc = queue[0]

                    for event in events:
                        if event.customer_id == cc.id and event.type_idx == 1:
                            events.remove(event)
                            break

                    insertion(events, Event(cc.id, 2, time + cc.service_time))

        pb_simulation = Blocks / Customers
        pd_simulation = DeadLined / Customers
        Nc_simulation = Nc_total / Customers

        print("lambda : ", lamba)
        with open('Exponential.txt', 'a') as f:
            f.writelines(str(pb_simulation) + "\t" + str(pb_analytics) + "\t\t" + str(pd_simulation) + "\t" + str(pd_analytics) + "\t\t" + str(Nc_simulation) + "\t" + str(Nc_analytics) + "\n")
