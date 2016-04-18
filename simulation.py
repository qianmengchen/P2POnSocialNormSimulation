#!/usr/bin/python
#!python

import random
import matplotlib.pyplot as plt
import math
import sys

s = raw_input("Please input the reward: ")
try:
	reward = int(s)
except ValueError:
	reward = 10
	print "set reward to default 10"

s = raw_input("Please input the cost: ")
try:
	cost = int(s)
except ValueError:
	cost = 2
	print "set cost to default 2"

s = raw_input("Please input the upper limit of reputation: ")
try:
	L = int(s)
except ValueError:
	L = 100
	print "set L to default 100"

s = raw_input("Please input the threshold of reputation: ")
try:
	h0 = int(s)
except ValueError:
	h0 = int(L*0.2)
	print "set h0 to default "+str(h0)

s = raw_input("Please input the number of peers: ")
try:
	num = int(s)
except ValueError:
	num = 200
	print "set num to default 200"

s = raw_input("Please input the probability of connectivity error: ")
try:
	varepsilon = float(s)
except ValueError:
	varepsilon = 0.05
	print "set varepsilon to default 0.05"

s = raw_input("Please input the probability of forgiveness: ")
try:
	beta = float(s)
except ValueError:
	beta = 0.3
	print "set beta to default 0.3"

s = raw_input("Please input the probability of encounter: ")
try:
	encounterProb = float(s)
except ValueError:
	encounterProb = 0.3
	print "set encounterProb to default 0.3"

s = raw_input("Please input the ratio of malicious peer: ")
try:
	maliciousRatio = float(s)
except ValueError:
	maliciousRatio = 0.02
	print "set maliciousRatio to default 0.02"

s = raw_input("Please input the ratio of altruistic peer: ")
try:
	altruisticRatio = float(s)
except ValueError:
	altruisticRatio = 0.1
	print "set altruisticRatio to default 0.1"

s = raw_input("Please input the time duration of simulation: ")
try:
	ticks = int(s)
except ValueError:
	ticks = 3000
	print "set ticks to default 3000"

alpha = varepsilon #since \lambda*b is defined as 1

class PeerType():
	unset = 0
	reciprocative = 1
	malicious = 2
	altruistic = 3

class peer:
	def __init__(self):
		self.reputation = 0
		self.utility = 0.0
		self.type = PeerType.unset;

## set \lambda*b to 1
def serve(server, client):
	if server.type == PeerType.malicious:
		server.utility = server.utility - cost
		client.utility = client.utility - cost
		return False
	if (server.reputation >= h0 and client.reputation >= h0) or server.type == PeerType.altruistic:
		server.utility = server.utility - cost
		random.seed()
		success = random.random()
		if(success >= varepsilon):
			client.utility = client.utility + (reward - cost)
			return True
		else:
			client.utility = client.utility - cost
			return False

distribution = [0 for x in range(0, L+1)]
distribution[0] = num
## Not necessary

allPeers = []
for i in range(num):
	allPeers.append(peer())
count = 0
while count < maliciousRatio*num:
	while True:
		pos = random.randint(0, num-1)
		if allPeers[pos].type == PeerType.unset:
			allPeers[pos].type = PeerType.malicious
			count = count + 1
			break
count = 0
while count < altruisticRatio*num:
	while True:
		pos = random.randint(0, num-1)
		if allPeers[pos].type == PeerType.unset:
			allPeers[pos].type = PeerType.altruistic
			count = count + 1
			break

for x in allPeers:
	if x.type == PeerType.unset:
		x.type = PeerType.reciprocative

plot = [[0 for t in range(ticks+1)] for x in range(0, L+1)]
ratio = [0.0 for t in range(ticks+1)]

theory = [[0.0 for t in range(ticks+1)] for x in range(0, L+1)]
theory[0][0] = num;
Theory_active = [0.0 for x in range(ticks+1)]
Theory_active[0] = 0
Theory_ratio = [0.0 for t in range(ticks+1)]

