import csv
import statistics
from collections import defaultdict, deque
from pathlib import Path

# Settings
CSV_FILE = Path(__file__).with_name('house_sale_clean.csv')
APARTMENT_TYPES = {'New building', 'Old building'}


# Linked List: Stores favorite property IDs and allows adding or removing them.
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    # Checks if a property ID already exists in the Linked List.
    # Time: O(n) | Space: O(1)
    def contains(self, data):
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    # Adds a new property ID to the end of the Linked List if it doesn't already exist.
    # Time: O(n) | Space: O(1)
    def insertNode(self, data):
        if self.contains(data):
            return False
        newNode = Node(data)
        if self.head is None:
            self.head = newNode
        else:
            currentNode = self.head
            while currentNode.next:
                currentNode = currentNode.next
            currentNode.next = newNode
        return True

    # Removes a property ID from the Linked List if it exists.
    # Time: O(n) | Space: O(1)
    def deleteNode(self, data):
        current, previous = self.head, None
        while current:
            if current.data == data:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                return True
            previous, current = current, current.next
        return False

    # Returns all favorite property IDs.
    # Time: O(n) | Space: O(n)
    def traverse(self):
        values, current = [], self.head
        while current:
            values.append(current.data)
            current = current.next
        return values


# Stack: Stores the history of changes made to favorite properties,
# allowing users to undo their most recent action using LIFO.
class Stack:
    def __init__(self):
        self.items = []

    # Saves a new action to the stack.
    # Time: O(1) | Space: O(1)
    def push(self, value):
        self.items.append(value)

    # Removes and returns the most recent action to support Undo.
    # Time: O(1) | Space: O(1)
    def pop(self):
        return self.items.pop() if self.items else None


# Binary Search Tree: Stores properties by listing ID for searching.
class BSTNode:
    def __init__(self, data):
        self.data = data
        self.leftChild = None
        self.rightChild = None


# Inserts a property into the BST.
# Time: O(n) worst case | Space: O(1)
def insertBST(rootNode, data):
    if rootNode is None:
        return BSTNode(data)
    current = rootNode
    while True:
        if data["listing_id"] < current.data["listing_id"]:
            if current.leftChild is None:
                current.leftChild = BSTNode(data)
                break
            current = current.leftChild
        elif data["listing_id"] > current.data["listing_id"]:
            if current.rightChild is None:
                current.rightChild = BSTNode(data)
                break
            current = current.rightChild
        else:
            break
    return rootNode


# Searches for a property by listing ID.
# Time: O(n) worst case | Space: O(n) for the visited path
def searchBST(rootNode, listingID):
    currentNode = rootNode
    visited = []
    while currentNode:
        currentID = currentNode.data['listing_id']
        visited.append(currentID)
        if listingID == currentID:
            return currentNode.data, visited
        if listingID < currentID:
            currentNode = currentNode.leftChild
        else:
            currentNode = currentNode.rightChild
    return None, visited


# Binary Search: Finds properties within the user's selected price range.
# Since property prices are sorted, Binary Search finds the range boundaries without checking every property individually.

# Finds the index of the first property whose price is >= the minimum price.
# Used to determine where the user's selected price range starts. Time: O(log n) | Space: O(1)
def binarySearchLowerBound(values, target):
    left, right = 0, len(values)
    while left < right:
        middle = (left + right) // 2
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left


