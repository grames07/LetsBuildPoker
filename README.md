# LetsBuildPoker

Kevin and Grady plan to build a networked poker game that allows a player to play poker with other players.
__________________________________________________________________________________________________________________________________________________________

FP Status:
For this update, we have completed the functions that we indend to call for our project

We wrote the following functions: create_deck, get_card_value, get_card_suit, evaluate_five_card_hand entirely solo, then used the Claude 4.6 model available through Harvard's Sandbox AI to refine the syntax (e.g. line 17 used to be across several lines, and has been condensed to one)

We were having trouble with the best_hand_rank function, because it requires us to iterate through all the combinations in the 7 available cards. We coded this piece with the help of Claude again.

The other troubling codeblock was the comparing two hands. If the hand ranks are different, this is quite simple. However, if the hand ranks are the same and we need to compare which is bettr it gets more difficult.