def punish(someone):
	prob = random.random()
	if prob >= math.pow(beta, L-someone.reputation+1):
		someone.reputation = 0

#prev_percent = 0
for t in range(ticks+1):
	distribution = [0 for x in range(0, L+1)]
	for cur in range(len(allPeers)):
		random.seed()
		prob = random.random()
		if prob < encounterProb:
			objID = random.randint(0, num-1)
			while objID == cur:
				objID = random.randint(0, num-1)
			if allPeers[cur].reputation < h0 or serve(allPeers[cur], allPeers[objID]):
				allPeers[cur].reputation = min(allPeers[cur].reputation + 1, L)
			else:
				punish(allPeers[cur])
		else:
			allPeers[cur].reputation = min(allPeers[cur].reputation + 1, L)
		distribution[allPeers[cur].reputation] = distribution[allPeers[cur].reputation] + 1
	activeNum = 0
	for i in range(h0, L+1):
		activeNum = activeNum + distribution[i]
	percent = int(t / float(ticks) * 100)
	print "Progress %d %% \r" %percent,
	sys.stdout.flush()
	#print distribution
	for x in range(0, L+1):
		plot[x][t] = distribution[x]
	if t >= 1:
		for x in range(0, L+1):
			if x == L:
				theory[x][t] = (1-alpha+alpha*beta)*theory[x][t-1] + (1-alpha)*theory[x-1][t-1]
			elif x >= h0+1:
				theory[x][t] = (1-alpha)*theory[x-1][t-1] + alpha*math.pow(beta, L-x+1)*theory[x][t-1]
			elif x == h0:
				theory[x][t] = theory[x-1][t-1] + alpha*math.pow(beta, L-x+1)*theory[x][t-1]
			elif x >= 1:
				theory[x][t] = theory[x-1][t-1]
			else:
				theory[x][t] = 0;
				for y in range(h0, L+1):
					theory[x][t] = theory[x][t] + alpha*(1-math.pow(beta, L-y+1))*theory[y][t-1]
	for x in range(h0, L+1):
		Theory_active[t] = Theory_active[t] + theory[x][t]
	Theory_ratio[t] = Theory_active[t]/float(num)
	ratio[t] = activeNum/float(num)
	#print "active ratio: " + str(activeNum/float(num))
	#print '\n'

#print plot[0]
print " "*20 + "\r"
print "Complete!"
txt = '$L = {0}$, $\\alpha = {1}$, $h_0 = {2}$, $num = {3}$\n$\\beta = {4}$, $encounter probability = {5}$, $forgiveness probability = {6}$\n$malicious ratio = {7}$, $altrustic ration = {8}$'.format(L, alpha, h0, num, beta, encounterProb, beta, maliciousRatio, altruisticRatio)
plt.figure(1)
#plt.text(.1, .1, "Simulation:\n" + txt)
plt.subplot(211)
plt.title("Distribution")
for x in range(0, L+1):
	plt.plot(plot[x], label = str(x))
plt.xlabel('Time')
plt.axis([0, ticks, 0, num+1])
plt.ylabel('Number')

plt.subplot(212)
plt.plot(ratio)
plt.title("Ratio")
plt.xlabel('Time')
plt.ylabel('Active Ratio')
plt.axis([0, ticks, 0, 1])

plt.figure(2)
plt.subplot(211)
plt.title("Theoretical Distribution")
for x in range(0, L+1):
	#print theory[x]
	plt.plot(theory[x], label = str(x))
plt.xlabel('Time')
plt.axis([0, ticks, 0, num+1])
plt.ylabel('Number')

plt.subplot(212)
#plt.text(.1, .1, "Theory:\n" + txt)
plt.plot(Theory_ratio)
plt.title("Theoretical Ratio")
plt.xlabel('Time')
plt.ylabel('Active Ratio')
plt.axis([0, ticks, 0, 1])
plt.show()

plt.close('all')