# Finds the index immediately after the last property whose price is <= the maximum price.
# Used to determine where the user's selected price range ends.
# Time: O(log n) | Space: O(1)
def binarySearchUpperBound(values, target):
    left, right = 0, len(values)
    while left < right:
        middle = (left + right) // 2
        if values[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return left


# Greedy: Selects properties with the highest estimated value per AZN within the budget.
# Time: O(n log n) | Space: O(n)
def greedyInvestment(houses, budget):
    # Sorts properties by estimated value-to-price ratio.
    items = sorted(houses, key=lambda h: h['estimated_gap'] / h['price'], reverse=True)
    remaining = budget
    selected = []

    # Selects affordable properties and updates the remaining budget.
    for house in items:
        if house['price'] <= remaining:
            selected.append(house)
            remaining -= house['price']
    return selected


# Dynamic Programming: Finds the best combination of properties to maximize estimated value within the budget.
# Time: O(n × budget) | Space: O(n × budget)
def portfolioDP(houses, budget):
    # Stores previously calculated results to avoid repeated calculations.
    tempDict = {}
    def findBest(index, remaining):
        if index >= len(houses) or remaining <= 0:
            return 0, ()
        key = (index, remaining)
        if key in tempDict:
            return tempDict[key]

        # Compares skipping the current property with including it in the portfolio.
        skipValue, skipSelection = findBest(index + 1, remaining)
        best = (skipValue, skipSelection)
        currentHouse = houses[index]
        housePrice = int(round(currentHouse['price']))
        if housePrice <= remaining:
            takeValue, takeSelection = findBest(index + 1, remaining - housePrice)
            takeValue += currentHouse['estimated_gap']
            if takeValue > best[0]:
                best = (takeValue, (index,) + takeSelection)
        tempDict[key] = best
        return best

    # Returns the optimal property selection, number of calculated states, and total estimated value.
    value, indices = findBest(0, int(budget))
    return [houses[i] for i in indices], len(tempDict), value


# Load Data: Reads property listings from the CSV file and prepares them for analysis.
# Time: O(n) | Space: O(n)
def loadHouses():
    houses = []
    # Reads each CSV row and converts property information into a dictionary.
    with CSV_FILE.open(encoding='utf-8-sig', newline='') as file:
        for row in csv.DictReader(file):
            try:
                house = {
                    'listing_id': int(float(row['listing_id'])),
                    'price': float(row['price']),
                    'category': row['category'],
                    'location': row['location'],
                    'area_m2': float(row['area_m2'] or 0),
                    'rooms': int(float(row['rooms'] or 0)),
                }

                # Keeps valid properties and initializes fields for investment analysis.
                if house['listing_id'] > 0 and house['price'] > 0:
                    house['estimated_gap'] = 0
                    house['peer_count'] = 0
                    house['discount_pct'] = None
                    houses.append(house)
            # Skips rows containing missing or invalid data.
            except (ValueError, KeyError, TypeError):
                continue
    return houses


# Price Estimation: Estimates potential property value gaps using median prices of comparable apartments.
def estimateGaps(houses):
    # Groups properties by location, building category, and number of rooms.
    exact, local, category = defaultdict(list), defaultdict(list), defaultdict(list)
    for h in houses:
        if h['category'] not in APARTMENT_TYPES or h['area_m2'] <= 10:
            continue
        unit = h['price'] / h['area_m2']
        exact[(h['location'], h['category'], h['rooms'])].append(unit)
        local[(h['location'], h['category'])].append(unit)
        category[h['category']].append(unit)

    # Selects the most specific comparison group containing at least 12 properties.
    for h in houses:
        if h['category'] not in APARTMENT_TYPES or h['area_m2'] <= 10:
            continue
        groups = [exact[(h['location'], h['category'], h['rooms'])],
                  local[(h['location'], h['category'])], category[h['category']]]
        peers = next((group for group in groups if len(group) >= 12), None)
        if peers:
            h['peer_count'] = len(peers)
            # Estimates reference value using median price per square meter.
            reference = statistics.median(peers) * h['area_m2']
            # Calculates the percentage difference and potential value gap.
            h['discount_pct'] = 100 * (1 - h['price'] / reference)
            h['estimated_gap'] = max(0, round(reference - h['price']))


# Terminal Helpers: Displays property information and handles user input.

# Displays up to 8 properties with their ID, location, category, price, and estimated value gap.
# Time: O(min(n, limit)) | Space: O(min(n, limit))
def show(houses, limit=8):
    if not houses:
        print('No matching properties.')
    for h in houses[:limit]:
        print(f"#{h['listing_id']} | {h['location'][:26]:26} | "
              f"{h['category'][:12]:12} | {h['price']:,.0f} AZN | "
              f"Gap: {h['estimated_gap']:,.0f}")
    if len(houses) > limit:
        print(f'... and {len(houses) - limit} more results')


# Reads an integer from the user and handles invalid input without crashing the program.
# Time: O(k) | Space: O(k), where k is the input length.
def readInt(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        print('Please enter a valid integer.')
        return None


# Main Menu
def main():
    if not CSV_FILE.exists():
        print(f'CSV not found: {CSV_FILE}\nRename your dataset to house_sale_clean.csv')
        return
    houses = loadHouses()
    estimateGaps(houses)
    byID = {h['listing_id']: h for h in houses}
    byPrice = sorted(houses, key=lambda h: h['price'])
    prices = [h['price'] for h in byPrice]
    root = None
    for house in houses:
        root = insertBST(root, house)
    favorites, undo, visits = LinkedList(), Stack(), deque()
    print(f'Loaded {len(houses):,} listings.')

    while True:
        print('\n=== evim.az | DSA TERMINAL ===')
        print('1. Price range (Binary Search)')
        print('2. Listing ID (Binary Search Tree)')
        print('3. Location filter')
        print('4. Favorites + Undo (Linked List / Stack)')
        print('5. Visit queue (Queue)')
        print('6. Investment: Greedy vs Dynamic Programming')
        print('0. Exit')
        choice = input('Choose: ').strip()

        if choice == '0':
            break
        elif choice == '1':
            low, high = readInt('Minimum price: '), readInt('Maximum price: ')
            if low is not None and high is not None and low <= high:
                left = binarySearchLowerBound(prices, low)
                right = binarySearchUpperBound(prices, high)
                print(f'Found {right-left} listings.')
                show(byPrice[left:right])
        elif choice == '2':
            listingID = readInt('Listing ID: ')
            if listingID is not None:
                house, path = searchBST(root, listingID)
                print(f'BST comparisons: {len(path)}')
                show([house] if house else [])
        elif choice == '3':
            location = input('Location keyword: ').strip().lower()
            result = [h for h in houses if location in h['location'].lower()]
            print(f'Found {len(result)} listings.')
            show(result)
        elif choice == '4':
            action = input('a=add, r=remove, u=undo, l=list: ').strip().lower()
            if action in ('a', 'r'):
                listingID = readInt('Listing ID: ')
                if listingID not in byID:
                    print('Listing not found.')
                    continue
                changed = favorites.insertNode(listingID) if action == 'a' else favorites.deleteNode(listingID)
                if changed:
                    undo.push((action, listingID))
            elif action == 'u':
                last = undo.pop()
                if last:
                    actionDone, listingID = last
                    if actionDone == 'a':
                        favorites.deleteNode(listingID)
                    else:
                        favorites.insertNode(listingID)
            show([byID[i] for i in favorites.traverse()])
        elif choice == '5':
            action = input('a=add, n=next visit, l=list: ').strip().lower()
            if action == 'a':
                listingID = readInt('Listing ID: ')
                if listingID in byID and listingID not in visits:
                    visits.append(listingID)
            elif action == 'n' and visits:
                print('Completed visit:', visits.popleft())
            show([byID[i] for i in visits])
        elif choice == '6':
            budget = readInt('Investment budget (AZN): ')
            if budget is None or budget <= 0:
                continue
            candidates = [h for h in houses if 0 < h['price'] <= budget and h['estimated_gap'] > 0
                          and h['discount_pct'] is not None and h['discount_pct'] <= 50
                          and h['peer_count'] >= 20 and h['area_m2'] > 10]
            # Limit candidates for DP
            ratio = sorted(candidates, key=lambda h: h['estimated_gap'] / h['price'], reverse=True)[:7]
            value = sorted(candidates, key=lambda h: h['estimated_gap'], reverse=True)[:7]
            cheap = sorted(candidates, key=lambda h: h['price'])[:4]
            pool = list({h['listing_id']: h for h in ratio + value + cheap}.values())[:17]
            greedy = greedyInvestment(pool, budget)
            optimal, states, score = portfolioDP(pool, budget)
            for name, selection in [('Greedy', greedy), ('Dynamic Programming', optimal)]:
                print(f'\n{name}:')
                show(selection, limit=17)
                print(f"Spent: {sum(h['price'] for h in selection):,.0f} AZN | "
                      f"Optimization score: {sum(h['estimated_gap'] for h in selection):,.0f} AZN")
            print(f'\nDP memoized states: {states} | Candidate pool: {len(pool)}')
            print('Score = estimated difference from comparable listing medians, NOT guaranteed profit.')
        else:
            print('Invalid menu option.')

if __name__ == '__main__':
    main()