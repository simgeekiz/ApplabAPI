import pandas as pd


class getScore():
	def __init__(self):
		self.U = 1.
		self.K = 0.0075
		
	def readData(self):
		filePath = "D:\\Radboud\\Third Semester\\App-Lab\\Applab_git\\app\\src\\main\\res\\raw\\data.csv";
		csv_data = pd.read_csv(filePath, header=None)
		
		df_data = pd.dataFrame(csv_data)
	

	def computeUncertainty(self, days):
		# Equation (5) in Klinkerberg's paper
		self.U = self.U - 1/40 + 1/30 * days
		return self.U
		
	
	def computeDevFromExp(self):
		# Equation (4) in Klinkerberg's paper
		K = self.K
		if self.U == 0:
			# c has default value when there is no uncertainty
			K = 0.0075
		K_p = 4
		K_m = .5
			
		self.K = K * (1 + K_p * self.U - K_m * self.U)
		return self.K
		
	def computeERS(self):
		# Equation (3) in Klinkenberg's paper
		self.ERS_player = self.K * (s_j - Es_j) #ability estimate for person
		self.ERS_item = self.K * (Es_j - s_j)

if __name__ == "__main__":
	gs = getScore()
	daysNotUsed = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 10, 10, 6]
	for d in daysNotUsed:
		print("Uncertainty:" , gs.computeUncertainty(d))
		print("Deviation from expectation:" , gs.computeDevFromExp())