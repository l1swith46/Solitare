import deck

def get_card_value(card):
    """Get numerical value of a card for comparison"""
    values = {'Ace': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'Jack': 11, 'Queen': 12, 'King': 13}
    return values[card.rank]

def get_card_color(card):
    """Get color of a card (red/black)"""
    return 'red' if card.suit in ['Hearts', 'Diamonds'] else 'black'

def can_place_on_tableau(card, target_pile):
    """Check if a card can be placed on a tableau pile"""
    if not target_pile:
        return card.rank == 'King'  # Only Kings can start empty piles
    
    top_card, _ = target_pile[-1]
    return (get_card_color(card) != get_card_color(top_card) and 
            get_card_value(card) == get_card_value(top_card) - 1)

def can_place_on_foundation(card, foundation):
    """Check if a card can be placed on a foundation pile"""
    if not foundation:
        return card.rank == 'Ace'
    
    top_card = foundation[-1]
    return (card.suit == top_card.suit and 
            get_card_value(card) == get_card_value(top_card) + 1)

def draw_from_stock(stock, waste):
    """Draw a card from stock to waste"""
    if stock:
        card = stock.pop()
        waste.append(card)
    elif waste:
        # Recycle waste back to stock
        stock.extend(reversed(waste))
        waste.clear()

def move_to_foundation(pile, foundations, suit_index):
    """Try to move top card of pile to foundation"""
    if pile and pile[-1][1]:  # Card must be face up
        card, _ = pile[-1]
        if can_place_on_foundation(card, foundations[suit_index]):
            foundations[suit_index].append(pile.pop()[0])
            # Reveal next card if pile not empty
            if pile and not pile[-1][1]:
                pile[-1] = (pile[-1][0], True)
            return True
    return False

def display_game(tableau, foundations, stock, waste, cursor_pos=None, cursor_card_idx=None):
    """Display the current game state"""
    print("\n" + "="*60)
    
    # Display foundations
    suit_names = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    print("Foundations:")
    for i, foundation in enumerate(foundations):
        cursor = " <--" if cursor_pos == f"f{i}" else ""
        if foundation:
            print(f"  {suit_names[i]}: {foundation[-1]}{cursor}")
        else:
            print(f"  {suit_names[i]}: [Empty]{cursor}")
    
    # Display waste and stock
    print("\nWaste/Stock:")
    waste_cursor = " <--" if cursor_pos == "waste" else ""
    stock_cursor = " <--" if cursor_pos == "stock" else ""
    waste_display = waste[-1] if waste else "[Empty]"
    print(f"  Waste: {waste_display}{waste_cursor}")
    print(f"  Stock: [{len(stock)} cards]{stock_cursor}")
    
    # Display tableau
    print("\nTableau:")
    for i, pile in enumerate(tableau):
        print(f"  Column {i+1}: ", end="")
        if not pile:
            cursor = " <--" if cursor_pos == f"c{i}" and cursor_card_idx == 0 else ""
            print(f"[Empty]{cursor}")
            continue
        
        for j, (card, face_up) in enumerate(pile):
            cursor = " <--" if cursor_pos == f"c{i}" and cursor_card_idx == j else ""
            if face_up:
                print(f"[{card}]{cursor} ", end="")
            else:
                print(f"[X]{cursor} ", end="")
        print()

def get_cursor_input(cursor_pos):
    """Get user input for cursor movement and actions"""
    print("\nControls:")
    print("  q - Draw from stock")
    print("  a - Move cursor up")
    print("  d - Move cursor down") 
    print("  w - Move cursor left")
    print("  s - Move cursor right")
    print("  e - Move selected card to waste position")
    print("  t - Move selected card to foundation")
    print("  m - Move selected card to another tableau column")
    print("  r - Move card from waste to tableau")
    print("  p - Quit")
    print(f"Current cursor: {cursor_pos}")
    return input("Enter command: ").strip().lower()

def move_cursor(cursor_pos, cursor_card_idx, direction, tableau):
    """Move cursor in specified direction"""
    positions = ["stock", "waste", "f0", "f1", "f2", "f3", "c0", "c1", "c2", "c3", "c4", "c5", "c6"]
    
    if cursor_pos not in positions:
        return "c0", 0  # Default to first column, first card   
    current_idx = positions.index(cursor_pos)
    
    if direction in ["left", "right"]:
        # Move between positions
        if direction == "right":
            new_idx = (current_idx + 1) % len(positions)
        else:
            new_idx = (current_idx - 1) % len(positions)
        
        new_pos = positions[new_idx]
        
        # Set card index based on new position
        if new_pos.startswith("c"):
            col_idx = int(new_pos[1:])
            pile = tableau[col_idx]
            # Start at the top face-up card, or 0 if empty
            if pile:
                for i, (_, face_up) in enumerate(pile):
                    if face_up:
                        return new_pos, i
                return new_pos, len(pile) - 1  # All face down, select last card
            else:
                return new_pos, 0  # Empty column
        else:
            return new_pos, 0  # Other positions don't have multiple cards
    
    elif direction in ["up", "down"]:
        # Move within current position
        if cursor_pos.startswith("c"):
            col_idx = int(cursor_pos[1:])
            pile = tableau[col_idx]
            
            if not pile:
                return cursor_pos, 0
            
            if direction == "up":
                new_card_idx = max(0, cursor_card_idx - 1)
            else:  # down
                new_card_idx = min(len(pile) - 1, cursor_card_idx + 1)
            
            return cursor_pos, new_card_idx
        else:
            # For other positions, up/down does nothing
            return cursor_pos, cursor_card_idx
    
    return cursor_pos, cursor_card_idx

