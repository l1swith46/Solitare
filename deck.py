class Card: #defining a card
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"
class Deck: #defining a deck of cards
    def __init__(self):
        self.cards = []
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    def shuffle(self): #shuffling the deck
        import random
        random.shuffle(self.cards)

    def deal_card(self): #dealing a card from the deck
        return self.cards.pop() if self.cards else None

    def __str__(self): #string representation of the deck
        return f"Deck of {len(self.cards)} cards"