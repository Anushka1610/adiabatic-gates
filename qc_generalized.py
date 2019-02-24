import pandas as pd
import numpy as np
import itertools
data = []
temp=[]

fileOutput = open("qiskitProgram.py", "w")
fileOutput.write("import numpy as np\n")
fileOutput.write("import matplotlib.pyplot as plt \n")
fileOutput.write("from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister\n")
fileOutput.write("from qiskit import available_backends, execute\n")
fileOutput.write("from qiskit.tools.visualization import matplotlib_circuit_drawer as drawer, qx_color_scheme\n")
fileOutput.write("from qiskit.tools.visualization import circuit_drawer\n")

inputNum=int(input("Enter number of input qubits: "))
outputNum=int(input("Enter number of output qubits: "))

totalQubits = inputNum + outputNum

weights = [0]*totalQubits
strengths = [[0]*(totalQubits) for i in range(totalQubits-1)]

for i in range(totalQubits):
	inputString = "Enter weight " + str(i+1) + ": "
	weights[i] = float(input(inputString))


for i in range(1,totalQubits):
	for j in range(i+1,totalQubits+1,1):
		inputString = "Enter strength " + str(i) + " - " + str(j) + ": "
		strengths[i-1][j-1] = float(input(inputString))

fileOutput.write("\n")

fileOutput.write("qx = QuantumRegister(" + str(inputNum)+ ") \n")
fileOutput.write("cx = ClassicalRegister(" + str(inputNum)+ ") \n")
if inputNum-2 != 0:
	fileOutput.write("qa = QuantumRegister(" + str(inputNum-2)+ ") \n")
	fileOutput.write("ca = ClassicalRegister(" + str(inputNum-2)+ ") \n")
fileOutput.write("qz = QuantumRegister(" + str(outputNum)+ ") \n")
fileOutput.write("cz = ClassicalRegister(" + str(outputNum)+ ") \n")
if inputNum-2 != 0:
	fileOutput.write("circuit = QuantumCircuit(qx,qz,qa,cx,cz,ca) \n")		
else:
	fileOutput.write("circuit = QuantumCircuit(qx,qz,cx,cz) \n")

fileOutput.write("\n")

fileOutput.write("a=np.zeros(("+str(inputNum)+"))\n")
fileOutput.write("for i in range("+str(inputNum)+"):\n")
fileOutput.write("\ta[i]=int(input(\"Enter input bit \" + str(i) + \" : \" ))\n")
fileOutput.write("\tif a[i] == 1:\n")
fileOutput.write("\t\tcircuit.x(qx[i])\n")



table = list(itertools.product(range(2), repeat=totalQubits))

objective = 0.0
for row in table:
	for i in range (totalQubits):
		objective+= row[i]*weights[i]	
	for i in range(totalQubits-1):
		for j in range(1+i,totalQubits,1):
			objective+=row[i]*row[j]*strengths[i][j]
	temp =list(row)
	temp.append(objective)
	objective = 0.0
	data.append(temp)

print(data)

minimum = 10000

flipInput = False
doubleFlip = False
midFlag = True
for row in data:
	if row[totalQubits]<=minimum:
		minimum = row[totalQubits]

print("Minimum values")
for row in data:
	if row[totalQubits] == minimum:
		print(row)

for row in data:
	if row[totalQubits] != minimum:
		continue
	else:
		for i in range (inputNum, totalQubits, 1):
			binaryValues = row
			if binaryValues[i] == 0:
				continue
			else:	
				for j in range (inputNum):
					if binaryValues[j] == 1:
						j-=1
						break

				if j == (inputNum-1):
					flipInput = True

if flipInput==True:
	for row in data:
		if row[totalQubits]==minimum:
			binaryValues = row[0:totalQubits]
			for i in range (inputNum):
				binaryValues[i] = 1 - binaryValues[i]
			row[0:totalQubits] = binaryValues	

if flipInput == True:
	for i in range(inputNum):
		fileOutput.write("circuit.x(qx[" + str(i) + "])\n")

fileOutput.write("\n")

numberOfControls = 0
controlLocations = [0]*inputNum
for row in data:
	if row[totalQubits]==minimum:
		for i in range (inputNum, totalQubits, 1):
			if row[i] == 1:
				for j in range(inputNum):
					if row[j] == 1:
						numberOfControls +=1
						controlLocations[j]=1

				if numberOfControls == 1:
					for j in range(inputNum):
						if controlLocations[j] == 1:
							fileOutput.write("circuit.cx(qx[" + str(j) + "], qz[" + str(i-inputNum) + "])\n")
							break

				if numberOfControls == 2:
					fileOutput.write("circuit.ccx(")
					for j in range(inputNum):
						if controlLocations[j] == 1:
							fileOutput.write("qx[" + str(j) + "],")
					fileOutput.write("qz[" + str(i-inputNum) + "])\n")		

				if numberOfControls >= 3:
					controlsAdded = 0
					jLastPosition = 0
					fileOutput.write("circuit.ccx(")
					for j in range(inputNum):
						if controlLocations[j] == 1:
							controlsAdded+=1
							fileOutput.write("qx[" + str(j) + "],")
						if controlsAdded == 2:
							jLastPosition = j
							break	
					fileOutput.write("qa[" + str(0) + "])\n")	
					for ancillaPos in range(numberOfControls-2):
						fileOutput.write("circuit.ccx(")
						fileOutput.write("qa[" + str(ancillaPos) + "],")
						for j in range(jLastPosition+1,inputNum):
							if controlLocations[j] == 1:
								fileOutput.write("qx[" + str(j) + "],")
								jLastPosition = j
								break
						if ancillaPos == (numberOfControls-3):
							fileOutput.write("qz[" + str(i-inputNum) + "])\n")	
						else:
							fileOutput.write("qz[" + str(ancillaPos+1) + "])\n")

					controlsAdded = 0
					for k in range(ancillaPos, -1, -1):
						fileOutput.write("circuit.ccx(")
						if k == (numberOfControls-3):	
							for j in range(jLastPosition-1, -1, -1):
								if controlLocations[j] == 1:
									fileOutput.write("qx[" + str(j) + "],")
									controlsAdded+=1
								if controlsAdded == 2:
									break
							fileOutput.write("qa[" + str(ancillaPos) + "])\n")
						else:
							fileOutput.write("qa[" + str(ancillaPos) + "],")
							for j in range(jLastPosition-1, -1, -1):
								if controlLocations[j] == 1:
									fileOutput.write("qx[" + str(j) + "],")
									jLastPosition = j
									break
							fileOutput.write("qa[" + str(ancillaPos-1) + "])\n")	

			numberOfControls=0				
			controlLocations = [0]*inputNum


fileOutput.write("\n")

if flipInput == True:
	for i in range(inputNum):
		fileOutput.write("circuit.x(qx[" + str(i) + "])\n")


fileOutput.write("\n")

fileOutput.write("circuit.measure(qz,cz)\n")
fileOutput.write("circuit.measure(qx,cx)\n")

fileOutput.write("\n")

fileOutput.write("print(circuit.qasm()) \n")

fileOutput.write("\n")

fileOutput.write("# Execute\n")

fileOutput.write("\n")

fileOutput.write("print(\"Running on simulator...\")\n")
fileOutput.write("backend = 'qasm_simulator' \n")
fileOutput.write("job = execute(circuit, backend, shots=1024)\n")
fileOutput.write("result = job.result()\n")
fileOutput.write("print(result.get_counts(circuit))\n")
fileOutput.write("\n")
fileOutput.write("circuit_drawer(circuit)\n")
fileOutput.close()


