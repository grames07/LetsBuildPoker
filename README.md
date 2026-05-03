# LetsBuildPoker

Kevin and Grady plan to build a networked poker game that allows a player to play poker with other players.
__________________________________________________________________________________________________________________________________________________________

FP Status:

For this update, we have completed the functions that we indend to call for our project

We wrote the following functions: create_deck, get_card_value, get_card_suit, evaluate_five_card_hand entirely solo, then used the Claude 4.6 model available through Harvard's Sandbox AI to refine the syntax (e.g. line 17 used to be across several lines, and has been condensed to one)

We were having trouble with the best_hand_rank function, because it requires us to iterate through all the combinations in the 7 available cards. We coded this piece with the help of Claude again.

The other troubling codeblock was the comparing two hands. If the hand ranks are different, this is quite simple. However, if the hand ranks are the same and we need to compare which is better it gets more difficult. To compare these, we wrote preliminary code for the easier cases (ranks 0, 4, 5, 8, 9), then had Claude use the same methodology for completing the other comparisons.

The functions in the betting parts of this are relatively straightforward to understand, and don't contain any additional functionalities that we weren't taught in class.

__________________________________________________________________________________________________________________________________________________________

FP Submission:

For this update, we've instituted the previous functions from the poker_lib.py file in order to run a complete game of poker. The biggest tasks since our FP Status submission are the functions that we defined to allow for playing of a networked the game. The most importnant of these functions is the "run_betting_round" function, which allows us to use the player_action function from poker_lib to loop the betting actions.

One of the key changes since FP Status includes eliminating redundancies. We used the Claude 4.6 model via Harvard's Sandbox AI in order to help us with this, and we were able to include both the "post_blinds" and "award_pot" functions within the functionality of poker_server.py, eliminating the need for those functions in the library. We also moved the "game values" over to the poker_server, because that was easier for us.

To highlight the very important piece of this code: the "mirror" function allows us to send different messages to each player (with opposite "You" and "Opponent" messages). This was suggested by Claude, since my initial plan was to hard code this for each message that needed to be sent. This is an example of AI being a helpful tool for making code simpler!