def main():
    # Initialize game
    deck_obj = deck.Deck()
    deck_obj.shuffle()
    
    # Deal tableau
    tableau = []
    for i in range(7):
        pile = []
        for j in range(i + 1):
            card = deck_obj.deal_card()
            face_up = (j == i)
            pile.append((card, face_up))
        tableau.append(pile)
    
    # Initialize other piles
    stock = deck_obj.cards[:]
    waste = []
    foundations = [[] for _ in range(4)]  # One for each suit
    
    cursor_pos = "c0"  # Start cursor on first column
    cursor_card_idx = 0  # Start at first card
    
    # Game loop
    while True:
        display_game(tableau, foundations, stock, waste, cursor_pos, cursor_card_idx)
        
        # Check win condition
        if all(len(f) == 13 for f in foundations):
            print("\nCongratulations! You won!")
            break
        
        command = get_cursor_input(cursor_pos)
        
        if command == 'p':
            break
        elif command == 'q':
            draw_from_stock(stock, waste)
        elif command in ['a', 'd', 'w', 's']:
            cursor_pos, cursor_card_idx = move_cursor(cursor_pos, cursor_card_idx, {'a': 'left', 'd': 'right', 'w': 'up', 's': 'down'}[command], tableau)
        elif command == 'e':
            # Move from current position to waste
            if cursor_pos.startswith('c'):
                col_idx = int(cursor_pos[1:])
                pile = tableau[col_idx]
                if cursor_card_idx < len(pile):
                    card, face_up = pile[cursor_card_idx]
                    if face_up:  # Can only move face-up cards
                        # Move the selected card and all cards above it
                        moving_cards = pile[cursor_card_idx:]
                        waste.extend([card for card, _ in moving_cards])
                        del pile[cursor_card_idx:]
                        
                        # Reveal next card if pile not empty
                        if pile and not pile[-1][1]:
                            pile[-1] = (pile[-1][0], True)
                        
                        # Adjust cursor if needed
                        if cursor_card_idx >= len(pile) and pile:
                            cursor_card_idx = len(pile) - 1
                        elif not pile:
                            cursor_card_idx = 0
        elif command == 't':
            # Move from current position to appropriate foundation
            if cursor_pos.startswith('c'):
                col_idx = int(cursor_pos[1:])
                pile = tableau[col_idx]
                if cursor_card_idx < len(pile):
                    card, face_up = pile[cursor_card_idx]
                    if face_up and cursor_card_idx == len(pile) - 1:  # Can only move top card
                        suit_names = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
                        suit_idx = suit_names.index(card.suit)
                        if move_to_foundation(pile, foundations, suit_idx):
                            # Adjust cursor
                            if pile and cursor_card_idx >= len(pile):
                                cursor_card_idx = max(0, len(pile) - 1)
                            continue
            elif cursor_pos == 'waste' and waste:
                card = waste[-1]
                suit_names = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
                suit_idx = suit_names.index(card.suit)
                if can_place_on_foundation(card, foundations[suit_idx]):
                    foundations[suit_idx].append(waste.pop())
                    continue
            print("Cannot move to foundation")
        elif command == 'r':
            # Move card from waste to tableau
            if cursor_pos == 'waste' and waste:
                card = waste[-1]
                try:
                    dest_col = int(input("Move to which column (1-7)? ").strip()) - 1
                    if 0 <= dest_col < 7:
                        to_pile = tableau[dest_col]
                        
                        if can_place_on_tableau(card, to_pile):
                            to_pile.append((card, True))
                            waste.pop()
                            print(f"Moved {card} to column {dest_col + 1}")
                        else:
                            print("Invalid move - cards must be placed on opposite color and one rank lower, or King on empty column")
                    else:
                        print("Invalid column number")
                except ValueError:
                    print("Please enter a valid column number (1-7)")
            else:
                print("No card in waste to move")
        elif command == 'm':
            # Move selected card/sequence to another tableau column
            if cursor_pos.startswith('c'):
                from_col = int(cursor_pos[1:])
                from_pile = tableau[from_col]
                
                if cursor_card_idx < len(from_pile):
                    # Find all face-up cards from cursor position
                    face_up_cards = []
                    for i in range(cursor_card_idx, len(from_pile)):
                        if from_pile[i][1]:  # face up
                            face_up_cards.append(from_pile[i])
                        else:
                            break
                    
                    if face_up_cards:
                        # Ask for destination column
                        try:
                            dest_col = int(input("Move to which column (1-7)? ").strip()) - 1
                            if 0 <= dest_col < 7 and dest_col != from_col:
                                to_pile = tableau[dest_col]
                                
                                # Check if the move is valid
                                if can_place_on_tableau(face_up_cards[0][0], to_pile):
                                    # Move the cards
                                    moving_cards = from_pile[cursor_card_idx:]
                                    to_pile.extend(moving_cards)
                                    del from_pile[cursor_card_idx:]
                                    
                                    # Reveal next card if pile not empty
                                    if from_pile and not from_pile[-1][1]:
                                        from_pile[-1] = (from_pile[-1][0], True)
                                    
                                    # Adjust cursor
                                    cursor_pos = f"c{dest_col}"
                                    cursor_card_idx = len(to_pile) - len(moving_cards)
                                else:
                                    print("Invalid move - cards must be placed on opposite color and one rank lower")
                            else:
                                print("Invalid column number")
                        except ValueError:
                            print("Please enter a valid column number (1-7)")
                    else:
                        print("No face-up cards to move")
                else:
                    print("No card selected")
            else:
                print("Can only move from tableau columns")

if __name__ == "__main__":
    main()