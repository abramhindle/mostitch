def partfun(a,b):
	if (a > 299 and a <= 410 and b <= 410):
		return "D"
	elif (b > 408 and b <= 423 and b > 410):
		return "A"
	elif (a > 153 and a <= 338 and a > 181 and b <= 238 and a > 199 and a <= 232):
		return "B"
	elif (a > 152 and a > 338 and b <= 459 and a > 423 and a > 436):
		return "C"
	elif (b <= 92 and b <= 53 and b <= 38):
		return "A"
	elif (a > 152 and b <= 354 and a > 233 and b <= 238 and a <= 266):
		return "B"
	elif (a > 152 and b <= 354 and b > 238 and a <= 277 and b <= 301):
		return "D"
	elif (b <= 92 and b <= 53 and a > 42 and b <= 44):
		return "A"
	elif (a > 152 and b <= 354 and b > 167 and a <= 181 and b <= 181):
		return "C"
	elif (b <= 92 and b > 69):
		return "A"
	elif (b > 459):
		return "D"
	elif (a <= 83 and b <= 53 and a > 43 and a <= 53 and a <= 52 and a > 49):
		return "A"
	elif (b > 417 and a <= 433 and a > 423):
		return "C"
	elif (a > 167 and b > 354 and a > 411):
		return "A"
	elif (a > 153 and a > 167 and b <= 301 and b <= 251 and a > 181 and a <= 216):
		return "B"
	elif (a > 152 and b > 354 and b <= 409 and b > 408):
		return "A"
	elif (a > 152 and a > 167 and b > 251 and b <= 301):
		return "B"
	elif (a > 152 and a > 167 and b > 267 and a <= 302):
		return "B"
	elif (a > 152 and a > 167 and b <= 303):
		return "B"
	elif (a > 152 and b > 165 and b > 166):
		return "D"
	elif (a <= 83 and b <= 53 and a > 43 and a <= 53):
		return "B"
	elif (b <= 70 and b <= 52 and a > 40 and b > 39):
		return "A"
	elif (b <= 70 and b > 56 and a > 55):
		return "D"
	elif (a <= 128 and a > 83 and b <= 196):
		return "C"
	elif (b <= 150 and b > 55 and a <= 141 and a > 54 and b > 70 and b > 130):
		return "B"
	elif (a > 153 and b <= 165 and a > 156 and a <= 165):
		return "B"
	elif (b <= 150 and b > 141):
		return "A"
	elif (a > 152 and b <= 165 and b > 153 and b <= 155):
		return "D"
	elif (b > 146 and a <= 153 and b <= 338 and a > 141):
		return "A"
	elif (b > 165 and a <= 118 and a > 94):
		return "A"
	elif (b > 147 and b > 165):
		return "C"
	elif (b > 105 and a <= 150 and b > 134):
		return "B"
	elif (b > 105 and b > 154 and a > 161):
		return "D"
	elif (b > 105):
		return "C"
	elif (b > 55 and b <= 57):
		return "B"
	elif (b > 56 and b <= 94):
		return "A"
	elif (b > 70 and a <= 98):
		return "B"
	elif (a > 98 and b <= 70):
		return "B"
	elif (a > 44 and b <= 70):
		return "D"
	elif (a <= 41 and a <= 40 and a > 39 and b <= 40):
		return "D"
	elif (b > 39):
		return "A"
	else:
		return "B"

