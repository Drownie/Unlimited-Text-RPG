from cmath import pi
import json
import random as rdm

from sqlalchemy import true

class Game:
	def __init__(self):
		playerJSON = open("player.json", "r")
		artifactJSON = open("artifact.json", "r")
		potionJSON = open("potions.json", "r")
		self.players = json.load(playerJSON)
		self.artifact = json.load(artifactJSON)
		self.potions = json.load(potionJSON)
		self.player = None
		# self.player = self.players[str(rdm.randint(0, 2))]

	def refresh(self):
		playerJSON = open("player.json", "r")
		self.players = json.load(playerJSON)

	def Start(self):
		self.refresh()
		print("======== Roles ========")
		for i in range(len(self.players)):
			print("%s. "%(i+1) + self.players[str(i)]["name"])

		role = int(input("\nRole > "))
		self.player = self.players[str(role-1)]
		self.player["coins"] = 100
		self.player["level"] = 1
		self.player["exp"] = 0
		self.player["exp_container"] = 100
		self.inventory = []
		self.bodyPart = {"head": None, "neck": None, "body": None, "left hand": None, "right hand": None, "leg": None, "foot": None}
		self.Menu()

	def Menu(self):
		while True:
			print(f"""
======== Options ========
1. My Stats
2. Fight
3. Home
4. Shop
5. {"Quit" if self.player["health"] > 0 else "Restart"}
""")
			decision = int(input("Decision > "))
			if (decision == 1):
				print("\n======== Stats ========")
				for i in self.player.keys():
					print("%s = %s"%(i, self.player[i]))
				# print(self.player)
			elif (decision == 2):
				self.Fight()
			elif (decision == 3):
				self.Home()
			elif (decision == 4):
				self.shop()
			elif (decision == 5):
				if (self.player["health"] > 0):
					break
				else:
					self.Start()
			elif (decision == 6):
				print("Health recovered")
				self.player["health"] = self.player["max_health"]
			elif (decision == 7):
				print("exp increased by 100")
				self.player["exp"] += 100
				self.level_up()
			elif (decision == 8):
				print("get 100 coins")
				self.player["coins"] += 100

	def Home(self):
		if (self.player["health"] > 0):
			recover = min(((rdm.randint(0, 4) * .1) * self.player["max_health"]), (self.player["max_health"] - self.player["health"]))
			self.player["health"] += recover
			print(f"Player has recovered {recover} health")
			if (recover == 0):
				print("Your health is full")
		else:
			print("\nYour player is dead, please buy revive potion first")

	def Fight(self):
		self.refresh()
		player = self.player
		enemy = self.enemyBalancing(player["level"], self.players[str(rdm.randint(0, 2))])
		playerLine = 20
		enemyLine = 20
		self.displayFight(player, enemy)
		while enemy["health"] > 0 and player["health"] > 0:
			playerLine -= player["attack_speed"]
			enemyLine -= enemy["attack_speed"]
			# print(playerLine, enemyLine)
			if (playerLine < enemyLine):
				playerLine += player["attack_speed"] * 2
				enemy["health"] -= (player["basic_attack"] - enemy["armor"])
				print("Player attack, enemy's health = %s"%enemy["health"])
			else:
				enemyLine += enemy["attack_speed"] * 2
				player["health"] -= (enemy["basic_attack"] - player["armor"])
				print("Enemy attack, player's health = %s"%player["health"])
		
		print("\n================\n")
		if (player["health"] > enemy["health"]):
			print("Player win")
			self.reward()
		elif (player["health"] < enemy["health"]):
			print("Enemy win")
		else:
			print("Draw")
		print("\n================")

	def enemyBalancing(self, playerLevel, enemy):
		print("\n")
		key = list(enemy.keys())
		key.remove("name")
		print(key)
		for i in range(playerLevel - 1):
			random_attribute = rdm.choices(key)[0]
			print(f"Enemy's {random_attribute} attribute got buffed by 20%")
			if (random_attribute == "health"):
				enemy["max_health"] *= 1.2
			else:
				enemy[random_attribute] *= 1.2
			enemy["health"] = enemy["max_health"]
		return enemy

	def displayFight(self, player, enemy):
		print("\n================\n")
		print("Player Vs Enemy")
		for i in enemy.keys():
			print(f'{i} = {player[i]} | {i} = {enemy[i]}')
		print("\n================\n")

	def reward(self):
		self.player["health"] += min(25, (self.player["max_health"] - self.player["health"]))
		exp = rdm.randint((20 * (self.player["level"])), (50 * (self.player["level"])))
		coins = rdm.randint(1, 50)
		self.player["exp"] += exp
		self.player["coins"] += coins
		print(f"You get {exp} exp point")
		print(f"You get {coins} coins")
		self.level_up()

	def level_up(self):
		if (self.player["exp"] >= self.player["exp_container"]):
			print("You Level Up")
			self.player["level"] += 1
			self.player["exp"] = self.player["exp"] - self.player["exp_container"]
			self.player["exp_container"] *= 1.5
			key = list(self.player.keys())
			key.remove("name")
			key.remove("coins")
			key.remove("level")
			key.remove("exp")
			key.remove("exp_container")
			random_attribute = rdm.choices(key)[0]
			# print(random_attribute)
			print(f'Your {random_attribute} attribute is increased by 20%')
			if (random_attribute == "health"):
				self.player["max_health"] *= 1.2
			else:
				self.player[random_attribute] *= 1.2
			self.player["health"] = self.player["max_health"]

	def backpack(self):
		while True:
			print("\n======== Backpack ========")
			print(f"Coins: {self.player['coins']}")
			for i, item in enumerate(self.inventory):
				print(f"{i+1}. {item['name']}")
			print(f"{len(self.inventory)+1}. Un-Bind")
			print(f"{len(self.inventory)+2}. Back\n")

			use = int(input("Use > "))
			if (use > 0 and use < len(self.inventory)+1):
				self.useItem(use - 1)
			elif (use == len(self.inventory)+1):
				print("\nun bind on Progress\n")
				self.unbindMenu()
			elif (use == len(self.inventory)+2):
				break
			elif (use == 100):
				print(self.player)

	def bindArtifact(self, item, index):
		part = item["position"]
		if (self.bodyPart[part] == None):
			self.bodyPart[part] = item
			print(f"Player equiped the {item['name']}")
			self.inventory.pop(index)
			if (item['type'] == 'attack'):
				self.player['basic_attack'] += item['value']
				print(f"Player basic attack increased by {item['value']} points")
			elif (item['type'] == 'defense'):
				self.player['armor'] += item['value']
				print(f"Player armor increased by {item['value']} points")
			elif (item['type'] == 'speed'):
				self.player['attack_speed'] += item['value']
				print(f"Player attack speed increased by {item['value']} points")
			elif (item['type'] == 'life'):
				self.player['max_health'] += item['value']
				print(f"Player max health increased by {item['value']} points")
		else:
			print(f"The player already have an item on their {part}")

	def unbindMenu(self):
		while True:
			index = 1
			tmp = []
			print("\n======== Equipment ========")
			for equipment in self.bodyPart.values():
				if (equipment != None):
					print(f"{index}. {equipment['name']}")
					index += 1
					tmp.append(equipment)
			print(f"{index}. Back\n")

			unequip = int(input("unequip > "))
			if (unequip > 0 and unequip < index):
				self.unbindArtifact(tmp[unequip - 1])
			elif (unequip == index):
				break

	def unbindArtifact(self, item):
		part = item["position"]
		if (self.bodyPart[part] != None):
			self.inventory.append(self.bodyPart[part])
			self.bodyPart[part] = None
			print(f"Player unequiped the {item['name']}")
			if (item['type'] == 'attack'):
				self.player['basic_attack'] -= item['value']
				print(f"Player basic attack decreased by {item['value']} points")
			elif (item['type'] == 'defense'):
				self.player['armor'] -= item['value']
				print(f"Player armor decreased by {item['value']} points")
			elif (item['type'] == 'speed'):
				self.player['attack_speed'] -= item['value']
				print(f"Player attack speed decreased by {item['value']} points")
			elif (item['type'] == 'life'):
				self.player['max_health'] -= item['value']
				print(f"Player max health decreased by {item['value']} points")
		else:
			print(f"Player doesn't equip anything on {part}")

	def useItem(self, index):
		selected = self.inventory[index]
		print(f"You use {selected['name']}")
		if (selected['class'] == 'artifact'):
			self.bindArtifact(selected, index)
			
		elif (selected['class'] == 'potions'):
			if (selected['type'] == 'recovery'):
				if (self.player['health'] > 0):
					print(f"Recover {selected['value'] * 100}% of Max HP")
					self.player['health'] += self.player['max_health'] * selected['value']
					if (self.player['health'] >= self.player['max_health']):
						print(f"Player HP is already full")
						self.player['health'] = self.player['max_health']
					self.inventory.pop(index)
				else:
					print("The player is dead, please use recovery potion to revive the player")
			elif (selected['type'] == 'revive'):
				if (self.player['health'] <= 0):
					self.player['health'] = self.player['max_health']
					print("Player is revived")
					self.inventory.pop(index)
				else:
					print("Can't use revive potion, while the player is alive")

	def shop(self):
		while True:
			print("""
======== Options ========
1. Artifacts
2. Potions
3. Gacha (50)
4. Sell Items
5. Bag
6. Back
""")
			decision = int(input("decision > "))
			if (decision == 1):
				while True:
					print("\n======== Options ========")
					for i in range(len(self.artifact)):
						print(f"{i+1}. {self.artifact[i]['name']} ({self.artifact[i]['price']})")
					print(f"{len(self.artifact)+1}. Back\n")

					decision2 = int(input("decision > "))
					if (decision2 > 0 and decision2 < len(self.artifact)+1):
						selected = self.artifact[decision2 - 1]
						if (self.player["coins"] >= selected["price"]):
							self.player["coins"] -= selected["price"]
							print(f"You buy {selected['name']}")
							self.inventory.append(selected)
						else:
							print("You dont have enough coins")
					if (decision2 == len(self.artifact)+1):
						break
			if (decision == 2):
				while True:
					print("\n======== Options ========")
					for i in range(len(self.potions)):
						print(f"{i+1}. {self.potions[i]['name']} ({self.potions[i]['price']})")
					print(f"{len(self.potions)+1}. Back\n")
					
					decision2 = int(input("decision > "))
					if (decision2 > 0 and decision2 < len(self.potions)+1):
						selected = self.potions[decision2 - 1]
						if (self.player["coins"] >= selected["price"]):
							self.player["coins"] -= selected["price"]
							print(f"You buy {selected['name']}")
							self.inventory.append(selected)
						else:
							print("You dont have enough coins")
					if (decision2 == len(self.potions)+1):
						break
			if (decision == 3):
				if (self.player["coins"] >= 50):
					self.player["coins"] -= 50
					prize_pool = [] + self.artifact + self.potions
					for i in range(len(prize_pool)*2):
						prize_pool.append({"name": "Zonk"})
					picked = rdm.choices(prize_pool)[0]
					print(f"You get {picked['name']} from gacha")
					if (picked["name"] != "Zonk"):
						self.inventory.append(picked)
				else:
					print("You dont have enough coins")
			if (decision == 4):
				while True:
					print("\n======== Options ========")
					for i, inv in enumerate(self.inventory):
						print(f"{i+1}. {self.inventory[i]['name']} ({int(self.inventory[i]['price'] * .60)})")
					print(f"{len(self.inventory)+1}. Back\n")

					decision2 = int(input("decision > "))
					if (decision2 > 0 and decision2 < len(self.inventory)+1):
						print(f"\nCoins = {self.player['coins']}")
						print(f"You sell {self.inventory[decision2 - 1]['name']} for {int(self.inventory[decision2 - 1]['price'] * .6)} coins")
						self.player["coins"] += int(self.inventory[decision2 - 1]['price'] * .6)
						self.inventory.pop(decision2 - 1)
						print(f"Coins = {self.player['coins']}")
						print(self.inventory)
					if (decision2 == len(self.inventory)+1):
						break
			if (decision == 5):
				self.backpack()
			if (decision == 6):
				break

g = Game()
g.Start()
# g.shop()